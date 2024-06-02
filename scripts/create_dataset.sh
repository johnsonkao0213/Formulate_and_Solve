#!/bin/bash
DATASET=$1

window_name="${DATASET}_create"
tmux new-session -d -s $window_name
index=0

tmux new-window -t $window_name:$index
tmux send-keys -t $window_name:$index "conda activate mwps" Enter
# Send the command to execute the Python file to the window
tmux send-keys -t $window_name:$index "python src/dataset_construction.py --dataset $DATASET --limit_dataset_size 0" Enter
