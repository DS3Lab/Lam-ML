import time
import urllib.parse
import logging
import numpy as np
import pickle

import torch
from torch.autograd import Variable
from torch.utils.data.sampler import SubsetRandomSampler

from elasticache.Redis.set_object import hset_object
from elasticache.Redis.counter import hcounter
from elasticache.Redis.get_object import hget_object
from elasticache.Redis.__init__ import redis_init
from s3.get_object import get_object
from s3.put_object import put_object
from sync.sync_grad_redis import *

from model.LogisticRegression import LogisticRegression
from data_loader.LibsvmDataset import DenseLibsvmDataset2

# lambda setting
grad_bucket = "tmp-grads"
model_bucket = "tmp-updates"
local_dir = "/tmp"
w_prefix = "w_"
b_prefix = "b_"
w_grad_prefix = "w_grad_"
b_grad_prefix = "b_grad_"

# algorithm setting
learning_rate = 0.1
batch_size = 100000
num_epochs = 55
validation_ratio = .2
shuffle_dataset = True
random_seed = 42


def handler(event, context):
    start_time = time.time()
    bucket = event['bucket']
    key = event['name']
    num_features = event['num_features']
    num_classes = event['num_classes']
    redis_location = event['elasticache']
    endpoint = redis_init(redis_location)
    print('bucket = {}'.format(bucket))
    print('key = {}'.format(key))
  
    key_splits = key.split("_")
    num_worker = event['num_files']
    worker_index = event['worker_index']

    batch_size = 100000
    batch_size = int(np.ceil(batch_size/num_worker))
    
    torch.manual_seed(random_seed)
    
    # read file(dataset) from s3
    file = get_object(bucket, key).read().decode('utf-8').split("\n")
    print("read data cost {} s".format(time.time() - start_time))
    parse_start = time.time()
    dataset = DenseLibsvmDataset2(file, num_features)
    preprocess_start = time.time()
    print("libsvm operation cost {}s".format(parse_start - preprocess_start))
   
    # Creating data indices for training and validation splits:
    dataset_size = len(dataset)
    print("dataset size = {}".format(dataset_size))
    indices = list(range(dataset_size))
    split = int(np.floor(validation_ratio * dataset_size))
    if shuffle_dataset:
        np.random.seed(random_seed)
        np.random.shuffle(indices)
    train_indices, val_indices = indices[split:], indices[:split]

    # Creating PT data samplers and loaders:
    train_sampler = SubsetRandomSampler(train_indices)
    valid_sampler = SubsetRandomSampler(val_indices)

    train_loader = torch.utils.data.DataLoader(dataset,
                                               batch_size=batch_size,
                                               sampler=train_sampler)
    validation_loader = torch.utils.data.DataLoader(dataset,
                                                    batch_size=batch_size,
                                                    sampler=valid_sampler)
    
    print("preprocess data cost {} s".format(time.time() - preprocess_start))

    model = LogisticRegression(num_features, num_classes)

    # Loss and Optimizer
    # Softmax is internally computed.
    # Set parameters to be updated.
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
    
    train_loss = []
    test_loss = []
    test_acc = []
    epoch_time = 0
    epoch_start = time.time()
    # Training the Model
    for epoch in range(num_epochs):
        tmp_train = 0
        for batch_index, (items, labels) in enumerate(train_loader):
            print("------worker {} epoch {} batch {}------".format(worker_index, epoch, batch_index))
            items = Variable(items.view(-1, num_features))
            labels = Variable(labels)
            # Forward + Backward + Optimize
            optimizer.zero_grad()
            outputs = model(items)
            loss = criterion(outputs, labels)
            loss.backward()

            w_grad = model.linear.weight.grad.data.numpy()
            b_grad = model.linear.bias.grad.data.numpy()
            
            #synchronization starts from that every worker writes their gradients of this batch and epoch
            sync_start = time.time()
            hset_object(endpoint, grad_bucket, w_grad_prefix + str(worker_index), w_grad.tobytes())
            hset_object(endpoint, grad_bucket, b_grad_prefix + str(worker_index), b_grad.tobytes())
            tmp_write_local_epoch_time = time.time()-sync_start
            print("write local gradient cost = {}".format(tmp_write_local_epoch_time))
            
            #merge gradients among files
            file_postfix = "{}_{}".format(epoch, batch_index)
            if worker_index == 0:
                
                w_grad_merge, b_grad_merge = \
                    merge_w_b_grads(endpoint, 
                                    grad_bucket, num_worker, w_grad.dtype,
                                    w_grad.shape, b_grad.shape,
                                    w_grad_prefix, b_grad_prefix)
                put_merged_w_b_grads(endpoint,model_bucket, 
                                    w_grad_merge, b_grad_merge, file_postfix,
                                    w_grad_prefix, b_grad_prefix)
                hset_object(endpoint, model_bucket, "epoch", epoch)
                hset_object(endpoint, model_bucket, "index", batch_index)
            else:
                w_grad_merge, b_grad_merge = get_merged_w_b_grads(endpoint,model_bucket, file_postfix,
                                                                    w_grad.dtype, w_grad.shape, b_grad.shape,
                                                                    w_grad_prefix, b_grad_prefix)
               
            model.linear.weight.grad = Variable(torch.from_numpy(w_grad_merge))
            model.linear.bias.grad = Variable(torch.from_numpy(b_grad_merge))
            tmp_sync_time = time.time() - sync_start
            print("synchronization cost {} s".format(tmp_sync_time))

            optimizer.step()
            
            tmp_train=tmp_train+loss.item()
            train_loss.append(tmp_train/(batch_index+1))
            
        epoch_time += time.time()-epoch_start
        # Test the Model
        correct = 0
        total = 0
        tmp_test = 0
        count = 0
        for items, labels in validation_loader:
            items = Variable(items.view(-1, num_features))
            outputs = model(items)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum()
            loss = criterion(outputs, labels)
            tmp_test = tmp_test + loss.item()
            count += 1
        print('Accuracy of the model on the %d test samples: %d %%' % (len(val_indices), 100 * correct / total))
        test_loss.append(tmp_test/count)
        test_acc.append(100 * correct / total)
        epoch_start = time.time()

    loss_record = [test_loss, test_acc, train_loss, epoch_time]
    put_object("grad-average-loss", "grad-loss{}".format(worker_index), bytes(loss_record))
