#!/bin/bash

world_size=$1
lr=$2
batch_size=$3

train_path="/home/ubuntu/dataset/rcv"
source /home/ubuntu/envs/pytorch/bin/activate

if [ $world_size == 1 ]
then
  source /home/ubuntu/envs/pytorch/bin/activate
  nohup python3.6 /home/ubuntu/LambdaML/ec2/lr/rcv_lr.py --rank 0 --batch-size $batch_size -l $lr --world-size $world_size --train-file /home/ubuntu/dataset/rcv --no-cuda > "/home/ubuntu/log/lr_single_b${batch_size}_lr${lr}.txt" 2>&1 &
else
  for ((i=0; i<$world_size; i++)); do
  python3.6 /home/ubuntu/LambdaML/ec2/lr/rcv_lr.py --epochs 5 --rank $i --batch-size $batch_size -l $lr --world-size $world_size --train-file "${train_path}${world_size}/${i}_${world_size}" --no-cuda > "/home/ubuntu/log/lr_local_${i}_${world_size}_${batch_size}_${lr}.txt" 2>&1 &
done
fi

