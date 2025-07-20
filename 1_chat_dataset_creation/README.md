Chat dataset creation
=====================

In this first step of the experiment, chats relating to a single topic were generated. Each sample contains a chat with several messages between 2 or more users, a precise GPT4 generated summary, a precise manually generated summary, a general manually generated summary, and some metadata (application/group name/participants/date of first message). Note that a general GPT4 generated summary will be added later in the process.

The topics of discussion varied between criminal and non-criminal related topics.

In total, 172 samples were created for the training and validation of the model (58 / 54 / 60) and 36 were created for testing and comparing the fine-tuned models.

The repository is separated in code and data. In data you will find the result obtained after following the process for this step. In creation you will find the codes and data used to obtain the results present in data. For this step, everything could be shared.


# Part One: Chat dataset creation through GPT4 (creation/chat_dataset_raw/)

This folder is separated between testing and tuning. While the idea is the same and the ==private_gpt4_interface.py== remains the same in the two subfolders, the ==chat_request.py== and ==testing_chat_request.py== varies slightly between the two.

We used GPT4 to generate the chats, a precise summary of these chats, and the associated metadata. The interface between the ==chat_request.py== script and the language model is managed by ==private_gpt4_interface.py==.

If you want to use ==private_gpt4_interface.py==, you need to add your own API endpoint, key, and proxies in the code first.

## Tuning (creation/chat_dataset_raw/tuning/)

Before executing ==chat_request.py==, you can change some of the parameters in the main part of the code.

The list of topics will provide the topic of interest for the chats (If you want to reproduce the experiment you can see the complete list of topics we used in the names of the folders in ./chat_60, ./chat_120, and ./chat_180.)
The number of participants is simply how many participants are part of the chat group (here 2 or 3+)
The number of days was kept from a previous version and is not really useful (here a list of two elements - it should be a list of size 2 if you use 10 chats per topic)
The number of chats per topic provided directly in the function call (here 10) 
The instruction provides information on the format and metadata expected for the chat as well as some names that can be used for the participants (see in the code)
The chat number provided directly in the function call gives information the part of the dataset being created (here 180 as it was the last part of the dataset)

For each topic and number of participants, several chats/metadata and summaries will be generated in a csv like format. With the parameters we used and for each topic, 6 chats between two persons and 4 chats between three and + persons are created (with their respective summary).

Each subset of the dataset (60/120/180) contains 6 topics and therefore approximately 60 samples.

In the end, each part of the dataset (60/120/180) contains folders named with topics and containing all the chats/metadata and summaries that relate to these topics (one file for the chat and one file for the summary with a common index). Each part of the dataset (chat_60/chat_120/chat_180) contains different topics.

These summaries and chats were reviewed and adjusted in part two.

## Testing (creation/chat_dataset_raw/testing/)

First, make sure to download the [kaggle name dataset](https://www.kaggle.com/datasets/gracehephzibahm/gender-by-name) and put the csv file in ./names/

The testing dataset generation was a bit different. For the fine-tuning, the topics of interest (criminal or non criminal) were generated using GPT4 and then combined with chit-chat from the SAMSUM dataset. To avoid having SAMSUM samples in the testing dataset (data-leakage), all the chats (chats of interest and chit-chat) were generated through GPT4. This means that the ==testing_chat_request.py== generates both the topics of interest (criminal or non-criminal) and the chit-chat.

Before executing ==chat_request.py==, you can change some of the parameters in the main part of the code.

The random seed is used to allow people to repeat our experiment (here 52)
The potential crime topics are the topics of interest related to crime (here they are the same as the ones used fot the tuning dataset)
The potential non criminal topics are the topics of interest that are not related to crime (here they are the same as the ones used fot the tuning dataset)
The chitchat topics are the topics that are not interesting and just uninteresting discussions (here we imagined a few)
The potential number of messages is there to bring variety in the number of messages generated (here 5-15, 5-10, and 10-15)
The potential number of topics determines how many topics will be present for one sample, with a single topic of interest (criminal or non criminal) and the rest of chitchat (here 4 to 7)
The potential participants is a list of participants names appearing several times. Each name is added to the list as many time as its count in the dataset. Popular names will appear more times in the list and will be more likely to be picked randomly (here we used a kaggle dataset)
The number of participants is predetermined and cannot be changed, with this time a balance between the chat with two and three + persons. This is due to a smaller number of samples for this dataset (only 36)

For each topic of interest, 2 samples will be created. One with two persons and one with 3+ persons. Each of these samples will contain the topic of interest and a few chit chat topics. With our parameters, it means that 36 samples will be created, including 18 with a criminal topic of interest and 18 with a non criminal topic of interest

In the end, each of the 36 samples of the testing datasets are stored in a folder (./testing_dataset/). In each of these folders, the chat/metadata and summaries files are stored in a csv like format (one file for the chat and one file for the summary with a common index). The files containing the topic of interest and its summary contain the addendum _of_interest.

These summaries and chats were reviewed and adjusted in part two.


# Part Two: Adjusting the chats and summaries (done manually)

Before going further, all these chats and summaries were manually reviewed. The text was adjusted when needed. For examples, we had to use the term fictional to bypass GPT4 on the criminal topic, and all mention of fictional was removed. The structure was also modified when GPT4 made errors. For example, csv structure of the files was sometimes adjusted (replacing the correct separator or adding it when needed).

Moreover, a precise and a general manually generated summaries are added to the dataset for each sample. Note that no manually precise summary was added for the chitchat chats in the testing dataset (not used later).

This modified version of the dataset was used as input for part three.


# Part Three: Adjusting the chats and summaries (creation/chat_dataset/)

This folder is separated between testing and tuning. While the idea is the same in the two subfolders, the ==dataset_creation.py== and ==testing_dataset_creation.py== varies slightly between the two.

The purpose of these scripts is to format the chats and summaries previously generated (part one) and adapted (part two) in json and add them in json files.

## Tuning (creation/chat_dataset/tuning/)

For the tuning dataset, the data needs to be split into a train and a test subsets (or splits). To do this, every first and last sample of every topic will be added to the test dataset, and the rest to the train dataset.

The script parses the files containing the chat/metadata, and the file containing the summaries (they have a common index) for each topic. Each time they extract the relevant information using the csv like format, transforms it when needed, and stores them in a json format.

The main transformation is the chat that is transformed into a single str containing each line of the chat (author + message) separated by a \r\n.

Many checks are done to ensure that all the elements required are gathered and that there are no duplicates between the test and train subsets.

The result is a test.json and train.json file for chat_60, chat_120, and chat_180.

## Testing (creation/chat_dataset/testing/)

For the testing dataset, the structure of the input data is a bit different. Instead of being clustered by topic of interest, they are stored based on the sample they belong to (out of 36 samples). Each sample contains chats/metadata and summaries files (with a common index) of several topics with one of them being of interest and the rest being chit chat.

Therefore, it travels through each sample folder, retrieves the subsample of interest and mark it as of interest. This sample/subsample/interesting or not elements are also part of the metadata. Otherwise, the process is the same as before, except that all the data is stored in a single dataset as there is no test/train splits.

Once again, many checks are done to ensure that all the elements required are gathered and that there are no duplicates between the test and train subsets, and the main transformation is the chat that is transformed into a single str containing each line of the chat (author + message) separated by a \r\n.

The result is a single test.json file.

# Data (data/)

The data created by following this step can be found in this folder. It is also present on [HuggingFace](https://huggingface.co/GaetanMichelet/datasets).