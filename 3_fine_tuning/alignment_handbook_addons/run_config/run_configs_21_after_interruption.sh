#!/bin/bash

# Array of models
paths=(
    "Llama-31-8B/Llama-31-8B_task-2_180-samples_config-1_full"
    "Llama-31-8B/Llama-31-8B_task-2_180-samples_config-2_full"
    "Llama-31-8B/Llama-31-8B_task-3_60-samples_config-1_full"
    "Llama-31-8B/Llama-31-8B_task-3_60-samples_config-2_full"
    "Llama-31-8B/Llama-31-8B_task-3_120-samples_config-1_full"
    "Llama-31-8B/Llama-31-8B_task-3_120-samples_config-2_full"
    "Llama-31-8B/Llama-31-8B_task-3_180-samples_config-1_full"
    "Llama-31-8B/Llama-31-8B_task-3_180-samples_config-2_full"
)


# Loop through each path and run the command
for path in "${paths[@]}"; do
    echo "ACCELERATE_LOG_LEVEL=info accelerate launch --config_file recipes/accelerate_configs/multi_gpu.yaml --num_processes=1 scripts/run_sft_classic.py recipes/custom/real_full/${path}/config_qlora.yaml --load_in_4bit=true"
    #code "./recipes/custom/test/${model}/${model}_${task}_${sample}_${config}/config_qlora.yaml"
    ACCELERATE_LOG_LEVEL=info accelerate launch --config_file recipes/accelerate_configs/multi_gpu.yaml --num_processes=1 scripts/run_sft_classic.py recipes/custom/real_full/${path}/config_qlora.yaml --load_in_4bit=true        
    sleep 60
done