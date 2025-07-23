import json

#This functions check if the generated text is the same for two given samples (used to check sampling was deactivated)
def check_result(element_1,element_2,task):
    #check two results for task 2
    if int(task)==2:
        return (element_1['result_1'] == element_2['result_1'] and element_1['result_2'] == element_2['result_2'])

    elif int(task) == 1 or int(task) == 3:
        return element_1['result'] == element_2['result']

    else:
        print(f'There is an error with the task provided')
        return None

#This function checks that prompt are the same between two provided samples
def check_prompt(element_1,element_2,task):
    #check two prompts for task 2
    if int(task) == 2:
        return (element_1['old_sample']['messages'][0] == element_2['old_sample']['messages'][0] and
                element_1['old_sample']['messages'][2] == element_2['old_sample']['messages'][2])

    elif int(task) == 1 or int(task) == 3:
        return element_1['old_sample']['messages'][0] == element_2['old_sample']['messages'][0]

    else:
        print(f'There is an error with the task provided')
        return None

#This functions check if all the identifiers of two given samples are the same
def check_element_result(element_1,element_2,base):
    if base:
        return (element_1['base_model'] == element_2['base_model'] and
                element_1['task'] == element_2['task'] and
                element_1['sample_type'] == element_2['sample_type'] and
                element_1['old_sample']['prompt_id'] == element_2['old_sample']['prompt_id'])
    else:
        return (element_1['base_model'] == element_2['base_model'] and
                element_1['task'] == element_2['task'] and
                element_1['sample_type'] == element_2['sample_type'] and
                element_1['nb_samples'] == element_2['nb_samples'] and
                element_1['loss_computation'] == element_2['loss_computation'] and
                element_1['config'] == element_2['config'] and
                element_1['old_sample']['prompt_id'] == element_2['old_sample']['prompt_id'])

#This functions check if all the identifiers of two given samples are the same (except for the sample_type), but it is based on the prompt itself instead of the identifier
#This function will be used in the next script
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

#controls if same samples have the same results between samples in two files
def check_two_files(file_1,file_2,task,base):
    #setup the bool value and the counter
    is_the_same = True
    counter = 0

    #open and load the data
    with open(file_1,"r") as f1:
        f1_json = json.load(f1)
    with open(file_2,"r") as f2:
        f2_json = json.load(f2)

    #compute the size of the smallest file
    smallest_file_size = min([len(f1_json),len(f2_json)])


    #compare each sample in both files
    for element_from_f1 in f1_json:
        for element_from_f2 in f2_json:
            #when the samples are identical
            if check_element_result(element_from_f1,element_from_f2,base):
                #check if the generated results are the same and update the bool value
                #the counter helps to check if all the elements are compared
                counter += 1
                is_the_same = is_the_same and check_result(element_from_f1,element_from_f2,task)

    #last check to see if the right number of comparisons occured
    if counter!=smallest_file_size:
        print('Problem with the number of common files detected!')

    #if True everything went well
    return is_the_same

#controls if each sample from two files, when compared 1 to 1 in order have same identifier (except sample_type) and prompts content
def check_two_files_all(file_1,file_2,task,base):
    #setup the bool value and the counter
    is_the_same = True
    counter = 0

    #open and load the data
    with open(file_1,"r") as f1:
        f1_json = json.load(f1)
    with open(file_2,"r") as f2:
        f2_json = json.load(f2)

    #compare each sample in both files in the order
    #is_the_same remains true if the two files have same identifier (except sample_type) and prompts content
    for element_from_f1,element_from_f2 in zip(f1_json,f2_json):
        is_the_same = is_the_same and check_all(element_from_f1,element_from_f2, task, base)

    #if True everything went well
    return is_the_same


#same as check_two_files_all but only rely on the prompt (not the id)
def check_two_files_prompt(file_1,file_2,task):
    #setup the bool value and the counter
    is_the_same = True
    counter = 0

    #open and load the data
    with open(file_1,"r") as f1:
        f1_json = json.load(f1)
    with open(file_2,"r") as f2:
        f2_json = json.load(f2)

    #compute the size of the smallest file
    if len(f1_json)!=len(f2_json):
        print("problem with the size of one of the two file")


    #compare each sample in both files in order
    for element_from_f1,element_from_f2 in zip(f1_json,f2_json):
        counter += 1
        is_the_same = is_the_same and check_prompt(element_from_f1,element_from_f2,task)

    #last check to see if the right number of comparisons occured
    if counter!=len(f1_json):
        print('Problem with the number of common files detected!')

    return is_the_same

#same as check_two_files_prompt but designed to compare base (where there are less samples) to ft
#therefore each time the base is finished it restarts
def check_two_files_prompt_base_ft(file_1,file_2,task):
    #setup the bool value and the counter
    is_the_same = True
    counter = 0

    #open and load the data
    with open(file_1,"r") as f1:
        f1_json = json.load(f1)
    with open(file_2,"r") as f2:
        f2_json = json.load(f2)

    #compute the size of the smallest file
    if len(f1_json) < len(f2_json):
        small_json = f1_json
        big_json = f2_json
    elif len(f2_json) < len(f1_json):
        small_json = f2_json
        big_json = f1_json
    else:
        print("both files have same size, strange")

    if len(big_json)%len(small_json)!=0:
        print("problem with the size of one of the two file")

    current_offset = 0
    #compare each sample in both files
    for i in range(len(big_json)//len(small_json)):
        current_offset = i*len(small_json)
        for element_from_f1,element_from_f2 in zip(big_json[current_offset:current_offset+len(small_json)],small_json):
            counter += 1
            is_the_same = is_the_same and check_prompt(element_from_f1,element_from_f2,task)

    #last check to see if the right number of comparisons occured
    if counter!=len(big_json):
        print('Problem with the number of common files detected!')

    return is_the_same

#done to check that sampling was really dectivated by comparing output vs output_check
#done on all the tasks
def check_sampling():
    #check for the no sampling of the models (meaning temperature = 0)
    folders = ['./data/ft_and_base/output','./data/ft_and_base/output_base']
    folders_check = ['./data/ft_and_base/output_check','./data/ft_and_base/output_base_check']
    models = ['Gemma-2-2B','Llama-31-8B','Mistral-7B']
    tasks = [1,2,3]
    modes = ['automatic','manual']

    #test for all files existing by looping
    for folder,folder_check in zip(folders,folders_check):
        # check if base or not
        if (folder == './data/ft_and_base/output_base' and
                folder_check == './data/ft_and_base/output_base_check'):
            base = True
        else:
            base = False
        for model in models:
            for task in tasks:
                for mode in modes:
                    file = f'{folder}/{model}/task-{str(task)}/{mode}/test_with_inferences.json'
                    file_check = f'{folder_check}/{model}/task-{str(task)}/{mode}/test_with_inferences.json'

                    print(check_two_files(file,file_check,task,base))

#check that samples from auto have the same prompt as the sample from manual when other elements are the same. They are taken and compared in order
def check_same_prompt_auto_manual():
    folders = ['./data/ft_and_base/output','./data/ft_and_base/output_base']
    models = ['Gemma-2-2B','Llama-31-8B','Mistral-7B']
    tasks = [1,2,3]
    modes = ['automatic','manual']

    #test for all files existing by looping
    for folder in folders:
        for model in models:
            for task in tasks:
                file_manual = f'{folder}/{model}/task-{str(task)}/manual/test_with_inferences.json'
                file_auto = f'{folder}/{model}/task-{str(task)}/automatic/test_with_inferences.json'

                print(check_two_files_prompt(file_manual,file_auto,task))

#same as before but this time is based on the three models instead of auto vs manual
def check_same_prompt_between_models():
    folders = ['./data/ft_and_base/output','./data/ft_and_base/output_base']
    models = ['Gemma-2-2B','Llama-31-8B','Mistral-7B']
    tasks = [1,2,3]
    modes = ['automatic','manual']

    for folder in folders:
        for mode in modes:
            for task in tasks:
                file_mistral = f'{folder}/Mistral-7B/task-{str(task)}/{mode}/test_with_inferences.json'
                file_llama = f'{folder}/Llama-31-8B/task-{str(task)}/{mode}/test_with_inferences.json'
                file_gemma = f'{folder}/Gemma-2-2B/task-{str(task)}/{mode}/test_with_inferences.json'

                print(check_two_files_prompt(file_mistral,file_llama,task) and
                      check_two_files_prompt(file_mistral,file_gemma,task) and
                      check_two_files_prompt(file_gemma,file_llama,task))


#same but this time dataset that are the same except that they are for a base vs ft models are compared
def check_same_prompt_base_ft():
    folders = ['./data/ft_and_base/output','./data/ft_and_base/output_base']
    models = ['Gemma-2-2B','Llama-31-8B','Mistral-7B']
    tasks = [1,2,3]
    modes = ['automatic','manual']

    for model in models:
        for mode in modes:
            for task in tasks:
                file_ft = f'./data/ft_and_base/output/{model}/task-{str(task)}/{mode}/test_with_inferences.json'
                file_base = f'./data/ft_and_base/output_base/{model}/task-{str(task)}/{mode}/test_with_inferences.json'

                print(check_two_files_prompt_base_ft(file_ft,file_base,task))

#here same check as check_same_prompt_auto_manual but there are additional elements compared: the prompt content and the identifiers (except the sample_type())
def quick_test():
    folders = ['./data/ft_and_base/output', './data/ft_and_base/output_base']
    models = ['Gemma-2-2B', 'Llama-31-8B', 'Mistral-7B']
    tasks = [1, 2, 3]

    for folder in folders:
        if folder == './data/ft_and_base/output_base':
            base = True
        else:
            base = False
        for model in models:
            for task in tasks:
                file_manual = f'{folder}/{model}/task-{str(task)}/manual/test_with_inferences.json'
                file_auto = f'{folder}/{model}/task-{str(task)}/automatic/test_with_inferences.json'

                print(check_two_files_all(file_manual, file_auto, task, base))

#last test, check if all ocmbinations are present and if there are 36 different in each one


if __name__ == '__main__':
    #Note that all tests were run and everything seems to be correct. Ready for the evaluation!
    quick_test()
