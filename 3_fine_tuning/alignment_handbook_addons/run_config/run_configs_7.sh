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
)


#Two remainings models
echo "ACCELERATE_LOG_LEVEL=info accelerate launch --config_file recipes/accelerate_configs/multi_gpu.yaml --num_processes=1 scripts/run_sft_classic.py recipes/custom/real_full/Llama-31-8B/Llama-31-8B_task-3_180-samples_config-1_full/config_qlora.yaml --load_in_4bit=true"
ACCELERATE_LOG_LEVEL=info accelerate launch --config_file recipes/accelerate_configs/multi_gpu.yaml --num_processes=1 scripts/run_sft_classic.py recipes/custom/real_full/Llama-31-8B/Llama-31-8B_task-3_180-samples_config-1_full/config_qlora.yaml --load_in_4bit=true
echo "ACCELERATE_LOG_LEVEL=info accelerate launch --config_file recipes/accelerate_configs/multi_gpu.yaml --num_processes=1 scripts/run_sft_classic.py recipes/custom/real_full/Llama-31-8B/Llama-31-8B_task-3_180-samples_config-2_full/config_qlora.yaml --load_in_4bit=true"
ACCELERATE_LOG_LEVEL=info accelerate launch --config_file recipes/accelerate_configs/multi_gpu.yaml --num_processes=1 scripts/run_sft_classic.py recipes/custom/real_full/Llama-31-8B/Llama-31-8B_task-3_180-samples_config-2_full/config_qlora.yaml --load_in_4bit=true                              


# Loop through each path and run the command
for model in "${models[@]}"; do
    for task in "${tasks[@]}"; do
        for sample in "${samples[@]}"; do
            for config in "${configs[@]}"; do
                echo "ACCELERATE_LOG_LEVEL=info accelerate launch --config_file recipes/accelerate_configs/multi_gpu.yaml --num_processes=1 scripts/run_sft_classic.py recipes/custom/real_full_auto/${model}/${model}_${task}_${sample}_${config}_full_auto/config_qlora.yaml --load_in_4bit=true"
                ACCELERATE_LOG_LEVEL=info accelerate launch --config_file recipes/accelerate_configs/multi_gpu.yaml --num_processes=1 scripts/run_sft_classic.py recipes/custom/real_full_auto/${model}/${model}_${task}_${sample}_${config}_full_auto/config_qlora.yaml --load_in_4bit=true
            done
        done
    done
done            
