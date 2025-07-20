from private_gpt4_interface import DefaultConversationalHandler

def generate_synthetic_chat_data_from_prompt_template_v4(prompt_context, topics, iterations_per_topic, participants, number_of_days,chat_number):
    #initiates the model
    model = DefaultConversationalHandler()

    #loop over the topics of interest
    for topic in topics:
        index = 1

	#loop over the participants nb of participants (here 2 or 3+)
        for participant in participants:

	    #loop over the number of days (here 1 or 2+)
            for number_of_day in number_of_days:

		#Used to create a small unbalance and get slightly more chats with two persons (6/4 ratio)
                if iterations_per_topic%(len(participants)*len(number_of_days))!=0:
                    if participant == 'two':
                        number_of_prompts = 3
                    else:
                        number_of_prompts = 2
                else:
                    number_of_prompts = iterations_per_topic//(len(participants)*len(number_of_days))

		#generates chats and summaries according to the number of participants
                for prompt in range(number_of_prompts):

		    #used to follow what happens on the console
                    print("_".join(topic.split(" ")))

		    #creates the prompt asking to generate the chat
                    prompt_chat_messages = f"Hey there, I would like to get a series of messages in a chat between {participant} individuals." \
                    f"The topic of the discussion should be related to {topic}. I'd like to have between 5 and 15 messages for this chat." \
                    "I would also like to have a description of the conversation.\n" + prompt_context

		    #creates the prompt asking for a precise summary of the chat
                    prompt_chat_summary = 'Could you know provide a summary of the conversation you just generated?'

		    #sends the chat request prompt and stores the answer
                    model.add_message(prompt_chat_messages)
                    messages_and_description = model.submit_prompt(True)

		    #sends the chat summary request prompt and stores the answer
                    model.add_message(prompt_chat_summary)
                    summary = model.submit_prompt(True)

		    #stores the answer in txt files
                    with open(f"./chat_{str(chat_number)}/{('_'.join(topic.split(' ')))}/chat_messages_and_description_{str(index)}.txt","w") as chat_description_file:
                        chat_description_file.write(messages_and_description)

                    with open(f"./chat_{str(chat_number)}/{'_'.join(topic.split(' '))}/chat_summary_{str(index)}.txt","w") as summary_file:
                        summary_file.write(summary)

                    index += 1

		    #resets all in the model before the next chat generation
                    model.clear_all()

    return 0



if __name__=="__main__":
    #setup for all the parameters used for the prompt, including instrictuions on how to generate the chat

    #['fictional drug trafficking activities', 'fictional heist activities', 'fictional burglary activities', 'hobby activities', 'week-end activities', 'usual day-to-day activities']
    topics = ['soccer or basketball game', 'funny online content', 'making an appointment']

    participants = ['two', 'three or more']

    number_of_days = ['one day','two or more days']

    #useful to provide more information on the format expected, the metadata expected, and the name that should be used
    instruction = "Please only provide the messages without introduction. I also want them in a semicolon separated value format with the following headers:" \
    "sender, and content. \nI also want a description of the the chat." \
    "Please only provide the description without introduction. I want it in semicolon separated value format with the following headers: application (you can chose between [WhatsApp, Telegram, and Signal]," \
    "chat group name, list of participants (in a list), and first message sending datetime (dd.mm.yyyy hh:mm:ss). \n" \
    "\n For the name of the characters, randomly pick any of the following ones: [James, Michael, Robert, John, David, William, Richard," \
    "Joseph, Thomas, Christopher, Charles, Daniel, Matthew, Anthony, Mark, Donald, Steven, Andrew, Paul, Joshua, Kenneth, Kevin, Brian, Timothy, Ronald, Mary, Patricia, Jennifer, Linda, Elizabeth, Barbara," \
    "Susan, Jessica, Karen, Sarah, Lisa, Nancy, Sandra, Betty, Ashley, Emily, Kimberly, Margaret, Donna, Michelle, Carol, Amanda, Melissa, Deborah, Stephanie]. \n Please separate the two elements (the messages and the chat description) with a '-----'," \
    "keep the headers provided, and just provide the two elements in semicolon separated value format (and nothing else)."


    generate_synthetic_chat_data_from_prompt_template_v4(instruction,topics,10,participants,number_of_days,180)

    
