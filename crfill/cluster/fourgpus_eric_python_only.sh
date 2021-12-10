#!/bin/bash

DATE=$(date '+%Y%m%d%H%M')
EXPERIMENT_NAME="fourgpu_inpaint"

JOBS_SOURCE="$HOME/challenging-nodes/crfill"
SINGULARITYIMAGE="$HOME/crfill.sif"
DATA="/scratch/scratchdata"

#Beta for the first task
BETAL1_1=1.

#Lambda for the first task
LAMBDA_1=1.

NUM_WORKERS=5

LOGGING_DIR="$HOME/challenging-nodes/crfill/checkpoints"

NAME="$EXPERIMENT_NAME""$DATE""-beta_l$BETAL1_1-lambda_ref$LAMBDA_1"

STANDARD_PARAMS="--seed 0  --batchSize 92 --k_means_clusters 3 --include_chexpert --include_mimic --node21_resample_count 10 --dataset_mode_train custom_train --dataset_mode custom_train --train_image_dir /data --netG twostagend --netD deepfill --preprocess_mode none --validation_freq 20000 --niter 600 --display_freq 2000 --model arrange"

python -u train.py --name $NAME --num_workers $NUM_WORKERS --checkpoints_dir $LOGGING_DIR/$NAME --gpu_ids 0 --beta_l1 $BETAL1_1 --lambda_ref $LAMBDA_1 $STANDARD_PARAMS



echo "$NAME command ran"