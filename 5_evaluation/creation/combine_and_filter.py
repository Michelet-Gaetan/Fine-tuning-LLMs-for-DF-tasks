import json

def concatenate_all_json(json_list):
    complete_json = []

    #parse all json, load them and add the content to the complete_json
    for json_file in json_list:
        with open(json_file,"r") as jf:
            complete_json += json.load(jf)

    #establish list of keys for each task
    for element in complete_json:
        if element["task"]=="task-1":
            keys_t1 = element.keys()
            break
    for element in complete_json:
        if element["task"]=="task-2":
            keys_t2 = element.keys()
            break
    for element in complete_json:
        if element["task"]=="task-3":
            keys_t3 = element.keys()
            break

    # check if each element of the new json has the same keys
    for element in complete_json:
        if element["task"]=="task-1":
            for element_key in element.keys():
                if element_key not in keys_t1:
                    print(f"Problem with element key {element_key}")
            for key in keys_t1:
                if key not in element.keys():
                    print(f"Problem with key {key}")
        elif element["task"]=="task-2":
            for element_key in element.keys():
                if element_key not in keys_t2:
                    print(f"Problem with element key {element_key}")
            for key in keys_t2:
                if key not in element.keys():
                    print(f"Problem with key {key}")
        elif element["task"]=="task-3":
            for element_key in element.keys():
                if element_key not in keys_t3:
                    print(f"Problem with element key {element_key}")
            for key in keys_t3:
                if key not in element.keys():
                    print(f"Problem with key {key}")
        else:
            print("AHHHHHHHHHHHHHHHHHHHHHH")

    #returns the concatenation of the json based on the list of paths
    return complete_json


#gathers all the json files and save them
def get_complete_jsons(output_auto, output_base_auto, output_manual, output_base_manual):
    json_ft_base = []
    folders = ['./data/ft_and_base/output', './data/ft_and_base/output_base']
    models = ['Gemma-2-2B', 'Llama-31-8B', 'Mistral-7B']
    tasks = [1, 2, 3]
    modes = ['automatic', 'manual']

    #loop over the different elements to reconstruct the paths of all the json
    #note that they will be concatenated to form 4 groups: ft_auto, ft_manual, base_auto, base_manual
    #the file path construction makes the four list very similar
    #the order will be similar except for the sample type (auto vs manual)
    for folder in folders:
        for mode in modes:
            list_of_files = []
            for model in models:
                for task in tasks:
                    list_of_files.append(f'{folder}/{model}/task-{str(task)}/{mode}/test_with_inferences.json')

            #group the json together based on the list provided
            json_ft_base.append(concatenate_all_json(list_of_files))

    #saves the json to the right place
    with open(output_auto,"w") as out_auto:
        json.dump(json_ft_base[0],out_auto,indent=5)

    with open(output_base_auto,"w") as out_base_auto:
        json.dump(json_ft_base[2],out_base_auto,indent=5)

    with open(output_manual,"w") as out_manual:
        json.dump(json_ft_base[1],out_manual,indent=5)

    with open(output_base_manual,"w") as out_base_manual:
        json.dump(json_ft_base[3],out_base_manual,indent=5)

    print("Okay!!!")

    return json_ft_base

#checks that all the identifiers (except sample_type) between two samples are the same and that the prompts are also the same (basically same sample just the sample_type varies
#this imply that the reference summary varies and can be exchanged
def check_all(element_1,element_2, task, base):
    if base:
        if task == "task_2":
            return (element_1['base_model'] == element_2['base_model'] and
                    element_1['task'] == element_2['task'] and
                    element_1['old_sample']['messages'][0] == element_2['old_sample']['messages'][0] and
                    element_1['old_sample']['messages'][2] == element_2['old_sample']['messages'][2])
        else:
            return (element_1['base_model'] == element_2['base_model'] and
                    element_1['task'] == element_2['task'] and
                    element_1['old_sample']['messages'][0] == element_2['old_sample']['messages'][0])
    else:
        if task == "task_2":
            return (element_1['base_model'] == element_2['base_model'] and
                    element_1['task'] == element_2['task'] and
                    element_1['nb_samples'] == element_2['nb_samples'] and
                    element_1['loss_computation'] == element_2['loss_computation'] and
                    element_1['config'] == element_2['config'] and
                    element_1['old_sample']['messages'][0] == element_2['old_sample']['messages'][0] and
                    element_1['old_sample']['messages'][2] == element_2['old_sample']['messages'][2])
        else:
            return (element_1['base_model'] == element_2['base_model'] and
                    element_1['task'] == element_2['task'] and
                    element_1['nb_samples'] == element_2['nb_samples'] and
                    element_1['loss_computation'] == element_2['loss_computation'] and
                    element_1['config'] == element_2['config'] and
                    element_1['old_sample']['messages'][0] == element_2['old_sample']['messages'][0])


#completes the json by exchanging the reference summaries between similar samples where only the sample_type varies
def combine_and_complete_everything(file_auto,file_manual, output,base):
    grouped_complete_json = []

    #load the two json files
    with open(file_auto) as f_auto:
        json_auto = json.load(f_auto)
    with open(file_manual) as f_manual:
        json_manual = json.load(f_manual)

    print(f"Base is {base}")

    #for samples in each file (taken in order)
    for sample_auto, sample_manual in zip(json_auto,json_manual):
        #create new samples based on the samples
        new_sample_auto = sample_auto
        new_sample_manual = sample_manual

        task = new_sample_auto["task"]

        #check that samples have identifiers in common (except sample_type) and common prompts
        if not check_all(new_sample_auto,new_sample_manual,base,task):
            print("AHHHHHHHHHHHHHH")

        #If this is the case provides the auto reference summary to manual and the manual reference sumyr to the auto
        new_sample_manual["old_sample_manual"] = new_sample_manual["old_sample"]
        new_sample_auto["old_sample_automatic"] = new_sample_auto["old_sample"]

        new_sample_auto["old_sample_manual"] = new_sample_manual["old_sample_manual"]
        new_sample_manual["old_sample_automatic"] = new_sample_auto["old_sample_automatic"]

        #add them to the new dataset
        grouped_complete_json.append(new_sample_manual)
        grouped_complete_json.append(new_sample_auto)

    #save that dataset
    with open(output, "w") as out:
        json.dump(grouped_complete_json, out, indent=5)

    return grouped_complete_json

#this function simply returns the same data but with only the important elements (redundant or useless information is filtered out)
#in the end, only the id are kept with the inference result(s), inference runtime(s), manual reference summary(ies) and auto reference summary(ies)
def apply_filters(input,output,base):
    filtered_json = []

    with open(input, "r") as inp:
        input_json = json.load(inp)

    print(f"Base is now {base}")

    for sample in input_json:
        new_sample = sample
        if base:
            if sample["task"] == "task-2":
                new_sample["expected_result_1_manual"] = sample["old_sample_manual"]["messages"][1]["content"]
                new_sample["expected_result_1_auto"] = sample["old_sample_automatic"]["messages"] [1]["content"]
                new_sample["expected_result_2_manual"] = sample["old_sample_manual"]["messages"][3]["content"]
                new_sample["expected_result_2_auto"] = sample["old_sample_automatic"]["messages"] [3]["content"]
                new_sample.pop("old_sample")
                new_sample.pop("old_sample_manual")
                new_sample.pop("old_sample_automatic")
                new_sample.pop("prompt_1")
                new_sample.pop("prompt_2")
                new_sample.pop("generated_messages")
            elif sample["task"] == "task-3":
                new_sample["expected_result_manual"] = sample["old_sample_manual"]["messages"][1]["content"]
                new_sample["expected_result_auto"] = sample["old_sample_automatic"]["messages"] [1]["content"]
                new_sample.pop("old_sample")
                new_sample.pop("old_sample_manual")
                new_sample.pop("old_sample_automatic")
                new_sample.pop("prompt")
                new_sample.pop("new_messages")
            else:
                new_sample["expected_result_manual"] = sample["old_sample_manual"]["messages"][1]["content"]
                new_sample["expected_result_auto"] = sample["old_sample_automatic"]["messages"] [1]["content"]
                new_sample.pop("old_sample")
                new_sample.pop("old_sample_manual")
                new_sample.pop("old_sample_automatic")
                new_sample.pop("prompt")
                new_sample.pop("generated_messages")

        else:
            if sample["task"] == "task-2":
                new_sample["expected_result_1_manual"] = sample["old_sample_manual"]["messages"][1]["content"]
                new_sample["expected_result_1_auto"] = sample["old_sample_automatic"]["messages"] [1]["content"]
                new_sample["expected_result_2_manual"] = sample["old_sample_manual"]["messages"][3]["content"]
                new_sample["expected_result_2_auto"] = sample["old_sample_automatic"]["messages"] [3]["content"]
                new_sample.pop("old_sample")
                new_sample.pop("old_sample_manual")
                new_sample.pop("old_sample_automatic")
                new_sample.pop("prompt_1")
                new_sample.pop("prompt_2")
                new_sample.pop("generated_messages")
            elif sample["task"]=="task-3":
                new_sample["expected_result_manual"] = sample["old_sample_manual"]["messages"][1]["content"]
                new_sample["expected_result_auto"] = sample["old_sample_automatic"]["messages"] [1]["content"]
                new_sample.pop("old_sample")
                new_sample.pop("old_sample_manual")
                new_sample.pop("old_sample_automatic")
                new_sample.pop("prompt")
                new_sample.pop("new_messages")
            else:
                new_sample["expected_result_manual"] = sample["old_sample_manual"]["messages"][1]["content"]
                new_sample["expected_result_auto"] = sample["old_sample_automatic"]["messages"] [1]["content"]
                new_sample.pop("old_sample")
                new_sample.pop("old_sample_manual")
                new_sample.pop("old_sample_automatic")
                new_sample.pop("prompt")
                new_sample.pop("generated_messages")

        filtered_json.append(new_sample)

    with open(output, "w") as out:
        json.dump(filtered_json,out,indent=5)


    return filtered_json

def main():
    #files to save the concatenated json files
    output_auto = './data_filtered_organized/split/output_auto.json'
    output_base_auto = './data_filtered_organized/split/output_base_auto.json'
    output_manual = './data_filtered_organized/split/output_manual.json'
    output_base_manual = './data_filtered_organized/split/output_base_manual.json'

    #this function groups the json based on the 4 fine-tuned vs base and auto vs manual combinations
    get_complete_jsons(output_auto,output_base_auto,output_manual,output_base_manual)
    

    #give the path to load the data and save the transformed datasets
    input_auto = './data_filtered_organized/split/output_auto.json'
    input_manual = './data_filtered_organized/split/output_manual.json'
    output = './data_filtered_organized/grouped/output.json'
    input_base_auto = './data_filtered_organized/split/output_base_auto.json'
    input_base_manual = './data_filtered_organized/split/output_base_manual.json'
    output_base = './data_filtered_organized/grouped/output_base.json'

    #checks if the samples between dataset 1 and dataset 2 have the same identifiers (except sample_type) and prompts
    #if everything is good (no message in the console), it provides the auto reference summary to the manual version and the manual reference summary to the auto version
    #This is done for the fine.tuned and base datasets
    combine_and_complete_everything(input_auto,input_manual,output,False)
    combine_and_complete_everything(input_base_auto,input_base_manual,output_base,True)

    #give the path tio the input and output
    input = './data_filtered_organized/grouped/output.json'
    input_base = './data_filtered_organized/grouped/output_base.json'
    output_filtered = './data_filtered_organized/filtered/output.json'
    output_filtered_base = './data_filtered_organized/filtered/output_base.json'

    #filters and rename some of the elements to simplify the next step
    apply_filters(input,output_filtered,False)
    apply_filters(input_base, output_filtered_base,True)

if __name__ == '__main__':
    main()
