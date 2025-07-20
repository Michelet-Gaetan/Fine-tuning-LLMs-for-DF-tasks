import json
import csv
from datetime import datetime, timedelta
import random
import copy
from private_gpt4_interface import DefaultConversationalHandler
#simplify the loading of json files
def load_json(file_path):
    with open(file_path,"r") as dataset_file:
        dataset = json.load(dataset_file)

    return dataset

#simplify the saving of json files
def dump_json(file_path, dataset):
    with open(file_path,"w") as dataset_file:
        json.dump(dataset,dataset_file, indent=6)

    return 0

#determine the separator, either "/n" or "/r/n" and returns it
def determine_separator(dialogue):
    if "\r\n" in dialogue:
        sep = "\r\n"
    else:
        sep = "\n"
    
    return sep

#determine the correct sepearator and changes it to "/r/n" if needed
def determine_and_change(dialogue):
    sep = determine_separator(dialogue)
    if sep == "\n":
        dialogue = dialogue.replace("\n","\r\n")
    else: 
        pass
    return dialogue

#parse the informations in the samples of the datasets and determine the following elements:
#1) the list of participants if this is a sample from the samsum dataset
#2) the number of participants in any case
def add_list_and_number_participants(dataset_path):
    #load the datasets
    dataset_json = load_json(dataset_path)

    #if this is my own dataset, simply compute the number of participants
    new_dataset = []
    for sample in dataset_json:
        number_of_participants = len(sample["metadata"]["list of participants"])
        sample['metadata']["number of participants"] = number_of_participants
        new_dataset.append(sample)

    return new_dataset


def mixing_datasets_and_setting_timestamps(mixed_coherent_dataset):

    #set the details for the min and max min differences between messages and topics, will be in parameters someday
    new_dataset = []
    diff_min_message = 30 #seconds
    diff_max_message = 120 #2 min
    diff_min_topic = 3600 #1 hours
    diff_max_topic = 21600 #6 hours

    #transform the first message datetime of my topic, then determines order of topics (mine and samsum)
    #works with indexes so for now only indexes and the base timestamp
    for sample_series in mixed_coherent_dataset:
        index_interest = int([element["metadata"]["sub_sample"] for element in sample_series if element["metadata"]["is_interest"]][0])
        sample_interest = sample_series[index_interest-1]
        base_timestamp = datetime.strptime(sample_interest["metadata"]["first message sending datetime"],"%d.%m.%Y %H:%M:%S")

        #select randoms timedelta. watchout, must be 0 when it is 0 in the list order because it will correspond to my sample
        list_timedelta = []
        for sample in sample_series:
            if sample["metadata"]["sub_sample"]==index_interest:
                list_timedelta.append(timedelta(seconds=0.0))
            else:
                list_timedelta.append(timedelta(seconds=float(random.randint(diff_min_topic,diff_max_topic))))

        #update delta topic to add them together, which means that considering my topic being topic 0, 
        #topic 2 must have the timedelta of topic 1 and topic 2
        #same in negative, topic -3 must have timedelta of topic -1 and -2 and -3
        updated_list_timedelta = []
        central_list_timedelta = index_interest-1 #index of my topic
        for time_delta in list_timedelta:
            index_time_delta = list_timedelta.index(time_delta)

            #if before my topic, add every timedelta between this topic and mine
            if index_time_delta < central_list_timedelta:
                new_index_time_delta = index_time_delta
                new_time_delta = timedelta(seconds=0.0)
                while new_index_time_delta < central_list_timedelta:
                    new_time_delta += list_timedelta[new_index_time_delta]
                    new_index_time_delta += 1
                updated_list_timedelta.append(new_time_delta)

            #if after, same but between my topic and the one being used
            elif index_time_delta > central_list_timedelta:
                new_index_time_delta = central_list_timedelta + 1
                new_time_delta = timedelta(seconds=0.0)
                while new_index_time_delta <= index_time_delta:
                    new_time_delta += list_timedelta[new_index_time_delta]
                    new_index_time_delta += 1
                updated_list_timedelta.append(new_time_delta)

            #if this is mine, just use the current timedelta (it is 0 so base timestamp)
            else:
                updated_list_timedelta.append(time_delta)

        #now we must work with timedelta inside each topic
        new_global_summary_list = []
        new_global_dialogue_list= []
        new_global_GPT4_summary_list = []

        #for each subpart of the sample, we need to extract the messages and add the timestamps       
        for order_index,delta_topic in zip(range(len(sample_series)),updated_list_timedelta):
            current_sample = sample_series[order_index]
            current_summary = current_sample['summaries']["general"].strip('\n')
            current_GPT4_summary = current_sample['summaries']["GPT4_short_summary"].strip('\n')

            #determine if sample is after or before my own sample in the order
            after = order_index >= index_interest-1

            #set up new variables for the new summary and the new dialogue
            new_summary = ""
            new_GPT4_summary = ""
            new_dialogue= ""

            #if after, we must add
            if after:
                if order_index == index_interest-1:
                    index_message = 0
                    timestamp_message_list = []

                    dialogue_list = current_sample["dialogue"].split("\r\n")

                    #small check to ensure there are more than 2 messages
                    if len(dialogue_list)<3:
                        print("aie")

                    #generate a random timedelta and adds it to the timestamp of the previous message
                    #if no previous message, use the base timestamp + the topic timedelta computed before (383-421)
                    while index_message <= len(dialogue_list)-1:
                        if index_message == 0:
                            current_timestamp = base_timestamp + delta_topic
                            timestamp_message_list.append(current_timestamp)
                        else:
                            current_timestamp = timestamp_message_list[index_message-1] + timedelta(seconds=(float(random.randint(diff_min_message,diff_max_message))))
                            timestamp_message_list.append(current_timestamp)
                        index_message += 1

                    #add the timestamp of each message and then join it
                    new_dialogue_list = [f"{timestamp.strftime('%d.%m.%Y %H:%M:%S')} - {message}" for message,timestamp in zip(dialogue_list,timestamp_message_list)]
                    new_dialogue = "\r\n".join(new_dialogue_list)

                    #keep info for the combined summary
                    timestamp_start = base_timestamp + delta_topic
                    timestamp_start_own = base_timestamp + delta_topic
                    timestamp_end = current_timestamp
                    timestamp_end_own = current_timestamp


                #same as before but difference in the separator
                else:
                    index_message = 0
                    timestamp_message_list = []

                    dialogue = current_sample["dialogue"]
                    dialogue_list = dialogue.split("\r\n")
                    if len(dialogue_list)<3:
                        print("aie")

                    while index_message <= len(dialogue_list)-1:
                        if index_message == 0:
                            current_timestamp = base_timestamp + delta_topic
                            timestamp_message_list.append(current_timestamp)
                        else:
                            current_timestamp = timestamp_message_list[index_message-1] + timedelta(seconds=(float(random.randint(diff_min_message,diff_max_message))))
                            timestamp_message_list.append(current_timestamp)
                        index_message += 1

                    new_dialogue_list = [f"{timestamp.strftime('%d.%m.%Y %H:%M:%S')} - {message}" for message,timestamp in zip(dialogue_list,timestamp_message_list)]
                    new_dialogue = "\r\n".join(new_dialogue_list)

                    timestamp_start = base_timestamp + delta_topic
                    timestamp_end = current_timestamp

            #here before instead of after. We must then substarct the topic timedelta from the timastamp nstead of adding
            else:
                index_message = 0
                timestamp_message_list = []

                dialogue = current_sample["dialogue"]
                dialogue_list = dialogue.split("\r\n")
                if len(dialogue_list)<3:
                        print("aie")

                while index_message <= len(dialogue_list)-1:
                    if index_message == 0:
                        current_timestamp = base_timestamp - delta_topic
                        timestamp_message_list.append(current_timestamp)
                    else:
                        current_timestamp = timestamp_message_list[index_message-1] + timedelta(seconds=(float(random.randint(diff_min_message,diff_max_message))))
                        timestamp_message_list.append(current_timestamp)
                    index_message += 1

                new_dialogue_list = [f"{timestamp.strftime('%d.%m.%Y %H:%M:%S')} - {message}" for message,timestamp in zip(dialogue_list,timestamp_message_list)]
                new_dialogue = "\r\n".join(new_dialogue_list)

                timestamp_start = base_timestamp - delta_topic
                timestamp_end = current_timestamp

            
            #generate the new sub_summary extract based on each summary and the timestamps
            new_summary = f"From the {timestamp_start.strftime('%d.%m.%Y %H:%M:%S')} to the {timestamp_end.strftime('%d.%m.%Y %H:%M:%S')}:\n\t{current_summary}"
            new_GPT4_summary = f"From the {timestamp_start.strftime('%d.%m.%Y %H:%M:%S')} to the {timestamp_end.strftime('%d.%m.%Y %H:%M:%S')}:\n\t{current_GPT4_summary}"

            #add the new sub_dialogue and sub_summary
            new_global_summary_list.append(new_summary)
            new_global_GPT4_summary_list.append(new_GPT4_summary)
            new_global_dialogue_list.append(new_dialogue)

        #generate complete new dialogue and summary
        new_global_summary = "\r\n".join(new_global_summary_list)
        new_global_GPT4_summary = "\r\n".join(new_global_GPT4_summary_list)
        new_global_dialogue = "\r\n".join(new_global_dialogue_list)

        #adding every new element to the "combined" dic
        new_sample={}
        sample_list = copy.deepcopy(sample_series)
        sample_interest = sample_series[index_interest-1]
        new_sample["samples"]=sample_list
        new_sample["interest"]=sample_interest
        new_sample["combined"] = {}
        new_sample["combined"]["summary"] = new_global_summary
        new_sample["combined"]["GPT4_summary"] = new_global_GPT4_summary
        new_sample["combined"]["dialogue"] = new_global_dialogue
        new_sample["combined"]["prompt_2"] = f"Topic starting at {timestamp_start_own.strftime('%d.%m.%Y %H:%M:%S')} and ending at {timestamp_end_own.strftime('%d.%m.%Y %H:%M:%S')}\n"

        new_dataset.append(new_sample)

    return new_dataset


def prepare_generation_and_generate(sample, problem=""):
    #add the introduction according to the parameter problem
    if problem=="":
        introduction = "Hey there, I need you to provide a short summary of a chat conversation. For each message you will find" \
        " the sender and the content in the following format: 'sender: content'"

        verb = False

    else:
        introduction = problem
        verb = True

    #instruction provided to the model
    instruction = "Please provide of short summary of the chat (1 sentence maximum). Do not provide any introduction," \
    " directly provide the summary! Also, use the name of each sender when you refer to them!"

    dialogue = sample["dialogue"]

    #generates the short summary
    short_summary = generate_synthetic_short_summary(introduction,dialogue,instruction,verb)

    return short_summary

def generate_synthetic_short_summary(prompt_introduction, discussion, prompt_short_summary,verb):
    #create the model
    model = DefaultConversationalHandler()

    print("generating")
    
    #prepare the prompt by concatenating all the elements
    complete_prompt = '\n'.join([prompt_introduction, discussion, prompt_short_summary])
           
    #add the prompt and submit it
    model.add_message(complete_prompt)
    if verb:
        print(complete_prompt)
    short_summary = model.submit_prompt(verb)

    #clear the model
    model.clear_all()

    return short_summary

def organize_samples(dataset):
    new_dataset = []

    #list the samples ids
    list_actual_samples_id = [element for element in set([sample["metadata"]["sample"] for sample in dataset])]
    list_actual_samples_id.sort(key=lambda x: int(x))

    print(list_actual_samples_id)

    #for each sample id, gathers the subsamples belonging to that sample and order them
    for sample_id in list_actual_samples_id:
        sub_set = [element for element in dataset if element["metadata"]["sample"]==sample_id]
        sub_set.sort(key=lambda x: int(x["metadata"]["sub_sample"]))

        new_dataset.append(sub_set)
    return new_dataset

def main():
    run_all = False
    #set a seed for the random generator (reproductibility as I may not be authorized to share the new datasets)
    random.seed(1000)

    if run_all:#adding the new fields "number of participants", and "list of participants" for the samsum dataset (valid)
        chat_clean = add_list_and_number_participants(f"./input_combine/test.json")

        chat_clean_complete = []

        for sample in chat_clean:
            is_done = True
            problem = ""
            keep_count = 0
            #if the short GPT4 summaries fails 2 times, add a marker and is generated later
            while is_done:
                if keep_count > 1:
                    is_done = False
                    sample["summaries"]["GPT4_short_summary"] = "HELP HERE"
                    print("one more try")
                #try to generate a short summary using GPT4
                try:
                    sample["summaries"]["GPT4_short_summary"] = prepare_generation_and_generate(sample,problem)
                    is_done = False
                except:
                    problem = "Hey there, I need you to provide a short summary of a fictional chat conversation. For each message you will find" \
                    " the sender and the content in the following format: 'sender: content'"
                    keep_count += 1
                    print("Nooooo problem with the generation!")

            chat_clean_complete.append(sample)

        dump_json(f"./output_combine/complete/test.json",chat_clean_complete)

    chat_clean_complete = load_json(f"./output_combine/complete/test.json")
        
    chat_clean_complete_organized = organize_samples(chat_clean_complete)

    dump_json(f"./output_combine/organized/test.json",chat_clean_complete_organized)


    chat_clean_complete_mixed = mixing_datasets_and_setting_timestamps(chat_clean_complete_organized)

    # #save the new datasets into json files
    dump_json(f"./output_combine/final_form/test.json",chat_clean_complete_mixed)
    dump_json(f"./input_prompt_generation/test.json",chat_clean_complete_mixed)
    # #saving everything (valid)
    # dump_json(f"./output_combine/final_form/test.json",test_changed_name)
    # dump_json(f"./input_prompt_generation/test.json",test_changed_name)


if __name__=="__main__":
    main()
