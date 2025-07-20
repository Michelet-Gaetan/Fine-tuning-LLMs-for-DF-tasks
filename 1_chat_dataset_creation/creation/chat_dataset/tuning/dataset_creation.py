import csv
import json
import os
from datetime import datetime


#used to facilitate the saving of json data into files
def dump_json(dataset, file_path):
    with open(file_path,"w") as file:
            json.dump(dataset,file,indent=6)
    
    return 0


def from_csv_to_json_v3(file_directory,file_number):
    #creates an empty sample
    dict_formatted = {}

    #retrieves the file containing the chat and metadata
    with open(f"{file_directory}/chat_messages_and_description_{str(file_number)}.txt","r") as message_and_description_file:
        complete_file = message_and_description_file.readlines()

	#creates two temporary lists, one for the messages, one for the description
        messages = []
        description = []
        no_change_token = True
	#stores the lines of the file in two different lists. At the start there is the chat, then a ------------- and finally the metadata
	#as long as the -------------- is not encountered, put the lines with the messages list, then put it with the metadata
        for element in complete_file:
            if '-----' in element:
                no_change_token = False
                continue

            if no_change_token:
                messages.append(element)
            else:
                description.append(element)

    #stores the summary from the summary files
    with open(f"{file_directory}/chat_summary_{str(file_number)}.txt","r") as summary_file:
        summaries = summary_file.readlines()

    #set the csv parsers for the 3 elements (messages, metadata, summaries)
    messages_reader = csv.DictReader(messages,delimiter=";")
    description_reader = csv.DictReader(description,delimiter=";")
    summaries_reader = csv.DictReader(summaries,delimiter=";")

    #append all the messages and stores them in a str
    messages_ready = '\r\n'.join([f"{i['sender']}: {i['content']}" for i in messages_reader])

    #setup the retrieval of the metadata and already adds the file directory information
    description_not_ready = [element for element in description_reader][0]
    description_ready = {}
    description_ready["directory name"] = file_directory.split("/")[-1]

    #parse all the components of the metadata and stores them if they are part of the list of elements we want, otherwise print that there is a problem (file wrongly formatted)
    for element in description_not_ready:
        if "list of participants" in element:
            real_list = [participant for participant in description_not_ready[element].strip("[").strip("]").split(", ")]
            description_ready["list of participants"] = real_list
        elif "first message sending datetime" in element:
            description_ready["first message sending datetime"] = description_not_ready[element]
        elif "application" in element:
            description_ready["application"] = description_not_ready[element]
        elif "chat group name" in element:
            description_ready["chat group name"] = description_not_ready[element]
        else:
            print(f"PROBLEMMMMM with {element} in file {file_number} of directory {file_directory}")

    #setup the retrieval of the summaries
    summary_not_ready = [element for element in summaries_reader][0]
    summary_ready = {}

    #parse all the components of the summary and stores them if they are part of the list of elements we want, otherwise print that there is a problem (file wrongly formatted)
    for element in summary_not_ready:
        if "general" in element:
            summary_ready["general"] = summary_not_ready[element]
        elif "precise" in element:
            summary_ready["precise"] = summary_not_ready[element]
        elif "GPT4_non_adjusted" in element:
            summary_ready["GPT4_non_adjusted"] = summary_not_ready[element]
        elif "GPT4_adjusted" in element:
            summary_ready["GPT4_adjusted"] = summary_not_ready[element]
        else:
            print(f"PROBLEMMMMM with {element} in file {file_number} of directory {file_directory}")

    #check that we have the right number of elements
    if len(summary_ready)!=4:
            print("Problem with the len of the dict")

    if len(description_ready)!=5:
            print("Problem with the len of the dict")

    #return the formatted sample
    dict_formatted = {"metadata": description_ready, "dialogue": messages_ready, "summaries": summary_ready}
    return dict_formatted


if __name__=="__main__":

    #initiates the list containing the dataset
    total = []

    #loop over the datasets
    for dataset in ["60","120","180"]:

	#prepare a training and testing subsets
        list_chats_training = []
        list_chats_testing = []

	#load the directory for the part of the dataset of interest and scan for directories
        directory_of_interest = f'./input/chat_{dataset}_with_modifications'
        list_dir = [f'{directory_of_interest}/{file}' for file in os.listdir(directory_of_interest) if os.path.isdir(f'{directory_of_interest}/{file}')]

	#retrieves the numbers for the first and last chats (will be included in test while the rest is included in the train)
        for dir in list_dir:
            nb_files = int(len(os.listdir(dir))/2)
            first = 1
            last = nb_files
	    #format the samples correctly from the chat and chat summary files
            for index in range(1,nb_files+1):
                i = from_csv_to_json_v3(dir,index)
		#if it is the first or last includes in test
                if index==first or index==last:
                    list_chats_testing.append(i)
                else:
                    list_chats_training.append(i)

	#check if everything went well or if some samples are both in test and train
        print(len(list_chats_testing))
        print(len(list_chats_training))
        for e in list_chats_testing:
            if e in list_chats_training:
                print("Problem with duplicates")

        header_summary = []
        header_description = []

        #small check for the header names to be sure everything is there
        for element in list_chats_testing + list_chats_training:
            for sub_d in element["metadata"]:
                if sub_d in header_description:
                    pass
                else:
                    header_description.append(sub_d)
            for sub_s in element["summaries"]:
                if sub_s in header_summary:
                    pass
                else:
                    header_summary.append(sub_s)

        print(header_summary)
        print(header_description)

	#put everything in total
        total += list_chats_training + list_chats_testing

	#set the path to save the dataset
        output_train_local = f"./output/chat_{dataset}/train.json"
        output_test_local = f"./output/chat_{dataset}/test.json"
        output_train_data = f"../../../data/tuning/chat_{dataset}/train.json"
        output_test_data = f"../../../data/tuning/chat_{dataset}/test.json"

	#saves all the data
        dump_json(list_chats_training,output_train_local)
        dump_json(list_chats_testing,output_test_local)
        dump_json(list_chats_training,output_train_data)
        dump_json(list_chats_testing,output_test_data)

    #check if there is a common summary between the datasets (should not be the case)
    summaries = [i["summaries"]["GPT4_non_adjusted"] for i in total]
    for a in summaries:
        count = 0
        for b in summaries:
            if a==b:
                count += 1
            if count>1:
                print("Duplicates between the 3 datasets")
        

