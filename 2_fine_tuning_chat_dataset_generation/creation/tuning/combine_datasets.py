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

#determine the correct separator and changes it to "/r/n" if needed
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
def add_list_and_number_participants(dataset_path,dataset_type):
    #load the datasets
    dataset_json = load_json(dataset_path)

    #if this is my own dataset, simply compute the number of participants
    if dataset_type == "own":
        new_dataset = []
        for sample in dataset_json:

            number_of_participants = len(sample["metadata"]["list of participants"])

            sample['metadata']["number of participants"] = number_of_participants

            new_dataset.append(sample)

        return new_dataset

    #if this is from the samsum dataset, first extract the participants based on the dialogue to obtain the list of participants and then compute the number of participants
    elif dataset_type == "samsum":
        new_dataset = []
        for sample in dataset_json:
            list_of_participants = []
            sep = determine_separator(sample["dialogue"])

            for message in sample["dialogue"].split(sep):
                name = message.split(":")[0]
                name_without_space = name.strip(" ")
                if name_without_space in list_of_participants:
                    pass
                else:
                    list_of_participants.append(name_without_space)

            number_of_participants = len(list_of_participants)

            sample["metadata"] = {}
            sample["metadata"]["list of participants"] = list_of_participants
            sample['metadata']["number of participants"] = number_of_participants

            new_dataset.append(sample)
            
        return new_dataset

    #else there is a problem with the datasettype provided
    else:
        print("wrong dataset type provided")

#for each sample, improve the list of participant by providing the "non_anonimized_name", 
#"anonimized_name" and "anonimized_gender" in the participant list. The gender is based on a public datset, 
#a custom dataset based on user input, and user input if required.
#The new participant list is called "list of participants complete"
def attribute_gender_to_names(dataset_chat,dataset_gender_path,new_names_path):

    #initiate the returned datasets, and the new names that were not seen so far
    new_dataset = []
    new_names = {}

    #load the name to gender dataset and store it in a csv dictreader
    with open(dataset_gender_path,"r",encoding='utf-8-sig') as gender_dataset_file:
        gender_dataset = gender_dataset_file.readlines()

    gender_dataset_reader = csv.DictReader(gender_dataset,delimiter=",")

    #the same name can be M and F in the dataset, so we select the one that 
    #has the biggest number of occurences to determine if this is M or F
    isolated_name_gender_prev = {}

    #parse the name dataset and store in the dict the name, gender and count, and only 
    #keeps the most popular gender for a given name
    for element in gender_dataset_reader:
        if element["Name"] in isolated_name_gender_prev:
            if int(element["Count"]) > int(isolated_name_gender_prev[element["Name"]]["Count"]):
                isolated_name_gender_prev[element["Name"]] = {"Count": element["Count"], "Gender": element["Gender"], "Probability": element["Probability"]}
            else:
                pass
        else:
            isolated_name_gender_prev[element["Name"]] = {"Count": element["Count"], "Gender": element["Gender"], "Probability": element["Probability"]}

    #work on the dict to only have the name and the gender, this simplify the future process
    #Note that the name is lowered to also simplify the process
    isolated_name_gender = {element.lower():isolated_name_gender_prev[element]["Gender"] for element in isolated_name_gender_prev}

    #load the dataset of names-gender I created to keep track of names-gender not presents in the big dataset
    new_names_old = load_json(new_names_path)

    #parse the sample and determine the gender for each participant based on their name and the previously loaded datasets
    #return a new list of participant with each time the name and gender and an anonimized name (user_x) with x increasing
    for sample in dataset_chat:
        participant_number = 1
        new_list_participants = []

        for name in sample['metadata']['list of participants']:
            anonimized_name = f"user_{participant_number}"

            if name.lower() in isolated_name_gender:
                anonimized_gender = isolated_name_gender[name.lower()]
            elif name.lower() in new_names_old:
                anonimized_gender = new_names_old[name.lower()]
            #new_names store names not seen before and asks for user input
            else:
                if name.lower() in new_names:
                    anonimized_gender = new_names[name.lower()]
                else:
                    anonimized_gender = input(f"What is the gender for the name {name.lower()}")
                
                    new_names[name.lower()] = anonimized_gender

            #add the name to the new participant list of that sample
            new_list_participants.append({'non_anonimized_name': name, 'anonimized_name':anonimized_name, 'anonimized_gender':anonimized_gender})

            participant_number += 1

        #add the new participant list to the sample
        sample["metadata"]["list of participants complete"] = new_list_participants
    
        #add the sample to the returned dataset
        new_dataset.append(sample)

    #add the new names to the gender-name dataset I created and save it
    for i in new_names:
        new_names_old[i] = new_names[i]

    dump_json(new_names_path,new_names_old)

    return new_dataset

#Parse the dialogues and summaty(ies) of each sample, and add an anonimized version
#"anonimized_dialogue", "anonimized_summaries" and then the three anonimized versions, and "anonimized_summary"
def replace_anonimized_names_in_dialogue_and_summaries(dataset_chat,type):
    new_dataset = []

    #for each sample in the dataset replace the name of the participants by their anonimized name
    for sample in dataset_chat:
        temp_dialogue = sample["dialogue"]
        for participant in sample["metadata"]["list of participants complete"]:
            temp_dialogue = temp_dialogue.replace(participant["non_anonimized_name"],participant["anonimized_name"])
        sample["dialogue_anonimized"] = temp_dialogue

        #Here same as for the dialogue but done for each summary in my dataset
        if type=="own":
            sample["summaries_anonimized"] = {}
            temp_summaries = copy.deepcopy(sample["summaries"])
            for sum in temp_summaries:
                #print(temp_summaries.keys())
                temp_summary = temp_summaries[sum]
                for participant in sample["metadata"]["list of participants complete"]:
                    temp_summary = temp_summary.replace(participant["non_anonimized_name"],participant["anonimized_name"])   
                sample["summaries_anonimized"][sum + "_anonimized"] = temp_summary
                
        #Here exactly same process as the one for the dialogue
        elif type == "samsum":
            temp_summary = sample["summary"]
            for participant in sample["metadata"]["list of participants complete"]:
                    temp_summary = temp_summary.replace(participant["non_anonimized_name"],participant["anonimized_name"])
            sample["summary_anonimized"] = temp_summary

        else:
            print("wrong dataset type provided")
        
        new_dataset.append(sample)
        
    return new_dataset

#determine if the number of participants of each gender is the same between the sample and the candidate
#if there is a N discard the cadidate directly (sometimes some strange entities such as a shop or a metaphorical entity)
def same_number_of_person_by_gender(sample,tested_sample):
    sample_dict = {"M": 0, "F": 0, "N": 0}
    tested_sample_dict = {"M": 0, "F": 0, "N": 0}
    for participant in sample["metadata"]["list of participants complete"]:
        sample_dict[participant["anonimized_gender"]] += 1
    for participant in tested_sample["metadata"]["list of participants complete"]:
        tested_sample_dict[participant["anonimized_gender"]] += 1

    return sample_dict["M"]==tested_sample_dict["M"] and sample_dict["F"]==tested_sample_dict["F"] and sample_dict["N"]==0 and tested_sample_dict["N"]==0

#first check if there is a gender rearrangement needed
#if this is the case, rearranges the list of participants
def arrange_gender_name_matter_if_needed(sample,candidate):
    problem_gender_m = []
    problem_gender_f = []

    #check if the participant gender of each participant matches between the sample and the candidate
    #otherwise, store the participant in a list / if there is a problem with a M that should be a F, 
    #there will be another problem and the other participant will be added to the other list
    for participant,participant_candidate in zip(sample["metadata"]["list of participants complete"],candidate["metadata"]["list of participants complete"]):
        if participant["anonimized_gender"] != participant_candidate["anonimized_gender"]:
            if participant_candidate["anonimized_gender"] == "M":
                problem_gender_m.append(participant_candidate["anonimized_name"])
            else:
                problem_gender_f.append(participant_candidate["anonimized_name"])

    #should not happen but there to be sure
    if len(problem_gender_m) != len(problem_gender_f):
           print("Biiiig problemmmmmmmm")

    #if the list is not empty there is a problem
    if len(problem_gender_m) != 0 and len(problem_gender_f) != 0:
        #copy the candidate dict
        new_candidate = candidate

        candidate_list_of_participants = candidate["metadata"]["list of participants complete"]
        candidate_dialogue = candidate["dialogue_anonimized"]
        candidate_summary = candidate["summary_anonimized"]
        candidate_short_summary = candidate["GPT4_summary_anonimized"]

        rearranged_candidate_list_of_participants = copy.deepcopy(candidate_list_of_participants)
        rearranged_dialogue = candidate_dialogue
        rearranged_summary = candidate_summary
        rearranged_short_summary = candidate_short_summary

        #zip the two lists, and each element from the extracted couple must be interverted (at least the anonimized name)
        for participant_m_anonimized_name, participant_f_anonimized_name in zip(problem_gender_m,problem_gender_f):
            #print(participant_f_anonimized_name + ":" + participant_m_anonimized_name)
            first_encounter = True
            for participant_of_candidate in candidate_list_of_participants:
                #if corresponds to the F, replace it with temp if first encounter otherwise change it to M 
                #(also in dialogue and summary)
                if participant_of_candidate["anonimized_name"] == participant_f_anonimized_name:
                    index = rearranged_candidate_list_of_participants.index(participant_of_candidate)
                    rearranged_candidate_list_of_participants[index]["anonimized_name"] = participant_m_anonimized_name
                    if first_encounter:
                        rearranged_dialogue = rearranged_dialogue.replace(participant_f_anonimized_name,"user_temp")
                        rearranged_summary = rearranged_summary.replace(participant_f_anonimized_name,"user_temp")
                        rearranged_short_summary = rearranged_short_summary.replace(participant_f_anonimized_name,"user_temp")
                        first_encounter = False
                    else:
                        rearranged_dialogue = rearranged_dialogue.replace(participant_f_anonimized_name,participant_m_anonimized_name)
                        rearranged_summary = rearranged_summary.replace(participant_f_anonimized_name,participant_m_anonimized_name)
                        rearranged_short_summary = rearranged_short_summary.replace(participant_f_anonimized_name,participant_m_anonimized_name)
                        rearranged_dialogue = rearranged_dialogue.replace("user_temp",participant_f_anonimized_name)
                        rearranged_summary = rearranged_summary.replace("user_temp",participant_f_anonimized_name)
                        rearranged_short_summary = rearranged_short_summary.replace("user_temp",participant_f_anonimized_name)

                #same as before but inverted
                elif participant_of_candidate["anonimized_name"] == participant_m_anonimized_name:
                    index = rearranged_candidate_list_of_participants.index(participant_of_candidate)
                    rearranged_candidate_list_of_participants[index]["anonimized_name"] = participant_f_anonimized_name
                    if first_encounter:
                        rearranged_dialogue = rearranged_dialogue.replace(participant_m_anonimized_name,"user_temp")
                        rearranged_summary = rearranged_summary.replace(participant_m_anonimized_name,"user_temp")
                        rearranged_short_summary = rearranged_short_summary.replace(participant_m_anonimized_name,"user_temp")
                        first_encounter = False
                    else:
                        rearranged_dialogue = rearranged_dialogue.replace(participant_m_anonimized_name,participant_f_anonimized_name)
                        rearranged_summary = rearranged_summary.replace(participant_m_anonimized_name,participant_f_anonimized_name)
                        rearranged_short_summary = rearranged_short_summary.replace(participant_m_anonimized_name,participant_f_anonimized_name)
                        rearranged_dialogue = rearranged_dialogue.replace("user_temp",participant_m_anonimized_name)
                        rearranged_summary = rearranged_summary.replace("user_temp",participant_m_anonimized_name)
                        rearranged_short_summary = rearranged_short_summary.replace("user_temp",participant_m_anonimized_name)
                        
                else:
                    pass

        # candidate_list_of_participants = candidate["metadata"]["list of participants complete"]
        # candidate_dialogue = candidate["dialogue"]
        # candidate_summary = candidate["summary"]

        #add the new rearranged elements to the samples
        new_candidate["metadata"]["rearranged list of participants complete"] = rearranged_candidate_list_of_participants
        new_candidate["rearranged_summary_anonimized"] = rearranged_summary
        new_candidate["rearranged_dialogue_anonimized"] = rearranged_dialogue
        new_candidate["rearranged_GPT4_summary_anonimized"] = rearranged_short_summary

        return new_candidate
    
    #otherwise we keep the same and just add the normal list as the new list
    else:
        #just adding the rearrangaed elements for normalization purpose
        candidate["metadata"]["rearranged list of participants complete"] = candidate["metadata"]["list of participants complete"]
        candidate["rearranged_dialogue_anonimized"] = candidate["dialogue_anonimized"]
        candidate["rearranged_summary_anonimized"] = candidate["summary_anonimized"]
        candidate["rearranged_GPT4_summary_anonimized"] = candidate["GPT4_summary_anonimized"]

        return candidate
    
#for each dataset, parse each sample and provide potential candidates from the samsum dataset where
#the number of participants of each gender is the same as the one in the sample.
#It also reorders the participants anonimized name for the candidates so that the gender fits with the sample participants
#Finally it rearranges the dialogue and summary
def mixed_coherent_samples_dataset(list_of_chat_dataset,samsum_dataset,nb_of_samsum_for_each_chat, used_samsum):
    #random number of candidates for each sample
    list_new_dataset = []
    already_used_samsum = used_samsum
    for chat_dataset in list_of_chat_dataset:
        new_dataset = []
        for sample in chat_dataset:
            print("handling a new sample")
            #determines the number of sammples from SAMSUM
            actual_nb_of_samsum_for_each_chat = random.randint(nb_of_samsum_for_each_chat//2,nb_of_samsum_for_each_chat)
            keep_count = 0
            problem = ""
            is_done = True
            #if the short GPT4 summaries fails 2 times, add a marker and is generated later
            while is_done:
                if keep_count > 1:
                    is_done = False
                    sample["summaries"]["GPT4_short"] = "HELP HERE"
                    print("one more try")
                try:
                    #try to generate a short summary using GPT4
                    sample["summaries"]["GPT4_short"] = prepare_generation_and_generate(sample,"own",problem)
                    is_done = False
                except:
                    problem = "Hey there, I need you to provide a short summary of a fictional chat conversation. For each message you will find" \
                        " the sender and the content in the following format: 'sender: content'"
                    keep_count += 1
                    print("Nooooo problem with the generation")
            
            #anonimizes the new GPT4 summary
            temp_GPT4_short = sample["summaries"]["GPT4_short"]
            for participant in sample["metadata"]["list of participants complete"]:
                temp_GPT4_short = temp_GPT4_short.replace(participant["non_anonimized_name"],participant["anonimized_name"])
            sample["summaries_anonimized"]["GPT4_short_anonimized"] = temp_GPT4_short

            candidates = []
            index = 0
            #keep adding samples until the samsum dataset is completely parsed or the number of candidates is reached
            while len(candidates) < actual_nb_of_samsum_for_each_chat and (index + 1) < len(samsum_dataset):
                tested_sample = samsum_dataset[index]
                #candidate is not reused
                if not (index in already_used_samsum):
                    #if same number of participants, check if same number for each gender and adds the index of the candidate
                    #it if this is the case
                    if tested_sample["metadata"]["number of participants"] == sample["metadata"]["number of participants"]:
                        #check if same number of participants for each gender
                        if same_number_of_person_by_gender(sample,tested_sample):
                            candidates.append(index)
                            already_used_samsum.append(index)
                        else:pass
                    else:pass
                else:pass
                index += 1

            #turns index into actual candidates
            actual_candidates = [samsum_dataset[i] for i in candidates]
            new_actual_candidates = []

            #for each candidates rearrange the order of participants so that they match the sample
            #then rearrange the dialogue and summary if needed
            for candidate in actual_candidates:
                is_done = True
                problem = ""
                keep_count = 0
                while is_done:
                    #if the short GPT4 summaries fails 2 times, add a marker and is generated later
                    if keep_count > 1:
                        is_done = False
                        candidate["GPT4_summary"] = "HELP HERE"
                        print("one more try")
                    #try to generate a short summary using GPT4
                    try:
                        candidate["GPT4_summary"] = prepare_generation_and_generate(candidate,"samsum",problem)
                        is_done = False
                    except:
                        problem = "Hey there, I need you to provide a short summary of a fictional chat conversation. For each message you will find" \
                        " the sender and the content in the following format: 'sender: content'"
                        keep_count += 1
                        print("Nooooo problem with the generation!")

                #anonimizes the new GPT4 summary
                temp_GPT4_summary = candidate["GPT4_summary"]
                for participant in candidate["metadata"]["list of participants complete"]:
                    temp_GPT4_summary = temp_GPT4_summary.replace(participant["non_anonimized_name"],participant["anonimized_name"])
                candidate["GPT4_summary_anonimized"] = temp_GPT4_summary

                new_actual_candidates.append(arrange_gender_name_matter_if_needed(sample,candidate))

            #create a new sample containing the sample from my database "own", and the list of candidates from samsum "samsum"
            new_sample = {"own":sample, "samsum": new_actual_candidates}
            new_dataset.append(new_sample)
        list_new_dataset.append(new_dataset)
    list_new_dataset.append(already_used_samsum)
    return list_new_dataset


def mixing_datasets_and_setting_timestamps(mixed_coherent_dataset):

    #set the details for the min and max min differences between messages and topics, will be in parameters someday
    new_dataset = []
    diff_min_message = 30 #seconds
    diff_max_message = 120 #2 min
    diff_min_topic = 3600 #1 hours
    diff_max_topic = 21600 #6 hours

    #transform the first message datetime of my topic, then determines order of topics (mine and samsum)
    #works with indexes so for now only indexes and the base timestamp
    for sample in mixed_coherent_dataset:
        base_timestamp = datetime.strptime(sample["own"]["metadata"]["first message sending datetime"],"%d.%m.%Y %H:%M:%S")
        #select random order and puts the indexes in a list
        len_samples = 1 + len(sample["samsum"])
        pool = list(range(len_samples))
        final_order = []
        while len(pool) >= 1:
            selected_index = random.randint(0,len(pool)-1)
            selected_sample_index = pool[selected_index]
            final_order.append(selected_sample_index)
            pool.remove(selected_sample_index)

        #select randoms timedelta. watchout, must be 0 when it is 0 in the list order because it will correspond to my sample
        list_timedelta = []
        count = 0
        for index in final_order:
            if index==0:
                stop_point = count
                list_timedelta.append(timedelta(seconds=0.0))
            else:
                list_timedelta.append(timedelta(seconds=float(random.randint(diff_min_topic,diff_max_topic))))
            count += 1

        #update delta topic to add them together, which means that considering my topic being topic 0, 
        #topic 2 must have the timedelta of topic 1 and topic 2
        #same in negative, topic -3 must have timedelta of topic -1 and -2 and -3
        updated_list_timedelta = []
        central_list_timedelta = stop_point #index of my topic
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
        for order_index,delta_topic in zip(final_order,updated_list_timedelta):


            #determine type and pick sample
            if order_index == 0:
                current_sample = sample["own"]
                current_summary = current_sample['summaries_anonimized']["general_anonimized"].strip('\n')
                current_GPT4_summary = current_sample['summaries_anonimized']["GPT4_short_anonimized"].strip('\n')
                sample_type = "own"
            else:
                current_sample = sample["samsum"][order_index-1]
                current_summary = current_sample['rearranged_summary_anonimized'].strip('\n')
                current_GPT4_summary = current_sample["rearranged_GPT4_summary_anonimized"].strip('\n')
                sample_type = "samsum"

            #determine if sample is after or before my own sample in the order
            after = final_order.index(order_index) >= final_order.index(0)

            #set up new variables for the new summary and the new dialogue
            new_summary = ""
            new_GPT4_summary = ""
            new_dialogue= ""

            #if after, we must add
            if after:
                if sample_type == "own":
                    index_message = 0
                    timestamp_message_list = []

                    dialogue_list = current_sample["dialogue_anonimized"].split("\r\n")

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

                    dialogue = determine_and_change(current_sample["rearranged_dialogue_anonimized"])
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

                dialogue = determine_and_change(current_sample["rearranged_dialogue_anonimized"])
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
        sample["combined"] = {}
        sample["combined"]["summary_anonimized"] = new_global_summary
        sample["combined"]["GPT4_summary_anonimized"] = new_global_GPT4_summary
        sample["combined"]["dialogue_anonimized"] = new_global_dialogue
        sample["combined"]["prompt_2"] = f"Topic starting at {timestamp_start_own.strftime('%d.%m.%Y %H:%M:%S')} and ending at {timestamp_end_own.strftime('%d.%m.%Y %H:%M:%S')}\n"

        new_dataset.append(sample)

    return new_dataset


#used to attribute new names randomly (weighted by name popularity)
def select_new_names(dataset,dataset_gender_path):
    new_dataset = []
    new_names = {}

    #load the dataset of names that contains name occurences in a csv dictreader
    with open(dataset_gender_path,"r",encoding='utf-8-sig') as gender_dataset_file:
        gender_dataset = gender_dataset_file.readlines()

    gender_dataset_reader = csv.DictReader(gender_dataset,delimiter=",")

    list_m = []
    list_f = []

    #append each name as many times as their occurence in the list of names of the correct gender
    for element in gender_dataset_reader:
        if element["Gender"] == "M":
            for count in range(int(element["Count"])):
                list_m.append(element["Name"])
        elif element["Gender"] == "F":
            for count in range(int(element["Count"])):
                list_f.append(element["Name"])
        else:
            pass
    
    #pick randomly (weigthed by name popularity) a new name for each participant according to the 
    #gender and add it to a new participant list
    for sample in dataset:
        new_participants = []
        new_sample = sample
        participants = sample["own"]["metadata"]["list of participants complete"]

        selected_participants = []

        for participant in participants:
            new_participant = copy.deepcopy(participant)
            if participant["anonimized_gender"]=="M":
                current_name_list = list_m
            elif participant["anonimized_gender"]=="F":
                current_name_list = list_f
            #if participant is not M or F alarm
            else:
                print("prooooooooooobbbbbbbblllllemmmmmmmmm")

            #check if already taken, if this is not the case use it
            while True:
                new_name = current_name_list[random.randint(0,len(current_name_list)-1)]
                if not (new_name in selected_participants):
                    break
            new_participant["non_anonimized_name"] = new_name
            new_participants.append(new_participant)
            
        new_sample["combined"]["current list of participants complete"] = new_participants
        new_dataset.append(new_sample)

    return new_dataset


#changes the names in the dialogues and summaries for both combined and own
#create new values with the new
def change_names(dataset):
    new_dataset = []

    for sample in dataset:
        new_sample = copy.deepcopy(sample)

        #change for combined 
        new_summary = new_sample["combined"]["summary_anonimized"]
        new_GPT4_summary = new_sample["combined"]["GPT4_summary_anonimized"]
        new_dialogue = new_sample["combined"]["dialogue_anonimized"]

        for participant in new_sample["combined"]["current list of participants complete"]:
            new_summary = new_summary.replace(participant["anonimized_name"],participant["non_anonimized_name"])
            new_GPT4_summary = new_GPT4_summary.replace(participant["anonimized_name"],participant["non_anonimized_name"])
            new_dialogue = new_dialogue.replace(participant["anonimized_name"],participant["non_anonimized_name"])
        
        new_sample["combined"]["new_summary"] = new_summary
        new_sample["combined"]["new_GPT4_summary"] = new_GPT4_summary
        new_sample["combined"]["new_dialogue"] = new_dialogue

        #change for own
        new_dialogue_own = new_sample["own"]["dialogue_anonimized"]

        for participant in new_sample["combined"]["current list of participants complete"]:
            new_dialogue_own = new_dialogue_own.replace(participant["anonimized_name"],participant["non_anonimized_name"])

        new_sample["own"]["new_dialogue"] = new_dialogue_own

        new_sample["own"]["new_summaries"] = {}

        for sum in new_sample["own"]["summaries_anonimized"]:
            temp_sum = new_sample["own"]["summaries_anonimized"][sum]
            for participant in new_sample["combined"]["current list of participants complete"]:
                temp_sum = temp_sum.replace(participant["anonimized_name"],participant["non_anonimized_name"])
            new_sample["own"]["new_summaries"][f"new_" + sum.replace("_anonimized","")] = temp_sum

        new_dataset.append(new_sample)

    return new_dataset


def prepare_generation_and_generate(sample, sample_type, problem=""):
    
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

    if sample_type == "own":
        dialogue = sample["dialogue"]
    elif sample_type == "samsum":
        dialogue = sample["dialogue"]
    else:
        print("Problem sample type unsupported!")

    #generates the short summary
    short_summary = generate_synthetic_short_summary(introduction,dialogue,instruction,verb)

    return short_summary

def generate_synthetic_short_summary(prompt_introduction, discussion, prompt_short_summary,verb):
    #create the model
    model = DefaultConversationalHandler()
    
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

def main():
    apply_all = False
    datasets = ["chat_60","chat_120","chat_180"]

    #set a seed for the random generator (reproductibility as I may not be authorized to share the new datasets)
    random.seed(1000)

    used_samsum = []

    for dataset_name in datasets:
        #This allow to only reapply the first phase, including the requests to the LLM, when required
        if apply_all:
            #adding the new fields "number of participants", and "list of participants" for the samsum dataset (valid)
            chat_clean = add_list_and_number_participants(f"./input_combine/my_data/{dataset_name}/train.json","own")
            chat_test_clean = add_list_and_number_participants(f"./input_combine/my_data/{dataset_name}/test.json","own")
            samsum_train_clean = add_list_and_number_participants("./input_combine/data_from_other_source/train.json","samsum")
            samsum_test_clean = add_list_and_number_participants("./input_combine/data_from_other_source/test.json","samsum")

            #combine the training and testing datasets from the samsum to have more sample for the later mix (valid)
            samsum_clean = samsum_train_clean + samsum_test_clean

            ##for each sample, add a new "list of participants complete" by providing the "non_anonimized_name", 
            #"anonimized_name" and "anonimized_gender" for each participant. The gender is determined using dataets and 
            #user input. (valid)
            chat_clean_anonimized = attribute_gender_to_names(chat_clean,"./input_combine/other_data/data.csv","./input_combine/other_data/new_data.json")
            chat_test_clean_anonimized = attribute_gender_to_names(chat_test_clean,"./input_combine/other_data/data.csv","./input_combine/other_data/new_data.json")
            samsum_clean_anonimized = attribute_gender_to_names(samsum_clean,"./input_combine/other_data/data.csv","./input_combine/other_data/new_data.json")

            #"anonimized_dialogue", "anonimized_summaries" and then the three anonimized versions ("precise_anonimized", 
            #"GPT4_anonimized", "general_anonimized"), and "anonimized_summary" (valid)
            chat_clean_anonimized_replaced = replace_anonimized_names_in_dialogue_and_summaries(chat_clean_anonimized,"own")
            chat_test_clean_anonimized_replaced = replace_anonimized_names_in_dialogue_and_summaries(chat_test_clean_anonimized,"own")
            samsum_clean_anonimized_replaced = replace_anonimized_names_in_dialogue_and_summaries(samsum_clean_anonimized,"samsum")
            
            #Provide candidates that match the sample with same participants gender and order
            #sample is stored in "own", list of candidates under "samsum"
            #New elements for the samsum elements were required: "rearranged list of participants complete", 
            #"rearranged anonimized summary", and "rearranged anonimized dialogue"
            #Note that it is different from the non rearranged elements only if there was a problem in the participant order. 
            list_mixed_clean_anonimized = mixed_coherent_samples_dataset([chat_clean_anonimized_replaced,chat_test_clean_anonimized_replaced],samsum_clean_anonimized_replaced,6,used_samsum)
            mix_clean_anonimized = list_mixed_clean_anonimized[0]
            mix_test_clean_anonimized = list_mixed_clean_anonimized[1]
            used_samsum = list_mixed_clean_anonimized[2]
            print(used_samsum)
            print(len(used_samsum))
            print(len(set(used_samsum)))
            if len(used_samsum) != len(set(used_samsum)):
                print("Problem!")

            #save the new datasets (valid)
            dump_json(f"./output_combine/mix_coherent_dataset/{dataset_name}/train.json",mix_clean_anonimized)
            dump_json(f"./output_combine/mix_coherent_dataset/{dataset_name}/test.json",mix_test_clean_anonimized)


            print("First part finished!")
        #otherwise, it simply loads it from the current file
        else:
            mix_clean_anonimized = load_json(f"./output_combine/mix_coherent_dataset/{dataset_name}/train.json")
            mix_test_clean_anonimized = load_json(f"./output_combine/mix_coherent_dataset/{dataset_name}/test.json")
        


            #mixes the elements together
            #addition of a new element along "own" and "samsum" named "combined"
            #here are the elements contained in combined:
            #"summary", "dialogue", "prompt_2". "prompt_2 is used for the second prompt in task 2
            # (should be valid)
            mixed = mixing_datasets_and_setting_timestamps(mix_clean_anonimized)
            test_mixed = mixing_datasets_and_setting_timestamps(mix_test_clean_anonimized)

            #save the new datasets into json files
            dump_json(f"./output_combine/mixed/{dataset_name}/train.json",mixed)
            dump_json(f"./output_combine/mixed/{dataset_name}/test.json",test_mixed)

            #Selection of new names for the different participants
            #store it in the combined dict under "current list of participants complete"
            with_selected_names = select_new_names(mixed,"./input_combine/other_data/data.csv")
            with_test_selected_names = select_new_names(test_mixed,"./input_combine/other_data/data.csv")

            #deanonimize texts based on the previoulsy picked names
            #Here the generated summaries and dialogues take the "new_" prefix
            #(should be valid)
            changed_name = change_names(with_selected_names)
            test_changed_name = change_names(with_test_selected_names)
            
            #printing to see if there was a problem somewhere
            print(len(changed_name))
            print(len(test_changed_name))

            #saving everything (valid)
            dump_json(f"./output_combine/final_form/{dataset_name}/train.json",changed_name)
            dump_json(f"./output_combine/final_form/{dataset_name}/test.json",test_changed_name)

            dump_json(f"./input_prompt_generation/{dataset_name}/train.json",changed_name)
            dump_json(f"./input_prompt_generation/{dataset_name}/test.json",test_changed_name)


if __name__=="__main__":
    main()
