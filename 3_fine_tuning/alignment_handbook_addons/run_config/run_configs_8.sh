#!/bin/bash

# Array of models
models=(
    "Gemma-2-2B"
)

# Array of tasks
tasks=(
    "task-1"
    "task-2"
    "task-3"
)

types=(
    ""
    "_auto"
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
)

# Loop through each path and run the command
for model in "${models[@]}"; do
    for type in "${types[@]}"; do
        for task in "${tasks[@]}"; do
            for sample in "${samples[@]}"; do
                for config in "${configs[@]}"; do
                    echo "ACCELERATE_LOG_LEVEL=info accelerate launch --config_file recipes/accelerate_configs/multi_gpu.yaml --num_processes=1 scripts/run_sft_classic.py recipes/custom/real_full${type}/${model}/${model}_${task}_${sample}_${config}_full${type}/config_qlora.yaml --load_in_4bit=true"
                    ACCELERATE_LOG_LEVEL=info accelerate launch --config_file recipes/accelerate_configs/multi_gpu.yaml --num_processes=1 scripts/run_sft_classic.py recipes/custom/real_full${type}/${model}/${model}_${task}_${sample}_${config}_full${type}/config_qlora.yaml --load_in_4bit=true
                done
            done
        done
    done            
done