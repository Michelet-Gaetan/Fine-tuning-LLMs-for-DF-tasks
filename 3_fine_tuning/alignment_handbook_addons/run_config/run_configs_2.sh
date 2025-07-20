#!/bin/bash

# Array of models
models=(
    "Llama-31-8B"
)

# Array of tasks
tasks=(
    "task-1"
    "task-2"
    "task-3"
)

# Array of samples
samples=(
    "60-samples"
    "120-samples"
    "180-samples"
)

configs=(
    "config-1"
    "config-2"
    "config-3"
    "config-4"  
)

# Loop through each path and run the command
for model in "${models[@]}"; do
    for task in "${tasks[@]}"; do
        for sample in "${samples[@]}"; do
            for config in "${configs[@]}"; do
                echo "ACCELERATE_LOG_LEVEL=info accelerate launch --config_file recipes/accelerate_configs/multi_gpu.yaml --num_processes=1 scripts/run_sft_classic.py recipes/custom/real_full/${model}/${model}_${task}_${sample}_${config}_full/config_qlora.yaml --load_in_4bit=true"
                #code "./recipes/custom/test/${model}/${model}_${task}_${sample}_${config}/config_qlora.yaml"
                ACCELERATE_LOG_LEVEL=info accelerate launch --config_file recipes/accelerate_configs/multi_gpu.yaml --num_processes=1 scripts/run_sft_classic.py recipes/custom/real_full/${model}/${model}_${task}_${sample}_${config}_full/config_qlora.yaml --load_in_4bit=true
            done
        done
    done            
done