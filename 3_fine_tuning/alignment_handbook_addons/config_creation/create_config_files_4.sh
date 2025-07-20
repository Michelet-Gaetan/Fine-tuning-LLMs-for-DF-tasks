#!/bin/bash

# Array of models
models=(
    "Gemma-2-2B"
)

types=(
    "manual"
    "auto"
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

# Loop through each path and run the command
for model in "${models[@]}"; do

    if [ "$model" = "Llama-31-8B" ]; then
        model_path="meta-llama/Meta-Llama-3.1-8B-Instruct"
    elif [ "$model" = "Gemma-2-2B" ]; then
        model_path="google/gemma-2-2b-it"
    elif [ "$model" = "Mistral-7B" ]; then
        model_path="mistralai/Mistral-7B-Instruct-v0.3"
    else
        echo "Problem"
    fi

    for type in "${types[@]}"; do

        if [ "$type" = "manual" ]; then
            type_written=""
        elif [ "$type" = "auto" ]; then
            type_written="_auto"
        else
            echo "Problem"
        fi

        repo_model="./recipes/custom/real${type_written}/${model}"

        if [ -d "$repo_model" ]; then
            echo "Directory $repo_model already exists."
        else
            mkdir "$repo_model"
            echo "Directory $repo_model created."
        fi

        for task in "${tasks[@]}"; do

            for sample in "${samples[@]}"; do

                if [ "$sample" = "60-samples" ]; then
                    dataset=$(echo -e "  GaetanMichelet/chat-60_ft_${task}${type_written}: 1.0")
                elif [ "$sample" = "120-samples" ]; then
                    dataset=$(echo -e "  GaetanMichelet/chat-60_ft_${task}${type_written}: 1.0\n  GaetanMichelet/chat-120_ft_${task}${type_written}: 1.0")
                elif [ "$sample" = "180-samples" ]; then
                    dataset=$(echo -e "  GaetanMichelet/chat-60_ft_${task}${type_written}: 1.0\n  GaetanMichelet/chat-120_ft_${task}${type_written}: 1.0\n  GaetanMichelet/chat-180_ft_${task}${type_written}: 1.0")
                else
                    echo "Problem"
                fi     

                for config in "${configs[@]}"; do

                    name_combo="${model}_${task}_${sample}_${config}${type_written}"

                    repo_file="./recipes/custom/real${type_written}/${model}/${model}_${task}_${sample}_${config}${type_written}"

                    mkdir -p "${repo_file}"

                    file_name="${repo_file}/config_qlora.yaml"

                    if [ "$config" = "config-1" ]; then
                        gradient_accumulation="8"
                        learning_rate="1.0e-04"
                        nb_epoch=50
                    elif [ "$config" = "config-2" ]; then
                        gradient_accumulation="16"
                        learning_rate="1.0e-04"
                        nb_epoch=50
                    else
                        echo "Problem again"
                    fi

                                # Corrected variable assignments (no spaces around '=')
                    text="# Model arguments
model_name_or_path: ${model_path}
model_revision: main
torch_dtype: bfloat16
attn_implementation: flash_attention_2

# LoRA arguments
load_in_4bit: true
use_peft: true
lora_r: 16
lora_alpha: 16
lora_dropout: 0.05
lora_target_modules:
- q_proj
- k_proj
- v_proj
- o_proj
- gate_proj
- up_proj
- down_proj

# Data training arguments
chat_template: \"{{ bos_token }}{% if messages[0]['role'] != 'user' %}{{ raise_exception('System role not supported') }}{% endif %}{% for message in messages %}{% if (message['role'] == 'user') != (loop.index0 % 2 == 0) %}{{ raise_exception('Conversation roles must alternate user/assistant/user/assistant/...') }}{% endif %}{% if (message['role'] == 'assistant') %}{% set role = 'model' %}{% else %}{% set role = message['role'] %}{% endif %}{{ '<start_of_turn>' + role + '\n' + message['content'] | trim + '<end_of_turn>\n' }}{% endfor %}{% if add_generation_prompt %}{{'<start_of_turn>model\n'}}{% endif %}\"
dataset_mixer:
${dataset}
dataset_splits:
- train
- test
preprocessing_num_workers: 12

# SFT trainer config
bf16: true
do_eval: true
eval_strategy: epoch
gradient_accumulation_steps: ${gradient_accumulation}
gradient_checkpointing: true
gradient_checkpointing_kwargs:
  use_reentrant: false
hub_model_id: ${name_combo}
hub_strategy: every_save
learning_rate: ${learning_rate}
log_level: info
logging_steps: 2
logging_strategy: steps
lr_scheduler_type: cosine
max_seq_length: 8192
max_steps: -1
num_train_epochs: ${nb_epoch}
output_dir: data/${name_combo}
overwrite_output_dir: true
per_device_eval_batch_size: 1
per_device_train_batch_size: 1
push_to_hub: true
report_to:
- tensorboard
save_strategy: epoch
save_steps: 25
save_total_limit: 1
seed: 42
warmup_ratio: 0.1
load_best_model_at_end: true"
                    
                    echo "${text}" > "${file_name}"
                done
            done
        done
    done            
done