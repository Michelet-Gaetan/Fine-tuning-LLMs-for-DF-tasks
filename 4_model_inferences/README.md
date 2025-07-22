Inferences generation
=====================

Now that our models are fine-tuned and our testing dataset is ready, it is time to run inferences on each sample of the test dataset for each model (fine-tuned and base models). These inferences will then be compared against our manually and automatically generated reference summaries (expected output).

To do this, we will load the appropriate dataset. There is a dataset for each combination between the task (1, 2, 3) and the sample type (auto, manual).

Then, the appropriate models will be loaded and generate inferences for each sample of the dataset.

# Inference generation (./creation/)

The test datasets are stored in the ==testing_dataset== and ==rerun task-3== folders (this folder contains the data obtained after the rerun for the task-3).

The different scripts were used to generate different parts of the final dataset, but they all work on the same idea.

For the fine-tuned models: Based on the base_model, task, and sample_type, the accurate testing dataset is loaded. Then, inferences are generated with each sample (using the prompt of this sample, or prompts if this is task 2) of the loaded testing dataset using all the fine-tuned model based on this task-sample_type combination. Each returned sample contains the inference or inferences for task-2 as well as the runtime for the inference and information about the fine-tuned model that generated this inference (base_model, task, nb_samples, config, loss_computation, and sample_type). The generation is done without sampling. The new samples are then stored for the evaluation.

Note that a checkpointing mechanism was setup for some of the run. The idea is that if there is a problem during the inference for the fine-tuned models, it is possible to analyze those that already made the inference (and saved them in the inference file) and put them in a skiplist. By doing this, the inference process will skip them and continue where it stopped. This checkpointing mechanism is not useful for the base models but was kept for simplicity. 

For the base models: Same as for the fine-tuned models but this time the loaded dataset (based on the model-task-sample_type) combination will be fed to a single base model. This time the inferences are stored as well as the runtime for the inference, the base_model, task, and sample_type.



Run order:

inferences_from_peft.py was used to generate the inferences with Llama on task-1 and task-3, then with Gemma and Mistral for task-1 and task-3, then with Gemma and Mistral for task-2, and then with Llama for task-2

Llama for task-2 took a long time and a checkpointing system was setup with inferences_from_peft_with_checkpoint.py was setup to reduce impact if an error occured. Therefore,  Llama for task-2 was then run using this new checkpoint system, and had then to be relaunched with a skiplist.

Then, inferences_from_peft_with_checkpoint_check.py was run to generate two samples from the dataset on all fine-tuned models and tasks to check that everything went well (in particular that the sampling was actually disabled) 

inferences_from_base_with_checkpoint.py was then run with all base models and tasks.

Then, inferences_from_base_with_checkpoint_check.py was run to generate two samples from the dataset on all base models and tasks to check that everything went well (in particular that the sampling was actually disabled)

inferences_from_peft_with_checkpoint_task-3.py was run for with the fine-tuned models for task-3, and then had to be run again for Mistral with a skiplist

inferences_from_peft_with_checkpoint_task-3_check.py was rtun to generate the checks

Then, inferences_from_base_with_checkpoint_task-3_check.py was run with all the base models for task-3

Finally inferences_from_base_with_checkpoint_task-3_check.py was run to generate the checks

If you want to rerun the experiment, think of adjusting the parameters in the python file




# Data (./data)

You will find all the data with the inferences there. Note that we had to rerun the inferences for the task-3. In the data used for the evaluation part, the data of task-3 is the one obtained after the rerun.

You will find the data for the fine-tuned and based models as well as some check data used later to confirm that everything went well during the inference process.