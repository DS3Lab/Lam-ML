import numpy as np
import time
import pickle
import torch
from torch.autograd import Variable
import torch.nn.functional as F

from s3.list_objects import list_bucket_objects
from s3.get_object import get_object
from s3.put_object import put_object

from sync.sync_neural_network import *
from sync.sync_meta import SyncMeta


merged_bucket = "merged-value"
tmp_bucket = "tmp-value"

weights_prefix = 'w_'
gradients_prefix = 'g_'


class Accuracy(object):

    def __init__(self):
        self.correct = 0
        self.count = 0

    def __str__(self):
        return '{:.2f}%'.format(self.accuracy * 100)

    @property
    def accuracy(self):
        return self.correct / self.count

    def update(self, output, target):
        with torch.no_grad():
            pred = output.argmax(dim=1)
            correct = pred.eq(target).sum().item()

        self.correct += correct
        self.count += output.size(0)
        
class Average(object):

    def __init__(self):
        self.sum = 0
        self.count = 0

    def __str__(self):
        return '{:.6f}'.format(self.average)

    @property
    def average(self):
        return self.sum / self.count

    def update(self, value, number):
        self.sum += value * number
        self.count += number


# Training
def train(epoch, net, trainloader, optimizer, device, worker_index, num_worker, sync_mode, sync_step):
    
    net.train()
    
    epoch_start = time.time()
    
    epoch_sync_time = 0
    num_batch = 0
    
    train_acc = Accuracy()
    train_loss = Average()

    for batch_idx, (inputs, targets) in enumerate(trainloader):

        # print("------worker {} epoch {} batch {}------".format(worker_index, epoch+1, batch_idx+1))
        batch_start = time.time()

        inputs, targets = inputs.to(device), targets.to(device)
        outputs = net(inputs)
        loss = F.cross_entropy(outputs, targets)
        
        optimizer.zero_grad()
        loss.backward()
        # print("forward and backward cost {} s".format(time.time()-batch_start))

        if sync_mode == 'model_avg':

            # apply local gradient to local model
            optimizer.step()
            # average model
            if (batch_idx+1) % sync_step == 0:
                
                sync_start = time.time()
                
                #################################reduce_broadcast####################################
                print("starting model average")
                weights = [param.data.numpy() for param in net.parameters()]
                # print("[Worker {}] Gradients before sync = {}".format(worker_index, gradients[0][0]))
                
                # put_object_start = time.time()
                
                put_object(tmp_bucket, gradients_prefix + str(worker_index), pickle.dumps(weights))
                
                # print("write local gradients cost {} s".format(time.time() - put_object_start))
                
                file_postfix = "{}_{}".format(epoch, batch_idx)
                if worker_index == 0:
                    # merge all workers
                    
                    # merged_value_start = time.time()
                    
                    merged_value = \
                        merge_all_workers(tmp_bucket, num_worker, gradients_prefix)
                        
                    # print("merged_value cost {} s".format(time.time() - merged_value_start))
                    
                    # put_merged_start = time.time()
                    # upload merged value to S3
                    put_merged(merged_bucket, merged_value,
                                        gradients_prefix, file_postfix)
                                        
                    # print("put_merged cost {} s".format(time.time() - put_merged_start))                   
                    
                    # delete_expired(merged_bucket, epoch, batch_idx, gradients_prefix)
                    
                else:
                    
                    # read_merged_start = time.time()
                    # get merged value from S3
                    merged_value = get_merged(merged_bucket, gradients_prefix, file_postfix)
                    
                    # print("read_merged cost {} s".format(time.time() - read_merged_start))
                    
                # print("[Worker {}] Gradients after sync = {}".format(worker_index, merged_value[0][0]))
                
                for layer_index, param in enumerate(net.parameters()):
                    param.data = torch.from_numpy(merged_value[layer_index])
                    
                # gradients = [param.grad.data.numpy() for param in net.parameters()]
                # print("[Worker {}] Gradients after sync = {}".format(worker_index, gradients[0][0]))
                # print("synchronization cost {} s".format(time.time() - sync_start))
                
                if worker_index == 0:
                    delete_expired(merged_bucket, epoch, batch_idx, gradients_prefix)
                
                epoch_sync_time += time.time() - sync_start
                    
                
        if sync_mode == 'grad_avg':
            
            sync_start = time.time()
            
            #################################scatter_reduce####################################
            # get gradients and flatten it to a 1-D array
            # gradients = [param.grad.data.numpy() for param in net.parameters()]
            # print("[Worker {}] Gradients before sync = {}".format(worker_index, gradients[0][0]))
            
            # param_dic = {}
            # for index, param in enumerate(net.parameters()):
            #     param_dic[index] = [param.grad.data.numpy().size, param.grad.data.numpy().shape]
            #     if index == 0:
            #         flattened_param = param.grad.data.numpy().flatten()
            #     else:
            #         flattened_param = np.concatenate((flattened_param, param.grad.data.numpy().flatten()))
                    
            # comm_start = time.time()

            # # merge gradients
            # file_postfix = "{}_{}".format(epoch, batch_idx)
            # merged_value = scatter_reduce(flattened_param, tmp_bucket, merged_bucket, num_worker, worker_index, file_postfix)
            # merged_value /= float(num_worker)
            
            # # print("scatter_reduce cost {} s".format(time.time() - comm_start))

            # # update the model gradients by layers
            # offset = 0
            # for layer_index, param in enumerate(net.parameters()):

            #     layer_size = param_dic[layer_index][0]
            #     layer_shape = param_dic[layer_index][1]

            #     layer_value = merged_value[offset : offset + layer_size].reshape(layer_shape)
            #     param.grad.data = torch.from_numpy(layer_value)

            #     offset += layer_size
                
            # if worker_index == 0:
            #     delete_expired_merged(merged_bucket, epoch, batch_idx)
            #################################scatter_reduce####################################
            
            
            
            #################################reduce_broadcast####################################
            gradients = [param.grad.data.numpy() for param in net.parameters()]
            # print("[Worker {}] Gradients before sync = {}".format(worker_index, gradients[0][0]))
            
            # put_object_start = time.time()
            
            put_object(tmp_bucket, gradients_prefix + str(worker_index), pickle.dumps(gradients))
            
            # print("write local gradients cost {} s".format(time.time() - put_object_start))
            
            file_postfix = "{}_{}".format(epoch, batch_idx)
            if worker_index == 0:
                # merge all workers
                
                # merged_value_start = time.time()
                
                merged_value = \
                    merge_all_workers(tmp_bucket, num_worker, gradients_prefix)
                    
                # print("merged_value cost {} s".format(time.time() - merged_value_start))
                
                # put_merged_start = time.time()
                # upload merged value to S3
                put_merged(merged_bucket, merged_value,
                                    gradients_prefix, file_postfix)
                                    
                # print("put_merged cost {} s".format(time.time() - put_merged_start))                   
                
                # delete_expired(merged_bucket, epoch, batch_idx, gradients_prefix)
                
            else:
                
                # read_merged_start = time.time()
                # get merged value from S3
                merged_value = get_merged(merged_bucket, gradients_prefix, file_postfix)
                
                # print("read_merged cost {} s".format(time.time() - read_merged_start))
                
            # print("[Worker {}] Gradients after sync = {}".format(worker_index, merged_value[0][0]))
            
            for layer_index, param in enumerate(net.parameters()):
                param.grad.data = torch.from_numpy(merged_value[layer_index])
                
            # gradients = [param.grad.data.numpy() for param in net.parameters()]
            # print("[Worker {}] Gradients after sync = {}".format(worker_index, gradients[0][0]))
            # print("synchronization cost {} s".format(time.time() - sync_start))
            
            if worker_index == 0:
                delete_expired(merged_bucket, epoch, batch_idx, gradients_prefix)
                
            #################################reduce_broadcast####################################
            
            epoch_sync_time += time.time() - sync_start
            optimizer.step()
            
        if sync_mode == 'cen':
            optimizer.step()
        
        train_acc.update(outputs, targets)
        train_loss.update(loss.item(), inputs.size(0))
        
        if num_batch%10 == 0:
            print("Epoch {} Batch {} training Loss:{}, Acc:{}".format(epoch+1, num_batch, train_loss, train_acc))
        
        num_batch += 1
        
    epoch_time = time.time() - epoch_start
    print("Epoch {} has {} batches, time = {} s, sync time = {} s, cal time = {} s".format(epoch+1, num_batch, epoch_time, epoch_sync_time, epoch_time - epoch_sync_time))
    
    return train_loss, train_acc



def test(epoch, net, testloader, device):
    # global best_acc
    net.eval()
    test_loss = Average()
    test_acc = Accuracy()
    
    with torch.no_grad():
        for batch_idx, (inputs, targets) in enumerate(testloader):
            
            inputs, targets = inputs.to(device), targets.to(device)
            
            outputs = net(inputs)
            
            loss = F.cross_entropy(outputs, targets)
            
            test_loss.update(loss.item(), inputs.size(0))
            test_acc.update(outputs, targets)
            
    
    return test_loss, test_acc
