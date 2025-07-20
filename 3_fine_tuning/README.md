Fine tuning
===========

Once the fine-tuning and testing datasets are ready, the fine-tuning process can start. To do this, we used the [alignment handbook](https://github.com/huggingface/alignment-handbook). Note that our version of the handbook was from July-August 2024.

We added some element to the handbook to adjust it to our needs. 

Note that the datasets used are private (as they contain SAMSUM samples), and you can not use them for fine-tuning. You will have to replace their name with your own dataset if you want to replicate the experiment.

# The scripts (./scripts)

We based our custom scripts on ther ==run_sft.py== script. We first built ==run_sft_classic.py==, a version of this script with an EarlyStoppingCallback (on line 177) to stop the training once the validation loss kept growing (indicating overfitting).

To fine-tune using a loss function computed on the response only (instead of a loss function computed on the prompt and the response as it was initially setup), we had to add a different data collator. To implement it, we also had to provide instruction and response templates which vary between the model (under 'Initialize the data collator'). This is why we have three scripts for this different loss function computation (==run_sft_Gemma.py==, ==run_sft_Llama.py==, and ==run_sft_Mistral.py==)

# The recipes (./recipes)

We have one recipe per fine.tuned model. The elements varying in the model are the following:

The base model (Gemma, Llama, and Mistral) / the loss computation (full or completion) / the type of summary (auto or manual) / the number of samples in the fine.tuning dataset (60, 120, and 180) / the task (task-1, task-2, and task-3) / and the configuration (gradient accumulation of 8 and 16)

Each recipe varies according to these variables. Note that the chat template needed to be provided with the Gemma model, but not with Llama and Mistral.

# The recipes creation (./config_creation)

To automatically generate the recipes, we took one of the recipe present in the alignment handbook and identified the elements that varied for our models. Bash scripts were then used to change the variable elements in a copy of this recipe and write the result in new files. All of them are used for a specific model. Here is a list of the elements that change between the recipes:

The model_path (changes according to the model)
The dataset (note that you will have to replace it with your own dataset)
The gradient_accumulation_steps (changes according to the tested configuration)
The hub_model_id (changes according to the parameters used)
The output_dir (changes according to the parameters used) 

# The execution of the fine-tuning (./run_config)

Finally, all the models were fine.tuned using basj scripts. These scripts automate the generation of the fine-tuning command line and run it.

The base command line is: ACCELERATE_LOG_LEVEL=info accelerate launch --config_file recipes/accelerate_configs/multi_gpu.yaml --num_processes=1 SCRIPT_TO_USE PATH_TO_THE_RECIPE --load_in_4bit=true

The script to use and path to recipe were built based on the parameters of all the fine-tuned models (simple loop over the model, tasks, number of samples, type of samples, and configuration).

There was an interruption and some of the models had to be fine-tuned again.