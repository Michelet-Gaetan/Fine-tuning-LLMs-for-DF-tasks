from private_gpt4_interface import DefaultConversationalHandler
import copy
import random
import csv

def generate_synthetic_chat_data_from_prompt_template_testing_data(topic, participants_names, nb_messages, chat_number, index,addendum):

    #initialize the model
    model = DefaultConversationalHandler()

    #creates the prompt message for the chat      
    prompt_chat_messages = f"Hey there, I would like to get a series of messages in a chat between {participants_names}" \
    f"The topic of the discussion should be related to {topic}. I'd like to have between {nb_messages} messages for this chat." \
    "I would also like to have a description of the conversation.\n" \
    "Please only provide the messages without introduction. I also want them in a semicolon separated value format with the following headers:" \
    "sender, and content. \nI also want a description of the the chat." \
    "Please only provide the description without introduction. I want it in semicolon separated value format with the following headers: application (you can chose between [WhatsApp, Telegram, and Signal]," \
    "chat group name, list of participants (in a list), and first message sending datetime (dd.mm.yyyy hh:mm:ss). \n" \
    "\n Please separate the two elements (the messages and the chat description) with a '-----'," \
    "keep the headers provided, and just provide the two elements in semicolon separated value format (and nothing else)."

    #creates the prompt message for the summary
    prompt_chat_summary = "'Could you know provide a summary of the conversation you just generated?'"

    #submit the prompt message for the chat and stores the response  
    model.add_message(prompt_chat_messages)
    messages_and_description = model.submit_prompt()

    #submit the prompt message for the chat and stores the response  
    model.add_message(prompt_chat_summary)
    summary = model.submit_prompt()

    #stores the chat 
    with open(f"./testing_dataset/sample_{str(chat_number)}/chat_messages_and_description_{str(index)}{addendum}.txt","w") as chat_description_file:
        chat_description_file.write(messages_and_description)

    #stores the summary
    with open(f"./testing_dataset/sample_{str(chat_number)}/chat_summary_{str(index)}{addendum}.txt","w") as summary_file:
        summary_file.write(summary)

    #reset the model
    model.clear_all()

    return 0

def main_testing(potential_participants, nb_participants, potential_nb_messages, chitchat_topics, interesting_topic, chat_number, potential_nb_topics):
    #deepcopy the list not to affect it
    copy_potential_topics = copy.deepcopy(chitchat_topics)

    #select the number of topics for the sample
    nb_topics = potential_nb_topics[random.randint(0,len(potential_nb_topics)-1)]
    print(f"nb_topics: {str(nb_topics)}")

    #select the index for the topic of interest (criminal or non criminal)
    index_interesting_topic = random.randint(0,nb_topics-1)

    #select the participants names according to the number of participants
    participants_names = ""
    for n_participant in range(1,nb_participants+1):
        while True:
	    #check to make sure the name is not in the list two times
            participant_name = potential_participants[random.randint(0,len(potential_participants)-1)]
            if participant_name not in participants_names:
                break
	#add the participant to the list, and add a AND if this is the last participant
        if n_participant == nb_participants:
            participants_names += f"and {participant_name}"
        else:
            participants_names += f"{participant_name}, "
        print(participants_names)

    #for each topic required, generate a chat and a summary
    for index in range(nb_topics):
        if index==index_interesting_topic:
	    #if the index is the one for the topic of interest, add the topic of interest, use 5 and 15 for the number of messages, and add interest in the file names
            nb_messages = "5 and 15"
            topic = interesting_topic
            addendum = "_interest"
        else:
	    #otherwise pick a random nb of messages, pick a random chitchat topic, removes that chitchat topic from the list of potential chitchat topics
            nb_messages = potential_nb_messages[random.randint(0,len(potential_nb_messages)-1)]
            print(f"nb_messages: {str(nb_messages)}")
            topic = copy_potential_topics[random.randint(0,len(copy_potential_topics)-1)]
            print(topic)
            copy_potential_topics.pop(copy_potential_topics.index(topic))
            addendum = ""
	#generate the chat and the summary
        generate_synthetic_chat_data_from_prompt_template_testing_data(topic, participants_names, nb_messages, chat_number, index+1, addendum)


if __name__=="__main__":
    random.seed(52)
    global_index = 1
    potential_crime_topics = ["fictional drug trafficking or dealing activities","fictional heist activities","fictional burglary activities", 
                      "fictional burglary activities currently taking place", "fictional drug dealing activities", "fictional heist that are currently taking place", 
                      "fictional heist currently in progress", "fictional scam activities", "fictional drug manufacturing operation"]
    potential_non_criminal_topics = ["hobby activities","usual day to day activities", "weekend activities", "any hobby activity",
                                      "a usual day to day conversation", "a weekend activity currently taking place" ,
                                      'soccer or basketball game', 'funny online content', 'making an appointment']
    chitchat_topics = ["hobby", "work", "high-school", "college", "travel", "weekend", "current news", "movies", 
                       "TV shows", "entertainment", "sibblings", "family", "health", "online videos", "restaurants", 
                       "video games", "sport", "books", "music", "weather", "concert", "podcasts", "pets", "philosophy", 
                       "dreams"]
    potential_nb_messages = ["5 and 15", "5 and 10", "10 and 15"]
    potential_nb_topics = [4,5,6,7]
    potential_participants = []

    #establish the list of potential participants using a kaggle csv dataset
    with open("names/data.csv","r",encoding='utf-8-sig') as name_dataset_file:
        name_dataset = name_dataset_file.readlines()
    name_dataset_reader = csv.DictReader(name_dataset,delimiter=",")

    #each name is added as many times as its associated counter. Names that are more frequent will more likely be randomly selected
    for name in name_dataset_reader:
        for count in range(int(name["Count"])):
            potential_participants.append(name["Name"])

    #for each criminal topic (here 9)
    for interesting_topic in potential_crime_topics:

	#creates a sample with two persons
        nb_participants = 2

        main_testing(potential_participants=potential_participants, nb_participants=nb_participants, potential_nb_messages=potential_nb_messages, 
                     chitchat_topics=chitchat_topics, interesting_topic=interesting_topic, chat_number=global_index, 
                     potential_nb_topics=potential_nb_topics)
        global_index += 1

	#creates a sample with 3, 4, or 5 persons (randomly selected)
        potential_nb_participants = [3,4,5]
        nb_participants = potential_nb_participants[random.randint(0,len(potential_nb_participants)-1)]

        main_testing(potential_participants=potential_participants, nb_participants=nb_participants, potential_nb_messages=potential_nb_messages, 
                     chitchat_topics=chitchat_topics, interesting_topic=interesting_topic, chat_number=global_index, 
                     potential_nb_topics=potential_nb_topics)
        global_index += 1

    #for each non criminal topic (here 9)
    for interesting_topic in potential_non_criminal_topics:

	#creates a sample with two persons
        nb_participants = 2

        main_testing(potential_participants=potential_participants, nb_participants=nb_participants, potential_nb_messages=potential_nb_messages, 
                     chitchat_topics=chitchat_topics, interesting_topic=interesting_topic, chat_number=global_index, 
                     potential_nb_topics=potential_nb_topics)
        global_index += 1

	#creates a sample with 3, 4, or 5 persons (randomly selected)
        potential_nb_participants = [3,4,5]
        nb_participants = potential_nb_participants[random.randint(0,len(potential_nb_participants)-1)]

        main_testing(potential_participants=potential_participants, nb_participants=nb_participants, potential_nb_messages=potential_nb_messages, 
                     chitchat_topics=chitchat_topics, interesting_topic=interesting_topic, chat_number=global_index, 
                     potential_nb_topics=potential_nb_topics)
        global_index += 1
