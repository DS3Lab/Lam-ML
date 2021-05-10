
import urllib
import numpy as np

from storage.memcached.memcached_type import MemcachedStorage


def async_reduce(storage, vector, bucket_name, vector_name):
    assert isinstance(storage, MemcachedStorage)

    # vector is supposed to be a 1-d numpy array
    vec_shape = vector.shape
    vec_dtype = vector.dtype

    data = storage.load_or_wait(vector_name, bucket_name, 0.1).read()
    new_vec = np.frombuffer(data, dtype=vec_dtype).reshape(vec_shape)
    storage.save_v2(vector.tobytes(), vector_name, bucket_name)

    return new_vec


def reduce_batch(storage, vector, tmp_bucket, merged_bucket, num_workers, worker_index, postfix):
    assert isinstance(storage, MemcachedStorage)

    # vector is supposed to be a 1-d numpy array
    vec_shape = vector.shape
    vec_dtype = vector.dtype
    merged_vec = np.zeros(vec_shape, dtype=vec_dtype)

    postfix_splits = postfix.split("_")
    curr_epoch = int(postfix_splits[0])
    curr_batch = int(postfix_splits[1])

    # put object to memcached, format of key: bucket_workerID_epoch_batch
    key = "{}_{}".format(worker_index, postfix)
    storage.save_v2(vector.tobytes(), key, tmp_bucket)

    # the first worker read and aggregate the corresponding chunk
    if worker_index == 0:
        num_files = 0
        candidate = [tmp_bucker+"_"+w+postfix for w in range(num_workers)]
        while num_files < num_workers:
            objects = storage.list(candidate)
            if objects is not None:
                delete_list = []
                for file_key, value in objects.items():
                    #candidate.remove(file_key)
                    key_splits = file_key.split("_")
                    key_epoch = key_splits[2] 
                    key_batch = key_splits[3] 
                    if key_epoch == str(curr_epoch) and key_batch == str(curr_batch):
                        data = value
                        bytes_data = np.frombuffer(data, dtype=vec_dtype).reshape(vec_shape)
                        pickle_data = pickle.loads(data_bytes)
                        for i in range(len(pickle_data)):
                            if n_files == 0:
                                merged_value.append(np.zeros(pickle_data[i].shape, dtype=pickle_data[i].dtype))
                            merged_value[i] = merged_value[i] + pickle_data[i]
                        num_files += 1
                    delete_list.append(file_key)
                storage.delete(delete_list)
        # write the merged data back to s3
        merged_file_name = 'merged_' + postfix
        storage.save_v2(merged_vec.tobytes(), merged_file_name, merged_bucket)
        delete_expired_batch(storage, merged_bucket, curr_epoch, curr_batch)
    else:
        merged_file_name = 'merged_' + postfix
        merged_data = storage.load_or_wait_v2(merged_file_name, merged_bucket, 0.1).read()
        merged_vec = merged_data

    return merged_vec


def reduce_epoch(storage, vector, tmp_bucket, merged_bucket, num_workers, worker_index, postfix):
    assert isinstance(storage, MemcachedStorage)

    # vector is supposed to be a 1-d numpy array
    vec_shape = vector.shape
    vec_dtype = vector.dtype
    merged_vec = np.zeros(vec_shape, dtype=vec_dtype)

    curr_epoch = int(postfix)

    # put object to memcache, format of key: bucket_workerID_epoch
    key = "{}_{}".format(worker_index, postfix)
    storage.save_v2(vector.tobytes(), key, tmp_bucket)

    # the first worker read and aggregate the corresponding chunk
    if worker_index == 0:
        num_files = 0
        candidate = [tmp_bucket+str(i)+postfix for i in range(num_workers)]
        while num_files < num_workers:
            objects = storage.list(candidate)
            if objects is not None:
                delete_list = []
                for file_key, data_bytes in objects.items():
                    #candidate.remove(file_key)
                    key_splits = file_key.split("_")
                    key_epoch = key_splits[2]
                    if key_epoch == str(curr_epoch):
                        data = pickle.loads(data_bytes)
                        for i in range(len(data)):
                            if n_files == 0:
                                merged_value.append(np.zeros(data[i].shape, dtype=data[i].dtype))
                            merged_value[i] = merged_value[i] + data[i]
                        num_files += 1
                        delete_list.append(file_key)
                storage.delete(delete_list)
        # write the merged data back to s3
        storage.save_v2(merged_vec.tobytes(), 'merged_' + postfix, merged_bucket)
        delete_expired_epoch(storage, merged_bucket, curr_epoch)
    else:
        merged_file_name = 'merged_' + postfix
        merged_data = storage.load_or_wait_v2(merged_file_name, merged_bucket, 0.1).read()
        merged_vec = np.frombuffer(merged_data, dtype=vec_dtype).reshape(vec_shape)

    return merged_vec


# delete the merged values of the *current or older* steps
def delete_expired_batch(storage, bucket_name, cur_epoch, cur_batch):
    assert isinstance(storage, MemcachedStorage)
    candidate = []
    for epoch in range(cur_epoch+1):
        for batch in range(cur_batch+1):
            candidatte.append("{}_{}_{}".format(bucket_name, epoch, batch))
    storage.delete(candidate)
    return True


def delete_expired_epoch(storage, bucket_name, cur_epoch):
    assert isinstance(storage, MemcachedStorage)
    candidate = []
    for epoch in range(cur_epoch+1):
        candidatte.append("{}_{}".format(bucket_name, epoch))
    storage.delete(candidate)
    return True


def reduce_scatter_batch(storage, vector, tmp_bucket, merged_bucket, num_workers, my_rank, postfix):
    assert isinstance(storage, MemcachedStorage)

    # vector is supposed to be a 1-d numpy array
    num_all_values = vector.size
    num_values_per_worker = num_all_values // num_workers
    residue = num_all_values % num_workers

    postfix_splits = postfix.split("_")
    curr_epoch = postfix_splits[0]
    curr_batch = postfix_splits[1]

    my_offset = (num_values_per_worker * my_rank) + min(residue, my_rank)
    my_length = num_values_per_worker + (1 if my_rank < residue else 0)
    my_chunk = vector[my_offset: my_offset + my_length]

    # write partitioned vector to the shared storage, except the chunk charged by myself
    for i in range(num_workers):
        if i != my_rank:
            offset = (num_values_per_worker * i) + min(residue, i)
            length = num_values_per_worker + (1 if i < residue else 0)
            # indicating the chunk number and which worker it comes from
            key = "{}_{}".format(i, my_rank)

            # format of key: tmp-bucket_chunkID_workerID_epoch_batch
            storage.save_v2(vector[offset: offset + length].tobytes(), key + '_' + postfix, tmp_bucket)

    candidate = []
    for worker_index in range(num_workers):
        if worker_index ! = myrank:
            candidate.append("{}_{}_{}_{}".format(merged_bucket, myrank, worker_index, postfix))
    # read and aggregate the corresponding chunk
    num_files = 0
    
    while num_files < num_workers - 1:
        objects = storage.list(candidate)
        if objects is not None:
            delete_list = [] 
            for file_key, data in objects.items():
                key_splits = file_key.split("_")

                # if it's the chunk I care and it is from the current step
                # format of key: tmp-bucket_chunkID_workerID_epoch_batch
                if key_splits[1] == str(my_rank) and key_splits[3] == curr_epoch and key_splits[4] == curr_batch:
                    bytes_data = np.frombuffer(data, dtype=vector.dtype)
                    my_chunk = my_chunk + bytes_data
                    num_files += 1
                    delete_list.append(file_key)
            storage.delete(delete_list)

    # write the aggregated chunk back
    # key format in merged_bucket: chunkID_epoch_batch
    storage.save_v2(my_chunk.tobytes(), str(my_rank) + '_' + postfix, merged_bucket)

    # read other aggregated chunks
    merged_value = dict()
    merged_value[my_rank] = my_chunk

    candidate = []
    for worker_index in range(num_workers):
        if worker_index != myrank:
            candidate.append("{}_{}_{}".format(merged_bucket, worker_index, postfix))

    num_merged_files = 0
    already_read_files = []

    while num_merged_files < num_workers - 1:
        objects = storage.list(candidate)
        if objects is not None:
            for file_key, data in objects:
                key_splits = file_key.split("_")
                # key format: merged-bucket_chunkID_epoch_batch
                if key_splits[1] != str(my_rank) and key_splits[2] == curr_epoch and \
                        key_splits[3] == curr_batch and file_key not in already_read_files:
                    bytes_data = np.frombuffer(data, dtype=vector.dtype)
                    merged_value[int(key_splits[1])] = bytes_data
                    already_read_files.append(file_key)
                    num_merged_files += 1

    # reconstruct the whole vector
    result = merged_value[0]
    for k in range(1, num_workers):
        result = np.concatenate((result, merged_value[k]))

    return result



def reduce_scatter_epoch(storage, vector, tmp_bucket, merged_bucket, num_workers, my_rank, postfix):
    assert isinstance(storage, MemcachedStorage)

    # vector is supposed to be a 1-d numpy array
    num_all_values = vector.size
    num_values_per_worker = num_all_values // num_workers
    residue = num_all_values % num_workers

    cur_epoch = int(postfix)

    my_offset = (num_values_per_worker * my_rank) + min(residue, my_rank)
    my_length = num_values_per_worker + (1 if my_rank < residue else 0)
    my_chunk = vector[my_offset: my_offset + my_length]

    # write partitioned vector to the shared memory, except the chunk charged by myself
    for i in range(num_workers):
        if i != my_rank:
            offset = (num_values_per_worker * i) + min(residue, i)
            length = num_values_per_worker + (1 if i < residue else 0)
            # indicating the chunk number and which worker it comes from
            key = "{}_{}".format(i, my_rank)
            # format of key in tmp-bucket: chunkID_workerID_epoch
            storage.save_v2(vector[offset: offset + length].tobytes(), key + '_' + postfix, tmp_bucket)

    # read and aggregate the corresponding chunk
    num_files = 0

    candidate = []
    for worker_index in range(num_workers):
        if worker_index != my_rank:
            candidate.append("{}_{}_{}".format(tmp_bucker, my_rank, worker_index))

            
    while num_files < num_workers - 1:
        objects = storage.list(candidate)
        if objects is not None:
            delete_list = []   
            for file_key, value in objects.items():
                key_splits = file_key.split("_")
                # if it's the chunk I care and it is from the current step
                # format of key in tmp-bucket: chunkID_workerID_epoch_batch
                if key_splits[1] == str(my_rank) and key_splits[3] == str(cur_epoch):
                    bytes_data = np.frombuffer(data, dtype=vector.dtype)
                    my_chunk = my_chunk + bytes_data
                    num_files += 1
                    delete_list.append(file_key)
            storage.delete(delete_list)

    # write the aggregated chunk back
    # key format in merged_bucket: chunkID_epoch_batch
    storage.save_v2(my_chunk.tobytes(), str(my_rank) + '_' + postfix, merged_bucket)

    # read other aggregated chunks
    merged_value = dict()
    merged_value[my_rank] = my_chunk

    num_merged_files = 0
    already_read_files = []

    candidate = []
    for workers_index in range(num_workers):
        if worker_index != my_rank:
            candidate.append("{}_{}_{}".format(merged_bucker, worker_index, postfix))

    while num_merged_files < num_workers - 1:
        objects = storage.list(candidate)
        if objects is not None:
            for file_key, value in objects:
                key_splits = file_key.split("_")
                candidate.remove(file_key)
                # key format in merged_bucket: chunkID_epoch
                # if not file_key.startswith(str(my_rank)) and file_key not in already_read:
                if key_splits[1] != str(my_rank) and key_splits[2] == str(cur_epoch) \
                        and file_key not in already_read_files:

                    bytes_data = np.frombuffer(data, dtype=vector.dtype)

                    merged_value[int(key_splits[1])] = bytes_data

                    already_read_files.append(file_key)
                    num_merged_files += 1

    # reconstruct the whole vector
    result = merged_value[0]
    for k in range(1, num_workers):
        result = np.concatenate((result, merged_value[k]))

    return result


