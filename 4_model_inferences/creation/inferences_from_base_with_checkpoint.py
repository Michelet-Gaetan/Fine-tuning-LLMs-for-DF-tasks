import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import json
import os
from datetime import datetime

from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM

#used to simplify the loading of data from json files
def load_json(file_path):
    with open(file_path,"r") as file:
        dataset = json.load(file)
    
    return dataset

#used to simplify the saving of data into json files
def dump_json(dataset, file_path):
    with open(file_path,"w") as file:
        json.dump(dataset,file,indent=6)
    
    return 0

#used to generate the inferences on a dataset when the targeted task is task 1
def generate_over_a_t1_dataset(model, tokenizer, dataset, base_model, task, sample_type_name):
    new_dataset = []

    print("let's go")
    #for each element in the dataset
    for index,sample in enumerate(dataset):
        print(index)
        #informations are first gathered (model, task, sample_type) this will be useful to keep track of the model used
        new_sample = {"base_model":base_model,"task":task, "sample_type":sample_type_name}
        #the sample is copied
        new_sample["old_sample"]=sample
        #the prompt is retrieved and saved
        prompt = [sample["messages"][0]]
        new_sample["prompt"] = prompt
        #the time before and after the inference is retrieved to compute the runtime
        bef = datetime.now()
        #the inference is generated and stored using the retrieved prompt and the accurate model
        results = generate_one_shot(model, tokenizer, prompt)
        aft = datetime.now()
        new_sample["prompt_time"] = (aft-bef).total_seconds()
        #the response is saved as well as a copy of the chat (prompt and answer)
        new_sample["result"]=results[0]
        new_sample["generated_messages"] = [sample["messages"][0],{"role":"assistant","content":results[0]}]
        #the sample with the new data is added to the data structure that is returned
        new_dataset.append(new_sample)

    return new_dataset

#used to generate the inferences on a dataset when the targeted task is task 2
def generate_over_a_t2_dataset(model, tokenizer, dataset, base_model, task, sample_type_name):
    new_dataset = []

    print("let's go")
    #for each element in the dataset
    for index,sample in enumerate(dataset):
        print(index)
        #informations are first gathered (model, task, sample_type) this will be useful to keep track of the model used
        new_sample = {"base_model":base_model,"task":task, "sample_type":sample_type_name}
        #the sample is copied
        new_sample["old_sample"]=sample
        #the first prompt is retrieved and saved
        prompt_1 = [sample["messages"][0]]
        new_sample["prompt_1"] = prompt_1
        #the second prompt is retrieved and saved
        prompt_2_not_ready = sample["messages"][2]
        new_sample["prompt_2"] = prompt_2_not_ready
        #the time before and after the first inference is retrieved to compute the runtime
        bef = datetime.now()
        #the first inference is generated and stored using the retrieved prompt and the accurate model
        results_1 = generate_one_shot(model, tokenizer, prompt_1)
        aft = datetime.now()
        print("ok")
        new_sample["prompt_1_time"] = (aft-bef).total_seconds()
        #the response is saved
        new_sample["result_1"]=results_1[0]
        #the second prompt is prepared by combining the first prompt, first response, and second prompt
        prompt_2 = [prompt_1[0],{"role":"assistant","content":results_1[0]},prompt_2_not_ready]
        #the time before and after the second inference is retrieved to compute the runtime
        bef_2 = datetime.now()
        #the second inference is generated and stored using the retrieved prompt and the accurate model
        results_2 = generate_one_shot(model, tokenizer, prompt_2)
        aft_2 = datetime.now()
        new_sample["prompt_2_time"] = (aft_2-bef_2).total_seconds()
        #the second response is saved as well as a copy of the chat (prompt 1, answer 1, prompt 2, answer 2)
        new_sample["result_2"]=results_2[0]
        new_sample["generated_messages"] = [prompt_1[0],{"role":"assistant","content":results_1[0]},prompt_2_not_ready,
                                      {"role":"assistant","content":results_2[0]}]
        #the sample with the new data is added to the data structure that is returned
        new_dataset.append(new_sample)

    return new_dataset

#used to generate the inferences on a dataset when the targeted task is task 3
def generate_over_a_t3_dataset(model, tokenizer, dataset, base_model, task, sample_type_name):
    new_dataset = []

    print("let's go")
    #for each element in the dataset
    for index,sample in enumerate(dataset):
        print(index)
        #informations are first gathered (model, task, sample_type) this will be useful to keep track of the model used
        new_sample = {"base_model":base_model,"task":task, "sample_type":sample_type_name}
        #the sample is copied
        new_sample["old_sample"]=sample
        #the prompt is retrieved and saved
        prompt = [sample["messages"][0]]
        new_sample["prompt"] = prompt
        #the time before and after the inference is retrieved to compute the runtime
        bef = datetime.now()
        #the inference is generated and stored using the retrieved prompt and the accurate model
        results = generate_one_shot(model, tokenizer, prompt)
        aft = datetime.now()
        new_sample["prompt_time"] = (aft-bef).total_seconds()
        #the response is saved as well as a copy of the chat (prompt and answer)
        new_sample["result"]=results[0]
        new_sample["new_messages"] = [prompt[0],{"role":"assistant","content":results[0]}]
        #the sample with the new data is added to the data structure that is returned
        new_dataset.append(new_sample)

    return new_dataset


# This function simply takes a look at the task for the dataset/model and calls the right function according to the task at hand
def generate_over_dataset(model, tokenizer, dataset, base_model, task, sample_type_name):
    if task=="task-1":
        results = generate_over_a_t1_dataset(model=model, tokenizer=tokenizer, dataset=dataset, 
                                                            base_model=base_model, task=task, sample_type_name=sample_type_name)
    elif task=="task-2":
        results = generate_over_a_t2_dataset(model=model, tokenizer=tokenizer, dataset=dataset, 
                                                            base_model=base_model, task=task, sample_type_name=sample_type_name)
    elif task=="task-3":
        results = generate_over_a_t3_dataset(model=model, tokenizer=tokenizer, dataset=dataset, 
                                                            base_model=base_model, task=task, sample_type_name=sample_type_name)
    else:
        print("Problem, task not supported")


    return results

# Generate the inference based on the model provided, tokenizer, and prompt
def generate_one_shot(model, tokenizer, prompt): 

       #prepares the prompt by tokenizing it
       tokenized_chat = tokenizer.apply_chat_template(prompt, tokenize=True, add_generation_prompt=True, return_tensors="pt")
       #generate the inference (not that sampling is deactivated)
       outputs = model.generate(input_ids=tokenized_chat.to("cuda"), do_sample=False, max_new_tokens=2049)
       #retrieves the full prompt and new_prompt (response) that are returned
       full_prompt = tokenizer.decode(outputs[0], skip_special_tokens = True)
       new_prompt = tokenizer.batch_decode(outputs[:, tokenized_chat.shape[1]:], skip_special_tokens=True)[0] #https://github.com/huggingface/transformers/issues/17117

       return (new_prompt,full_prompt)


if __name__=="__main__":
       
    ##################################################################
    #parameters settings

    print("setting parameters")

    skip_list = []

    base_models = ["meta-llama/Meta-Llama-3.1-8B-Instruct","google/gemma-2-2b-it","mistralai/Mistral-7B-Instruct-v0.3"]
    tasks = ["task-1","task-2","task-3"]
    #nb_samples = ["60-samples","120-samples","180-samples"]
    #nb_samples = ["60-samples","120-samples","180-samples"]
    #loss_computations = ["", "_full"]
    sample_types = ["","_auto"]
    #configs=["config-1","config-2"]
    transformers.logging.set_verbosity_error()

    print("setting parameters finished")

    #######################################################################

    #loop over all models
    for base_model in base_models:
        
        #retrieves the name as used in the dataset folders
        if base_model=="meta-llama/Meta-Llama-3.1-8B-Instruct":
             base_model_name = "Llama-31-8B"
        elif base_model=="google/gemma-2-2b-it":
            base_model_name = "Gemma-2-2B"
        elif base_model=="mistralai/Mistral-7B-Instruct-v0.3":
            base_model_name = "Mistral-7B"
        else:
            print("Base model is not supported")

        #loop over the tasks
        for task in tasks:
            #loop over the types
            for sample_type in sample_types:
                print("Launching dataset loading process")

                #retrieves the name as used in the dataset folders
                if sample_type=="_auto":
                    sample_type_name="automatic"
                elif sample_type=="":
                    sample_type_name = "manual"
                else:
                    print("Oops there is a problem with the provided sample_type")

                #retrieves the right testing dataset
                testing_dataset_path = f"./testing_dataset/{task}/{sample_type_name}/test.json"

                #creates the output file (add the model name)
                testing_dataset_with_inferences_path = f"./output_base/{base_model_name}/{task}/{sample_type_name}/test_with_inferences.json"
                
                #load the dataset and prepare the new one
                testing_dataset = load_json(testing_dataset_path)

                print("Dataset loading process finished")

    #######################################################################

                print(f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')} - Launching inference for adapters {base_model} for {task} in {sample_type_name}")

                #load the base model
                model = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=torch.bfloat16)
                model = model.to("cuda")

                #setup the tokenizer based on the base model
                tokenizer = AutoTokenizer.from_pretrained(base_model)

                #check if some data already exists, indicating that some of the models already did the inference
                #if this is the case load the currently existing data
                if os.path.exists(testing_dataset_with_inferences_path):
                    print("Checkpoint available, loading the file")
                    new_complete_dataset = load_json(testing_dataset_with_inferences_path)
                #otherwise create a new one
                else:
                    print("No checkpoint available, initiating with an empty list")
                    new_complete_dataset = []

                #launch the generation over the whole dataset for the current model
                results = generate_over_dataset(model=model, tokenizer=tokenizer, dataset=testing_dataset, 
                                            base_model=base_model, task=task, sample_type_name=sample_type_name)
            
                #add the current results
                new_complete_dataset += results

                print(f"The inferences dataset currently has {str(len(new_complete_dataset))} elements")

                print("Saving checkpoint")
                #save it
                dump_json(new_complete_dataset,testing_dataset_with_inferences_path)
                
                print(f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')} - Inference process finished")


    #######################################################################