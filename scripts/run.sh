#!/bin/bash
MODEL=$1
DATASET=$2

window_name="${MODEL}_${DATASET}"
tmux new-session -d -s $window_name
index=1
method_list=("zero_shot_cot" "zero_shot_plan_and_solve" "few_shot_cot" "few_shot_pot" "few_shot_eot" "few_shot_declarative" "auto_analogical" "auto_zero_shot_cot" "auto_formalize_and_solve")

for var in "${method_list[@]}"; do
    # Create a new window named "python_window_$i" in the "python_session" session
    tmux new-window -t $window_name:$index
    tmux send-keys -t $window_name:$index "conda activate mwps" Enter
    # Send the command to execute the Python file to the window
    tmux send-keys -t $window_name:$index "python src/main.py --method $var --exp_name final --model $MODEL --dataset $DATASET --limit_dataset_size 0 --log_dir ./log/" Enter
    ((index++))
done
