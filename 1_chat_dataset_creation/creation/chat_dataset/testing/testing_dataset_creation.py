import csv
import json
import os
from datetime import datetime

#used to facilitate the saving of json data into files
def dump_json(dataset, file_path):
    with open(file_path,"w") as file:
            json.dump(dataset,file,indent=6)
    
    return 0


def from_csv_to_json_v3(file_directory,file_number, current_sample, is_interest):
    #creates an empty sample
    dict_formatted = {}

    #adds the addendumn when the sample is the sample of interest
    if is_interest:
        addendum = "_interest"
    else:
        addendum = ""

    #retrieves the file containing the chat and metadata
    with open(f"{file_directory}/chat_messages_and_description_{str(file_number)}{addendum}.txt","r") as message_and_description_file:
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
    with open(f"{file_directory}/chat_summary_{str(file_number)}{addendum}.txt","r") as summary_file:
        summaries = summary_file.readlines()
    
    #set the csv parsers for the 3 elements (messages, metadata, summaries)
    messages_reader = csv.DictReader(messages,delimiter=";")
    description_reader = csv.DictReader(description,delimiter=";")
    summaries_reader = csv.DictReader(summaries,delimiter=";")

    #append all the messages and stores them in a str
    messages_ready = '\r\n'.join([f"{i['sender']}: {i['content']}" for i in messages_reader])

    #setup the retrieval of the metadata
    description_not_ready = [element for element in description_reader][0]
    description_ready = {}

    #add metadata that was provided in the function parameters
    description_ready["sample"] = current_sample
    description_ready["sub_sample"] = file_number
    description_ready["is_interest"] = is_interest

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

    #check that we have the right number of elements (here elements not of interest have less summaries)
    if len(summary_ready)!=4 and is_interest:
            print("Problem with the len of the dict")

    if len(summary_ready)!=2 and not is_interest:
            print("Problem with the len of the dict")

    if len(description_ready)!=7:
            print("Problem with the len of the dict")

    #return the formatted sample
    dict_formatted = {"metadata": description_ready, "dialogue": messages_ready, "summaries": summary_ready}

    return dict_formatted


if __name__=="__main__":

    #initiates the list containing the dataset
    total = 0
    list_chats_testing = []

    #load the directory of the dataset and scan for directories
    directory_of_interest = f'./input/testing_dataset_with_modif_finished/testing_dataset_with_modif'
    list_dir = [f'{directory_of_interest}/{file}' for file in os.listdir(directory_of_interest) if os.path.isdir(f'{directory_of_interest}/{file}')]

    print([e.split("/")[-1].replace("sample_","") for e in list_dir])

    #for each directory (representing samples)
    for dir in list_dir:
	#retrieves the sample number
        current_sample = int(dir.split("/")[-1].replace("sample_",""))

	#retieves the number of sub samples for the sample
        nb_files = int(len(os.listdir(dir))/2)
        total += nb_files

	#retrieve the sub sample of interest and its index
        for f in os.listdir(dir):
            if "interest" in f and "summary" in f:
                file_of_interest = f
                print(file_of_interest)
        index_file_of_interest = int(file_of_interest.split("/")[-1].split("_")[-2])

	#check to see if it is accurate
        print(f"current sample is {str(current_sample)}")
        print(f"the file of interest is {str(index_file_of_interest)}")

	#for each sub sample format the samples correctly from the chat and chat summary files and add it to the list 
        for index in range(1,nb_files+1):
            i = from_csv_to_json_v3(dir,index,current_sample, index_file_of_interest==index)
            list_chats_testing.append(i)


    print(len(list_chats_testing))

    header_summary = []
    header_description = []

    #small check for the header names
    for element in list_chats_testing:
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

    #set the path to save the data
    output_test_local = f"./output/test.json"
    output_test_data = f"../../../data/testing/test.json"

    print(total)

    #saves the data
    dump_json(list_chats_testing,output_test_local)
    dump_json(list_chats_testing,output_test_data)
        

