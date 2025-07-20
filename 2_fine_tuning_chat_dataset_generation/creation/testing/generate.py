import json
import random
import uuid

#function used to simplify the saving of datasets
def dump_json(dataset,file_path):
    with open(file_path,"w") as file:
        json.dump(dataset,file,indent=6)
    
    return 0

#function used to simplify the loading of datasets
def load_json(file_path):
    with open(file_path,"r") as file:
        dataset = json.load(file)
    
    return dataset

#function taking a sample from the chat summarization dataset, a request file path, and an optional introduction file path to generate a fine-tuning sample for the first task
def generate_message_summary_prompt_v2_task_1(type_sample,json_dataset_sample,
                                       request_file_path,
                                       introduction_message_file_path = None):

    #if there is no introduction message provided, use this one instead. Otherwise use the one provided by extracting the text from the introduction file
    if introduction_message_file_path is None:
        introduction_messages_text = "Here is a series of messages discussing a single topic sent over a messaging application. You'll find the following information for each " \
        "message: the name of the sender and the content of the message. Note that the information is presented in the following format: 'sender: message'\n"
    else:
        with open(introduction_message_file_path,'r') as introduction_messages_file:
            introduction_messages_text = ''.join(introduction_messages_file.readlines())

    #extract the text from the request file
    with open(request_file_path,'r') as request_file:
        request_text = ''.join(request_file.readlines())

    #built the prompt and the expected answer based on the request, introduction, and chat summarization sample
    #also add a prompt id
    #prompt: intro + dialogue (here only one topic) + request
    #answer: precise summary (one with details)
    prompt='\n'.join([introduction_messages_text, json_dataset_sample["interest"]["dialogue"], request_text])
    if type_sample=="manual":
        answer = json_dataset_sample["interest"]["summaries"]["precise"]
    elif type_sample=="automatic":
        answer = json_dataset_sample["interest"]["summaries"]["GPT4_adjusted"]
    else:
        print("Problem with the type")
    user_prompt = {"content": prompt, "role": "user"}
    assistant_prompt = {"content": answer, "role": "assistant"}
    prompt_id = str(uuid.uuid4())

    #return the fine-tuning sample
    return {"prompt": prompt, "prompt_id": prompt_id, "messages": [user_prompt, assistant_prompt]}

#Note: the second task is a 2-step process with two user prompts and two answers from the model
#function taking a sample from the chat summarization dataset, two request file path, and two optionals introduction files paths to generate a fine-tuning sample for the second task
def generate_message_summary_prompt_v2_task_2(type_sample,json_dataset_sample,
                                       initial_request_file_path,
                                       second_request_file_path,
                                       initial_introduction_message_file_path = None,
                                       second_introduction_message_file_path = None):

    #if there is no first introduction message provided, use this one instead. Otherwise use the one provided by extracting the text from the first introduction file
    if initial_introduction_message_file_path is None:
        initial_introduction_messages_text = "Here is a series of messages sent over a messaging application. You'll find the following information for each " \
        "message: the sending datetime, the name of the sender and the content of the message. Note that the information is presented in the following format: 'datetime - sender: message'\n"
    else:
        with open(initial_introduction_message_file_path,'r') as introduction_messages_file:
            initial_introduction_messages_text = ''.join(introduction_messages_file.readlines())

    #if there is no second introduction message provided, use this one instead. Otherwise use the one provided by extracting the text from the second introduction file
    if second_introduction_message_file_path is None:
        second_introduction_messages_text = "I think that the following topic is of interest:\n"
    else:
        with open(second_introduction_message_file_path,'r') as introduction_messages_file:
            second_introduction_messages_text = ''.join(introduction_messages_file.readlines())

    #extract the text from the first request file
    with open(initial_request_file_path,'r') as request_file:
        initial_request_text = ''.join(request_file.readlines())

    #extract the text from the second request file
    with open(second_request_file_path,'r') as request_file:
        second_request_text = ''.join(request_file.readlines())

    #built the prompts and the expected answers based on the requests, introductions, and the chat summarization sample
    #also add a prompt id
    #prompt 1: intro + dialogues (here several topics, with timestamps) + request
    #answer 1: short summary (1-2 sentences) for each topic discussed with starting and ending timestamps for each topic
    #prompt 2: selection of the topic of interest (extracted from my dataset) + request
    #answer 2: precise summary of the topic of interest (one with details)
    prompt_1 = '\n'.join([initial_introduction_messages_text, json_dataset_sample["combined"]["dialogue"].replace("\n\n","\r\n"), initial_request_text])
    prompt_2 = '\n'.join([second_introduction_messages_text, json_dataset_sample["combined"]["prompt_2"], second_request_text])
    if type_sample=="manual":
        answer_1 = json_dataset_sample["combined"]["summary"]
        answer_2 = json_dataset_sample["interest"]["summaries"]["precise"]
    elif type_sample == "automatic":
        answer_1 = json_dataset_sample["combined"]["GPT4_summary"]
        answer_2 = json_dataset_sample["interest"]["summaries"]["GPT4_adjusted"]
    else:
        print("Problem with the type")
    user_prompt_1 = {"content": prompt_1, "role": "user"}
    assistant_prompt_1 = {"content": answer_1, "role": "assistant"}
    user_prompt_2 = {"content": prompt_2, "role": "user"}
    assistant_prompt_2 = {"content": answer_2, "role": "assistant"}
    prompt_id = str(uuid.uuid4())

    #return the fine-tuning sample
    return {"prompt": prompt_1, "prompt_id": prompt_id, "messages": [user_prompt_1, assistant_prompt_1, user_prompt_2, assistant_prompt_2]}


#function taking a sample from the chat summarization dataset, a request file path, and an optional introduction file path to generate a fine-tuning sample for the third task
def generate_message_summary_prompt_v2_task_3(type_sample,json_dataset_sample,
                                       request_file_path,
                                       introduction_message_file_path = None):
    
    list_of_all_crimes = ["drug trafficking or dealing activities","drug trafficking or dealing activities","heist activities","heist activities", "burglary activities","burglary activities","burglary activities currently taking place",
                          "burglary activities currently taking place","drug dealing activities","drug dealing activities", "heist that are currently taking place", "heist that are currently taking place","heist currently in progress",
                          "heist currently in progress", "scam activities","scam activities", "drug manufacturing operation", "drug manufacturing operation"]
    
    #extract and prepare the elements of interest for the investigation
    sample_index = int(json_dataset_sample["interest"]["metadata"]["sample"])-1
    if sample_index < len(list_of_all_crimes):
        investigated_element = list_of_all_crimes[sample_index]
        is_criminal = True
    else:
        is_criminal = False

    #if there is no introduction message provided, use this one instead. Otherwise use the one provided by extracting the text from the introduction file
    if introduction_message_file_path is None:
        if is_criminal:
            introduction_messages_text = f"Here is a series of messages sent over a messaging application. The crime investigated is related to '{investigated_element}'. You'll find the following information for each " \
            "message: the sending datetime, the name of the sender and the content of the message. Note that the information is presented in the following format: 'datetime - sender: message'\n"
        else:
            new_investigated_index = random.randint(0,len(list_of_all_crimes)-1)
            new_investigated = list_of_all_crimes[new_investigated_index]
            introduction_messages_text = f"Here is a series of messages sent over a messaging application. The crime investigated is related to '{new_investigated}'. You'll find the following information for each " \
            "message: the sending datetime, the name of the sender and the content of the message. Note that the information is presented in the following format: 'datetime - sender: message'\n"
    else:
        with open(introduction_message_file_path,'r') as introduction_messages_file:
            introduction_messages_text = ''.join(introduction_messages_file.readlines())

    #extract the text from the request file
    with open(request_file_path,'r') as request_file:
        request_text = ''.join(request_file.readlines())    

    #built the prompt and the expected answer based on the request, introduction, and chat summarization sample
    #also add a prompt id
    #prompt: intro + dialogue (here several topics) + request
    #answer: identification of the topic related to the case with a precise summary of that topic (one with details)
    prompt='\n'.join([introduction_messages_text, json_dataset_sample["combined"]["dialogue"].replace("\n\n","\r\n"), request_text])
    if type_sample=="manual":
        answer_summary = json_dataset_sample["interest"]["summaries"]["precise"]
    elif type_sample=="automatic":
        answer_summary = json_dataset_sample["interest"]["summaries"]["GPT4_adjusted"]
    else:
        print("Problem with the type")
    
    if is_criminal:
        answer_topic = f"The topic of interest identified is the {json_dataset_sample['combined']['prompt_2'].lower()}"
        answer = "\n".join([answer_topic,answer_summary])
    else:
        answer = "None of the topic is interesting for the investigation."
    user_prompt = {"content": prompt, "role": "user"}
    assistant_prompt = {"content": answer, "role": "assistant"}
    prompt_id = str(uuid.uuid4())

    #return the fine-tuning sample
    return (is_criminal,{"prompt": prompt, "prompt_id": prompt_id, "messages": [user_prompt, assistant_prompt]})

def main():

    t1_r1_path = "./input_prompt_generation/requests/task_1_request_1.txt"
    t2_r1_path = "./input_prompt_generation/requests/task_2_request_1.txt"
    t2_r2_path = "./input_prompt_generation/requests/task_2_request_2.txt"
    t3_r1_path = "./input_prompt_generation/requests/task_3_request_1.txt"

    dataset_name = "testing_dataset"
    tasks = ["task-1", "task-2", "task-3"]
    creations = ["manual", "automatic"]

    #apply everythoing to the same dataset
    for task in tasks:
        for creation in creations:

            track_crime = 0
            
            #setup the ouput path for each fine-tuning testing dataset
            test_output = f"./output_prompt_generation/{dataset_name}/{task}/{creation}/test.json"
            
            #setup the ouput path for each fine-tuning testing dataset
            test_output_check = f"../../data/testing_dataset/{dataset_name}/{task}/{creation}/test.json"

            
            #load the training and testing chat summarization datasets
            test_input = f"./input_prompt_generation/test.json"
            testing_dataset = load_json(test_input)

            #setup the lists that will receive the fine-tuning testing dataset for each task
            ft_list_testing = []


            #generate the fine-tuning testing samples for each task based on the current chat summarization dataset
            for sample in testing_dataset:
                if task=="task-1":
                    ft_sample = generate_message_summary_prompt_v2_task_1(type_sample=creation, json_dataset_sample = sample, request_file_path = t1_r1_path)
                    ft_list_testing.append(ft_sample)
                elif task=="task-2":
                    ft_sample = generate_message_summary_prompt_v2_task_2(type_sample=creation, json_dataset_sample = sample, initial_request_file_path = t2_r1_path, second_request_file_path= t2_r2_path)
                    ft_list_testing.append(ft_sample)
                elif task=="task-3":
                    ft_sample = generate_message_summary_prompt_v2_task_3(type_sample=creation, json_dataset_sample = sample, request_file_path = t3_r1_path)
                    if ft_sample[0]:
                        track_crime+=1
                    ft_list_testing.append(ft_sample[1])
                else:
                    print("Problem with the task")

            
            #small print to check everything is still under control (expected number of samples is known for each dataset)
            print(len(ft_list_testing))
            print(f"Number of tracked crimes is {str(track_crime)}")



            #saving the fine-tuning testing dataset for each task
            dump_json(ft_list_testing,test_output)


            #saving the fine-tuning testing dataset for each task
            dump_json(ft_list_testing,test_output_check)

            #saving the fine-tuning testing dataset for each task
            dump_json(ft_list_testing,test_output_inference)



if __name__=="__main__":
    #first run normal
    random.seed(1000)
    main()

