import pandas
import json
import copy
import matplotlib.pyplot as plt
from tabulate import tabulate
import seaborn as sns

#creates the dataset from the json files containing all the data with evaluation
def create_dataframe(input,base):

    #load the data
    with open(input,"r") as json_f:
        samples = json.load(json_f)

    #prepares the json for the dataframe withh all required fields
    values = {"base_model":[],
              "type_model":[],
              "task":[],
              "sample_type": [],
              "nb_samples": [],
              "loss_computation": [],
              "config": [],
              "prompt_time_r1": [],
              "prompt_time_r2": [],
              "bleu_1_r1": [],
              "bleu_2_r1": [],
              "bleu_3_r1": [],
              "bleu_4_r1": [],
              "rouge_1_r1": [],
              "rouge_2_r1": [],
              "rouge_L_r1": [],
              "rouge_Lsum_r1": [],
              "bert_p_r1": [],
              "bert_r_r1": [],
              "bert_f1_r1": [],
              "roberta_p_r1": [],
              "roberta_r_r1": [],
              "roberta_f1_r1": [],
              "bleu_1_auto_r1": [],
              "bleu_2_auto_r1": [],
              "bleu_3_auto_r1": [],
              "bleu_4_auto_r1": [],
              "rouge_1_auto_r1": [],
              "rouge_2_auto_r1": [],
              "rouge_L_auto_r1": [],
              "rouge_Lsum_auto_r1": [],
              "bert_p_auto_r1": [],
              "bert_r_auto_r1": [],
              "bert_f1_auto_r1": [],
              "roberta_p_auto_r1": [],
              "roberta_r_auto_r1": [],
              "roberta_f1_auto_r1": [],
              "bleu_1_r2": [],
              "bleu_2_r2": [],
              "bleu_3_r2": [],
              "bleu_4_r2": [],
              "rouge_1_r2": [],
              "rouge_2_r2": [],
              "rouge_L_r2": [],
              "rouge_Lsum_r2": [],
              "bert_p_r2": [],
              "bert_r_r2": [],
              "bert_f1_r2": [],
              "roberta_p_r2": [],
              "roberta_r_r2": [],
              "roberta_f1_r2": [],
              "bleu_1_auto_r2": [],
              "bleu_2_auto_r2": [],
              "bleu_3_auto_r2": [],
              "bleu_4_auto_r2": [],
              "rouge_1_auto_r2": [],
              "rouge_2_auto_r2": [],
              "rouge_L_auto_r2": [],
              "rouge_Lsum_auto_r2": [],
              "bert_p_auto_r2": [],
              "bert_r_auto_r2": [],
              "bert_f1_auto_r2": [],
              "roberta_p_auto_r2": [],
              "roberta_r_auto_r2": [],
              "roberta_f1_auto_r2": [],
              }


    #for each sample
    for sample in samples:
        #retrieves the name of the base_model and make it more readable before adding to the dataframe
        if sample["base_model"]== "google/gemma-2-2b-it":
            values["base_model"].append("gemma-2-2b")
        elif sample["base_model"]== "meta-llama/Meta-Llama-3.1-8B-Instruct":
            values["base_model"].append("Llama-3.1-8B")
        elif sample["base_model"] == "mistralai/Mistral-7B-Instruct-v0.3":
            values["base_model"].append("Mistral-0.3-7B")
        else:
            print("Problem!")

        #add elements of interest
        values["task"].append(sample["task"])
        values["sample_type"].append(sample["sample_type"])

        #if base adds base for the type and None for missing elements
        if base:
            values["type_model"].append("BASE")
            values["nb_samples"].append(None)
            values["loss_computation"].append(None)
            values["config"].append(None)
        #otherwise set fine-tuning and retrieves values
        else:
            values["type_model"].append("FT")
            values["nb_samples"].append(sample["nb_samples"])
            #add loss in a more readable way
            if sample["loss_computation"] == "":
                values["loss_computation"].append("completion")
            elif sample["loss_computation"] == "_full":
                values["loss_computation"].append("full")
            else:
                print("Problem")
            values["config"].append(sample["config"])

        #if task two add all elements
        if sample["task"] == "task-2":

            values["prompt_time_r1"].append(sample["prompt_1_time"])
            values["prompt_time_r2"].append(sample["prompt_2_time"])

            values["bleu_1_r1"].append(sample["bleu_rouge_bert_1_manual"]["bleu_1"]["bleu"])
            values["bleu_2_r1"].append(sample["bleu_rouge_bert_1_manual"]["bleu_2"]["bleu"])
            values["bleu_3_r1"].append(sample["bleu_rouge_bert_1_manual"]["bleu_3"]["bleu"])
            values["bleu_4_r1"].append(sample["bleu_rouge_bert_1_manual"]["bleu_4"]["bleu"])

            values["rouge_1_r1"].append(sample["bleu_rouge_bert_1_manual"]["rouge"]["rouge1"])
            values["rouge_2_r1"].append(sample["bleu_rouge_bert_1_manual"]["rouge"]["rouge2"])
            values["rouge_L_r1"].append(sample["bleu_rouge_bert_1_manual"]["rouge"]["rougeL"])
            values["rouge_Lsum_r1"].append(sample["bleu_rouge_bert_1_manual"]["rouge"]["rougeLsum"])

            values["bert_p_r1"].append(sample["bleu_rouge_bert_1_manual"]["bertscore_bert"]["precision"][0])
            values["bert_r_r1"].append(sample["bleu_rouge_bert_1_manual"]["bertscore_bert"]["recall"][0])
            values["bert_f1_r1"].append(sample["bleu_rouge_bert_1_manual"]["bertscore_bert"]["f1"][0])

            values["roberta_p_r1"].append(sample["bleu_rouge_bert_1_manual"]["bertscore_roberta"]["precision"][0])
            values["roberta_r_r1"].append(sample["bleu_rouge_bert_1_manual"]["bertscore_roberta"]["recall"][0])
            values["roberta_f1_r1"].append(sample["bleu_rouge_bert_1_manual"]["bertscore_roberta"]["f1"][0])

            values["bleu_1_auto_r1"].append(sample["bleu_rouge_bert_1_auto"]["bleu_1"]["bleu"])
            values["bleu_2_auto_r1"].append(sample["bleu_rouge_bert_1_auto"]["bleu_2"]["bleu"])
            values["bleu_3_auto_r1"].append(sample["bleu_rouge_bert_1_auto"]["bleu_3"]["bleu"])
            values["bleu_4_auto_r1"].append(sample["bleu_rouge_bert_1_auto"]["bleu_4"]["bleu"])

            values["rouge_1_auto_r1"].append(sample["bleu_rouge_bert_1_auto"]["rouge"]["rouge1"])
            values["rouge_2_auto_r1"].append(sample["bleu_rouge_bert_1_auto"]["rouge"]["rouge2"])
            values["rouge_L_auto_r1"].append(sample["bleu_rouge_bert_1_auto"]["rouge"]["rougeL"])
            values["rouge_Lsum_auto_r1"].append(sample["bleu_rouge_bert_1_auto"]["rouge"]["rougeLsum"])

            values["bert_p_auto_r1"].append(sample["bleu_rouge_bert_1_auto"]["bertscore_bert"]["precision"][0])
            values["bert_r_auto_r1"].append(sample["bleu_rouge_bert_1_auto"]["bertscore_bert"]["recall"][0])
            values["bert_f1_auto_r1"].append(sample["bleu_rouge_bert_1_auto"]["bertscore_bert"]["f1"][0])

            values["roberta_p_auto_r1"].append(sample["bleu_rouge_bert_1_auto"]["bertscore_roberta"]["precision"][0])
            values["roberta_r_auto_r1"].append(sample["bleu_rouge_bert_1_auto"]["bertscore_roberta"]["recall"][0])
            values["roberta_f1_auto_r1"].append(sample["bleu_rouge_bert_1_auto"]["bertscore_roberta"]["f1"][0])


            values["bleu_1_r2"].append(sample["bleu_rouge_bert_2_manual"]["bleu_1"]["bleu"])
            values["bleu_2_r2"].append(sample["bleu_rouge_bert_2_manual"]["bleu_2"]["bleu"])
            values["bleu_3_r2"].append(sample["bleu_rouge_bert_2_manual"]["bleu_3"]["bleu"])
            values["bleu_4_r2"].append(sample["bleu_rouge_bert_2_manual"]["bleu_4"]["bleu"])

            values["rouge_1_r2"].append(sample["bleu_rouge_bert_2_manual"]["rouge"]["rouge1"])
            values["rouge_2_r2"].append(sample["bleu_rouge_bert_2_manual"]["rouge"]["rouge2"])
            values["rouge_L_r2"].append(sample["bleu_rouge_bert_2_manual"]["rouge"]["rougeL"])
            values["rouge_Lsum_r2"].append(sample["bleu_rouge_bert_2_manual"]["rouge"]["rougeLsum"])

            values["bert_p_r2"].append(sample["bleu_rouge_bert_2_manual"]["bertscore_bert"]["precision"][0])
            values["bert_r_r2"].append(sample["bleu_rouge_bert_2_manual"]["bertscore_bert"]["recall"][0])
            values["bert_f1_r2"].append(sample["bleu_rouge_bert_2_manual"]["bertscore_bert"]["f1"][0])

            values["roberta_p_r2"].append(sample["bleu_rouge_bert_2_manual"]["bertscore_roberta"]["precision"][0])
            values["roberta_r_r2"].append(sample["bleu_rouge_bert_2_manual"]["bertscore_roberta"]["recall"][0])
            values["roberta_f1_r2"].append(sample["bleu_rouge_bert_2_manual"]["bertscore_roberta"]["f1"][0])


            values["bleu_1_auto_r2"].append(sample["bleu_rouge_bert_2_auto"]["bleu_1"]["bleu"])
            values["bleu_2_auto_r2"].append(sample["bleu_rouge_bert_2_auto"]["bleu_2"]["bleu"])
            values["bleu_3_auto_r2"].append(sample["bleu_rouge_bert_2_auto"]["bleu_3"]["bleu"])
            values["bleu_4_auto_r2"].append(sample["bleu_rouge_bert_2_auto"]["bleu_4"]["bleu"])

            values["rouge_1_auto_r2"].append(sample["bleu_rouge_bert_2_auto"]["rouge"]["rouge1"])
            values["rouge_2_auto_r2"].append(sample["bleu_rouge_bert_2_auto"]["rouge"]["rouge2"])
            values["rouge_L_auto_r2"].append(sample["bleu_rouge_bert_2_auto"]["rouge"]["rougeL"])
            values["rouge_Lsum_auto_r2"].append(sample["bleu_rouge_bert_2_auto"]["rouge"]["rougeLsum"])

            values["bert_p_auto_r2"].append(sample["bleu_rouge_bert_2_auto"]["bertscore_bert"]["precision"][0])
            values["bert_r_auto_r2"].append(sample["bleu_rouge_bert_2_auto"]["bertscore_bert"]["recall"][0])
            values["bert_f1_auto_r2"].append(sample["bleu_rouge_bert_2_auto"]["bertscore_bert"]["f1"][0])

            values["roberta_p_auto_r2"].append(sample["bleu_rouge_bert_2_auto"]["bertscore_roberta"]["precision"][0])
            values["roberta_r_auto_r2"].append(sample["bleu_rouge_bert_2_auto"]["bertscore_roberta"]["recall"][0])
            values["roberta_f1_auto_r2"].append(sample["bleu_rouge_bert_2_auto"]["bertscore_roberta"]["f1"][0])

        #otherwise add for one and the None for the other one
        else:

            values["prompt_time_r1"].append(sample["prompt_time"])
            values["prompt_time_r2"].append(None)

            values["bleu_1_r1"].append(sample["bleu_rouge_bert_manual"]["bleu_1"]["bleu"])
            values["bleu_2_r1"].append(sample["bleu_rouge_bert_manual"]["bleu_2"]["bleu"])
            values["bleu_3_r1"].append(sample["bleu_rouge_bert_manual"]["bleu_3"]["bleu"])
            values["bleu_4_r1"].append(sample["bleu_rouge_bert_manual"]["bleu_4"]["bleu"])

            values["rouge_1_r1"].append(sample["bleu_rouge_bert_manual"]["rouge"]["rouge1"])
            values["rouge_2_r1"].append(sample["bleu_rouge_bert_manual"]["rouge"]["rouge2"])
            values["rouge_L_r1"].append(sample["bleu_rouge_bert_manual"]["rouge"]["rougeL"])
            values["rouge_Lsum_r1"].append(sample["bleu_rouge_bert_manual"]["rouge"]["rougeLsum"])

            values["bert_p_r1"].append(sample["bleu_rouge_bert_manual"]["bertscore_bert"]["precision"][0])
            values["bert_r_r1"].append(sample["bleu_rouge_bert_manual"]["bertscore_bert"]["recall"][0])
            values["bert_f1_r1"].append(sample["bleu_rouge_bert_manual"]["bertscore_bert"]["f1"][0])

            values["roberta_p_r1"].append(sample["bleu_rouge_bert_manual"]["bertscore_roberta"]["precision"][0])
            values["roberta_r_r1"].append(sample["bleu_rouge_bert_manual"]["bertscore_roberta"]["recall"][0])
            values["roberta_f1_r1"].append(sample["bleu_rouge_bert_manual"]["bertscore_roberta"]["f1"][0])


            values["bleu_1_auto_r1"].append(sample["bleu_rouge_bert_auto"]["bleu_1"]["bleu"])
            values["bleu_2_auto_r1"].append(sample["bleu_rouge_bert_auto"]["bleu_2"]["bleu"])
            values["bleu_3_auto_r1"].append(sample["bleu_rouge_bert_auto"]["bleu_3"]["bleu"])
            values["bleu_4_auto_r1"].append(sample["bleu_rouge_bert_auto"]["bleu_4"]["bleu"])

            values["rouge_1_auto_r1"].append(sample["bleu_rouge_bert_auto"]["rouge"]["rouge1"])
            values["rouge_2_auto_r1"].append(sample["bleu_rouge_bert_auto"]["rouge"]["rouge2"])
            values["rouge_L_auto_r1"].append(sample["bleu_rouge_bert_auto"]["rouge"]["rougeL"])
            values["rouge_Lsum_auto_r1"].append(sample["bleu_rouge_bert_auto"]["rouge"]["rougeLsum"])

            values["bert_p_auto_r1"].append(sample["bleu_rouge_bert_auto"]["bertscore_bert"]["precision"][0])
            values["bert_r_auto_r1"].append(sample["bleu_rouge_bert_auto"]["bertscore_bert"]["recall"][0])
            values["bert_f1_auto_r1"].append(sample["bleu_rouge_bert_auto"]["bertscore_bert"]["f1"][0])

            values["roberta_p_auto_r1"].append(sample["bleu_rouge_bert_auto"]["bertscore_roberta"]["precision"][0])
            values["roberta_r_auto_r1"].append(sample["bleu_rouge_bert_auto"]["bertscore_roberta"]["recall"][0])
            values["roberta_f1_auto_r1"].append(sample["bleu_rouge_bert_auto"]["bertscore_roberta"]["f1"][0])


            values["bleu_1_r2"].append(None)
            values["bleu_2_r2"].append(None)
            values["bleu_3_r2"].append(None)
            values["bleu_4_r2"].append(None)

            values["rouge_1_r2"].append(None)
            values["rouge_2_r2"].append(None)
            values["rouge_L_r2"].append(None)
            values["rouge_Lsum_r2"].append(None)

            values["bert_p_r2"].append(None)
            values["bert_r_r2"].append(None)
            values["bert_f1_r2"].append(None)

            values["roberta_p_r2"].append(None)
            values["roberta_r_r2"].append(None)
            values["roberta_f1_r2"].append(None)


            values["bleu_1_auto_r2"].append(None)
            values["bleu_2_auto_r2"].append(None)
            values["bleu_3_auto_r2"].append(None)
            values["bleu_4_auto_r2"].append(None)

            values["rouge_1_auto_r2"].append(None)
            values["rouge_2_auto_r2"].append(None)
            values["rouge_L_auto_r2"].append(None)
            values["rouge_Lsum_auto_r2"].append(None)

            values["bert_p_auto_r2"].append(None)
            values["bert_r_auto_r2"].append(None)
            values["bert_f1_auto_r2"].append(None)

            values["roberta_p_auto_r2"].append(None)
            values["roberta_r_auto_r2"].append(None)
            values["roberta_f1_auto_r2"].append(None)

    #creates the dataframe and returns it
    df = pandas.DataFrame(values)

    return df

#for each score, this functions averages the values for r1 and r2 if this is task 2 and provides r1 if this is task 1 or task 3
def mean_for_t2(df_to_modify):

    df_to_modify["prompt_time"] = df_to_modify.apply(lambda row: row["prompt_time_r1"] if not row["task"] == "task-2" else
    (row["prompt_time_r1"] + row["prompt_time_r2"]) / 2, axis=1)

    df_to_modify["BLEU_1"] = df_to_modify.apply(lambda row: row["bleu_1_r1"] if not row["task"]=="task-2" else
    (row["bleu_1_r1"]+row["bleu_1_r2"])/2, axis=1)
    df_to_modify["BLEU_2"] = df_to_modify.apply(lambda row: row["bleu_2_r1"] if not row["task"] == "task-2" else
    (row["bleu_2_r1"] + row["bleu_2_r2"]) / 2, axis=1)
    df_to_modify["BLEU_3"] = df_to_modify.apply(lambda row: row["bleu_3_r1"] if not row["task"] == "task-2" else
    (row["bleu_3_r1"] + row["bleu_3_r2"]) / 2, axis=1)
    df_to_modify["BLEU_4"] = df_to_modify.apply(lambda row: row["bleu_4_r1"] if not row["task"] == "task-2" else
    (row["bleu_4_r1"] + row["bleu_4_r2"]) / 2, axis=1)

    df_to_modify["ROUGE_1"] = df_to_modify.apply(lambda row: row["rouge_1_r1"] if not row["task"]=="task-2" else
    (row["rouge_1_r1"]+row["rouge_1_r2"])/2, axis=1)
    df_to_modify["ROUGE_2"] = df_to_modify.apply(lambda row: row["rouge_2_r1"] if not row["task"] == "task-2" else
    (row["rouge_2_r1"] + row["rouge_2_r2"]) / 2, axis=1)
    df_to_modify["ROUGE_L"] = df_to_modify.apply(lambda row: row["rouge_L_r1"] if not row["task"] == "task-2" else
    (row["rouge_L_r1"] + row["rouge_L_r2"]) / 2, axis=1)
    df_to_modify["ROUGE_Lsum"] = df_to_modify.apply(lambda row: row["rouge_Lsum_r1"] if not row["task"] == "task-2" else
    (row["rouge_Lsum_r1"] + row["rouge_Lsum_r2"]) / 2, axis=1)

    df_to_modify["BERTscore_p"] = df_to_modify.apply(lambda row: row["bert_p_r1"] if not row["task"]=="task-2" else
    (row["bert_p_r1"]+row["bert_p_r2"])/2, axis=1)
    df_to_modify["BERTscore_r"] = df_to_modify.apply(lambda row: row["bert_r_r1"] if not row["task"] == "task-2" else
    (row["bert_r_r1"] + row["bert_r_r2"]) / 2, axis=1)
    df_to_modify["BERTscore_F1"] = df_to_modify.apply(lambda row: row["bert_f1_r1"] if not row["task"] == "task-2" else
    (row["bert_f1_r1"] + row["bert_f1_r2"]) / 2, axis=1)

    df_to_modify["RoBERTascore_p"] = df_to_modify.apply(lambda row: row["roberta_p_r1"] if not row["task"]=="task-2" else
    (row["roberta_p_r1"]+row["roberta_p_r2"])/2, axis=1)
    df_to_modify["RoBERTascore_r"] = df_to_modify.apply(lambda row: row["roberta_r_r1"] if not row["task"] == "task-2" else
    (row["roberta_r_r1"] + row["roberta_r_r2"]) / 2, axis=1)
    df_to_modify["RoBERTascore_F1"] = df_to_modify.apply(lambda row: row["roberta_f1_r1"] if not row["task"] == "task-2" else
    (row["roberta_f1_r1"] + row["roberta_f1_r2"]) / 2, axis=1)



    df_to_modify["BLEU_auto_1"] = df_to_modify.apply(lambda row: row["bleu_1_auto_r1"] if not row["task"] == "task-2" else
    (row["bleu_1_auto_r1"] + row["bleu_1_auto_r2"]) / 2, axis=1)
    df_to_modify["BLEU_auto_2"] = df_to_modify.apply(lambda row: row["bleu_2_auto_r1"] if not row["task"] == "task-2" else
    (row["bleu_2_auto_r1"] + row["bleu_2_auto_r2"]) / 2, axis=1)
    df_to_modify["BLEU_auto_3"] = df_to_modify.apply(lambda row: row["bleu_3_auto_r1"] if not row["task"] == "task-2" else
    (row["bleu_3_auto_r1"] + row["bleu_3_auto_r2"]) / 2, axis=1)
    df_to_modify["BLEU_auto_4"] = df_to_modify.apply(lambda row: row["bleu_4_auto_r1"] if not row["task"] == "task-2" else
    (row["bleu_4_auto_r1"] + row["bleu_4_auto_r2"]) / 2, axis=1)

    df_to_modify["ROUGE_auto_1"] = df_to_modify.apply(lambda row: row["rouge_1_auto_r1"] if not row["task"] == "task-2" else
    (row["rouge_1_auto_r1"] + row["rouge_1_auto_r2"]) / 2, axis=1)
    df_to_modify["ROUGE_auto_2"] = df_to_modify.apply(lambda row: row["rouge_2_auto_r1"] if not row["task"] == "task-2" else
    (row["rouge_2_auto_r1"] + row["rouge_2_auto_r2"]) / 2, axis=1)
    df_to_modify["ROUGE_auto_L"] = df_to_modify.apply(lambda row: row["rouge_L_auto_r1"] if not row["task"] == "task-2" else
    (row["rouge_L_auto_r1"] + row["rouge_L_auto_r2"]) / 2, axis=1)
    df_to_modify["ROUGE_auto_Lsum"] = df_to_modify.apply(lambda row: row["rouge_Lsum_auto_r1"] if not row["task"] == "task-2" else
    (row["rouge_Lsum_auto_r1"] + row["rouge_Lsum_auto_r2"]) / 2, axis=1)

    df_to_modify["BERTscore_auto_p"] = df_to_modify.apply(lambda row: row["bert_p_auto_r1"] if not row["task"] == "task-2" else
    (row["bert_p_auto_r1"] + row["bert_p_auto_r2"]) / 2, axis=1)
    df_to_modify["BERTscore_auto_r"] = df_to_modify.apply(lambda row: row["bert_r_auto_r1"] if not row["task"] == "task-2" else
    (row["bert_r_auto_r1"] + row["bert_r_auto_r2"]) / 2, axis=1)
    df_to_modify["BERTscore_auto_F1"] = df_to_modify.apply(lambda row: row["bert_f1_auto_r1"] if not row["task"] == "task-2" else
    (row["bert_f1_auto_r1"] + row["bert_f1_auto_r2"]) / 2, axis=1)

    df_to_modify["RoBERTascore_auto_p"] = df_to_modify.apply(lambda row: row["roberta_p_auto_r1"] if not row["task"] == "task-2" else
    (row["roberta_p_auto_r1"] + row["roberta_p_auto_r2"]) / 2, axis=1)
    df_to_modify["RoBERTascore_auto_r"] = df_to_modify.apply(lambda row: row["roberta_r_auto_r1"] if not row["task"] == "task-2" else
    (row["roberta_r_auto_r1"] + row["roberta_r_auto_r2"]) / 2, axis=1)
    df_to_modify["RoBERTascore_auto_F1"] = df_to_modify.apply(lambda row: row["roberta_f1_auto_r1"] if not row["task"] == "task-2" else
    (row["roberta_f1_auto_r1"] + row["roberta_f1_auto_r2"]) / 2, axis=1)

    #returns the dataframe with the new values
    return df_to_modify


def display_table_model_base(df_ft,df_base,sample,comparison,list_metrics,focus):

    #print information on what elements are compared in the plot
    focus_str = "-".join(focus)
    print("\n"*2 +
        "-" * 15 +
        f" Here are the {focus_str} results. Fine-tuned models were trained using {sample} samples, and the evaluation "
        f"was run against {comparison} expected output " +
        "-" * 15 +
        "\n"*2 )

    #copy the provided list of metrics
    new_list_metrics = copy.deepcopy(focus)
    new_list_metrics += list_metrics
    
    #used for info purpose
    for i in focus:
        print(set(df_ft[i]))
        print(set(df_base[i]))

    #creates the ft models df and aggregates the values present in focus(elements that are compared) by averaging them
    df_ft_model= df_ft[new_list_metrics].groupby(by=focus).mean()

    #same but for the base models
    df_base_model = df_base[new_list_metrics].groupby(by=focus).mean()

    print(df_base_model)

    print(df_ft_model)

    #concatenate the elements in one df and sort it according to the focus (elements compared)
    df_model = pandas.concat([df_ft_model, df_base_model], sort=False).sort_values(focus)

    #change the column name
    df_model["runtime (min)"] = df_model.apply(lambda row: row["prompt_time"]/60.0, axis=1)
    df_model = df_model.drop("prompt_time", axis=1)


    #prepare the plot
    fs=22
    plt.figure(figsize=(16, 8))
    ax = sns.heatmap(df_model, fmt=".3f", annot=True, annot_kws={"size": fs}, cmap='Blues', xticklabels=True, yticklabels=df_model.index)
    ax.spines['left'].set_visible(False)
    ax.xaxis.set_ticks_position('top')  # Move x-axis labels to the top
    ax.tick_params(top=True, bottom=False)  # Disable bottom ticks
    plt.xticks(rotation=45, ha='left', fontsize=fs)
    plt.yticks(fontsize=fs)# Rotate labels if needed for clarity

    # Adjust the layout to add more space at the top (increase padding)
    plt.tight_layout(rect=[0, 0, 1, 1])  # Adjust the rect parameter to give more space

    #save the figure
    plt.savefig(f'./plots_blue/heatmap_{focus_str}_{sample}_{comparison}.png', dpi=300, bbox_inches='tight')  # Save with high resolution (dpi=300)

    plt.close()

    #print in the console as well
    print(tabulate(df_model, headers='keys', tablefmt='psql'))

    return df_model

def display_table_model(df_ft,df_base,sample,comparison,list_metrics,focus,new_index):

    #print information on what elements are compared in the plot
    print("\n"*2 +
        "-" * 15 +
        f" Here are the {focus} results. Fine-tuned models were trained using {sample} samples, and the evaluation was run against {comparison} expected output " +
        "-" * 15 +
        "\n"*2 )

    #creates two lists, this time fit and based are treated differently (because the element in the focus is not part of the base for example nb samples or config or loss)
    #therefore the base models will just show BASE and the rest te elements analyzed (nb samples or config or loss)
    new_list_metrics = [focus]
    new_list_metrics_base = ["type_model"]
    new_list_metrics += list_metrics
    new_list_metrics_base += list_metrics

    print(set(df_base["type_model"]))

    print(set(df_ft[focus]))
    
    
    #creates the ft models df and aggregates the values present in focus(elements that is compared, nb samples or config or loss) by averaging them
    df_model= df_ft[new_list_metrics].groupby(by=[focus]).mean()

    #same but here the focus is just the type_model (BASE)
    df_base = df_base[new_list_metrics_base].groupby(by=["type_model"]).mean()

    print(df_base)

    print(df_model)
    
    #values are sorted
    df_model = df_model.sort_values(focus)

    #base is added to the df
    df_model_base = pandas.concat([df_model, df_base], sort=False)

    #index is recreated based on the provided index (generated by hand each time)
    df_model_base = df_model_base.reindex(index=new_index)

    #column name is changed
    df_model_base["runtime (min)"] = df_model_base.apply(lambda row: row["prompt_time"] / 60.0, axis=1)
    df_model_base = df_model_base.drop("prompt_time", axis=1)

    #plot is prepared
    fs = 18

    plt.figure(figsize=(16, 8))
    #plt.suptitle(f" Here are the {focus} results.\nFine-tuned models were trained using {sample} samples.\nThe "
    #             f"evaluation was run against {comparison} expected output", y=-0.05)
    ax = sns.heatmap(df_model_base, annot=True, annot_kws={"size": fs}, fmt=".3f", cmap='Blues', xticklabels=True, yticklabels=new_index)
    ax.spines['left'].set_visible(False)
    ax.xaxis.set_ticks_position('top')  # Move x-axis labels to the top
    ax.tick_params(top=True, bottom=False)  # Disable bottom ticks
    plt.xticks(rotation=45, ha='left',fontsize=fs)  # Rotate labels if needed for clarity
    plt.yticks(fontsize=fs, rotation=0)
    # Adjust the layout to add more space at the top (increase padding)
    plt.tight_layout(rect=[0, 0, 1, 1])  # Adjust the rect parameter to give more space

    #save the plot
    plt.savefig(f'./plots_blue/heatmap_{focus}_{sample}_{comparison}.png', dpi=300,
                bbox_inches='tight')  # Save with high resolution (dpi=300)

    plt.close()

    #print the plot
    print(tabulate(df_model_base, headers='keys', tablefmt='psql'))

    return df_model_base


def main():
    #create dataframe for the fine.tuned models, also saves the dataset
    input_ft = "./data_with_evaluation/brb/brb_eval.json"
    output_ft = "./dataframes/complete/data_ft.csv"
    df_ft = create_dataframe(input_ft,False)
    df_ft.to_csv(output_ft)

    #same for the base models
    input_base = "./data_with_evaluation/brb/brb_eval_base.json"
    output_base = "./dataframes/complete/data_base.csv"
    df_base = create_dataframe(input_base,True)
    df_base.to_csv(output_base)


    #selection of the metrics of interest (more were computed but this is the list we use for our analysis
    #there is a list when compared against manual reference summaries and one when compared against auto reference summaries
    l_metrics_manual = ["BLEU_1", "BLEU_2", "BERTscore_F1", "RoBERTascore_F1", "ROUGE_1", "ROUGE_2", "ROUGE_L","prompt_time"]

    l_metrics_auto = ["BLEU_auto_1", "BLEU_auto_2", "BERTscore_auto_F1", "RoBERTascore_auto_F1",
                      "ROUGE_auto_1", "ROUGE_auto_2", "ROUGE_auto_L", "prompt_time"]

    #computes the mean for the two results for task-2
    df_ft = mean_for_t2(df_ft)
    df_base = mean_for_t2(df_base)


    #note that when generating the plots, each time 6 plots are generated:
    
    #all_manual were results from all models were compared against manually generated references
    #all_auto were results from all models were compared against automatically generated references
    #manual_manual were results from models fine-tuned using manual summaries were compared against manually generated references
    #auto_manual were results from models fine-tuned using automatic summaries were compared against manually generated references
    #manual_auto were results from models fine-tuned using manual summaries were compared against automatically generated references
    #auto_auto were results from models fine-tuned using automatic summaries were compared against automatically generated references
    
    #note that except for the one analyzing the loss compuation, only the one with loss computed on completion only are kept
    

    ### Model ###

    #compares the base models (and the model type ft vs base)
    display_table_model_base(df_ft[df_ft.loss_computation == "completion"], df_base, "all", "manual", l_metrics_manual, ["base_model","type_model"])
    display_table_model_base(df_ft[df_ft.loss_computation == "completion"], df_base, "all", "automatic", l_metrics_auto, ["base_model","type_model"])

    display_table_model_base(df_ft[(df_ft.sample_type == "automatic") & (df_ft.loss_computation == "completion")], df_base[df_base.sample_type == "automatic"], "automatic",
                  "automatic", l_metrics_auto, ["base_model","type_model"])
    display_table_model_base(df_ft[(df_ft.sample_type == "manual") & (df_ft.loss_computation == "completion")], df_base[df_base.sample_type == "manual"], "manual", "automatic",
                  l_metrics_auto, ["base_model","type_model"])

    display_table_model_base(df_ft[(df_ft.sample_type == "automatic") & (df_ft.loss_computation == "completion")], df_base[df_base.sample_type == "automatic"], "automatic",
                  "manual", l_metrics_manual, ["base_model","type_model"])
    display_table_model_base(df_ft[(df_ft.sample_type=="manual") & (df_ft.loss_computation == "completion")],df_base[df_base.sample_type=="manual"],"manual","manual",
                  l_metrics_manual,["base_model","type_model"])

    # ### Task with model ###

    # compares the tasks and base models (and the model type ft vs base)
    display_table_model_base(df_ft[df_ft.loss_computation == "completion"], df_base, "all", "manual", l_metrics_manual, ["base_model", "task", "type_model"])
    display_table_model_base(df_ft[df_ft.loss_computation == "completion"], df_base, "all", "automatic", l_metrics_auto, ["base_model", "task", "type_model"])

    display_table_model_base(df_ft[(df_ft.sample_type == "automatic") & (df_ft.loss_computation == "completion")], df_base[df_base.sample_type == "automatic"], "automatic",
                  "automatic", l_metrics_auto, ["base_model", "task", "type_model"])
    display_table_model_base(df_ft[(df_ft.sample_type=="manual") & (df_ft.loss_computation == "completion")], df_base[df_base.sample_type == "manual"], "manual", "automatic",
                  l_metrics_auto, ["base_model", "task", "type_model"])

    display_table_model_base(df_ft[(df_ft.sample_type == "automatic") & (df_ft.loss_computation == "completion")], df_base[df_base.sample_type == "automatic"], "automatic",
                  "manual", l_metrics_manual, ["base_model", "task", "type_model"])
    display_table_model_base(df_ft[(df_ft.sample_type=="manual") & (df_ft.loss_computation == "completion")],df_base[df_base.sample_type=="manual"],"manual","manual",
                  l_metrics_manual,["base_model", "task", "type_model"])

    # ### tasks_only ###

    # compares the tasks (and the model type ft vs base)
    display_table_model_base(df_ft[df_ft.loss_computation == "completion"], df_base, "all", "manual", l_metrics_manual,
                             ["task", "type_model"])
    display_table_model_base(df_ft[df_ft.loss_computation == "completion"], df_base, "all", "automatic", l_metrics_auto,
                             ["task", "type_model"])

    display_table_model_base(df_ft[(df_ft.sample_type == "automatic") & (df_ft.loss_computation == "completion")],
                             df_base[df_base.sample_type == "automatic"], "automatic",
                             "automatic", l_metrics_auto, ["task", "type_model"])
    display_table_model_base(df_ft[(df_ft.sample_type == "manual") & (df_ft.loss_computation == "completion")],
                             df_base[df_base.sample_type == "manual"], "manual", "automatic",
                             l_metrics_auto, ["task", "type_model"])

    display_table_model_base(df_ft[(df_ft.sample_type == "automatic") & (df_ft.loss_computation == "completion")],
                             df_base[df_base.sample_type == "automatic"], "automatic",
                             "manual", l_metrics_manual, ["task", "type_model"])
    display_table_model_base(df_ft[(df_ft.sample_type == "manual") & (df_ft.loss_computation == "completion")],
                             df_base[df_base.sample_type == "manual"], "manual", "manual",
                             l_metrics_manual, ["task", "type_model"])


    # ### nb_samples ###

    # compares the nb of samples used during fine tuning (and the base model)
    display_table_model(df_ft[df_ft.loss_computation == "completion"], df_base, "all", "manual", l_metrics_manual, "nb_samples",["BASE","60-samples","120-samples","180-samples"])
    display_table_model(df_ft[df_ft.loss_computation == "completion"], df_base,"all", "automatic", l_metrics_auto, "nb_samples",["BASE","60-samples","120-samples","180-samples"])

    display_table_model(df_ft[(df_ft.sample_type == "automatic") & (df_ft.loss_computation == "completion")],df_base[df_base.sample_type == "automatic"], "automatic",
                  "automatic", l_metrics_auto, "nb_samples",["BASE","60-samples","120-samples","180-samples"])
    display_table_model(df_ft[(df_ft.sample_type=="manual") & (df_ft.loss_computation == "completion")],df_base[df_base.sample_type == "manual"], "manual", "automatic",
                  l_metrics_auto, "nb_samples",["BASE","60-samples","120-samples","180-samples"])

    display_table_model(df_ft[(df_ft.sample_type == "automatic") & (df_ft.loss_computation == "completion")],df_base[df_base.sample_type == "automatic"], "automatic",
                  "manual", l_metrics_manual, "nb_samples",["BASE","60-samples","120-samples","180-samples"])
    display_table_model(df_ft[(df_ft.sample_type=="manual") & (df_ft.loss_computation == "completion")],df_base[df_base.sample_type == "manual"],"manual","manual",
                  l_metrics_manual,"nb_samples",["BASE","60-samples","120-samples","180-samples"])

    # ### loss ###

    # compares the loss computation used during fine tuning (and the base model)
    display_table_model(df_ft, df_base,"all", "manual", l_metrics_manual, "loss_computation",["BASE","completion","full"])
    display_table_model(df_ft, df_base,"all", "automatic", l_metrics_auto, "loss_computation",["BASE","completion","full"])

    display_table_model(df_ft[df_ft.sample_type == "automatic"],df_base[df_base.sample_type == "automatic"], "automatic",
                  "automatic", l_metrics_auto, "loss_computation",["BASE","completion","full"])
    display_table_model(df_ft[df_ft.sample_type=="manual"],df_base[df_base.sample_type == "manual"], "manual", "automatic",
                  l_metrics_auto, "loss_computation",["BASE","completion","full"])

    display_table_model(df_ft[df_ft.sample_type == "automatic"],df_base[df_base.sample_type == "automatic"], "automatic",
                  "manual", l_metrics_manual, "loss_computation",["BASE","completion","full"])
    display_table_model(df_ft[df_ft.sample_type=="manual"],df_base[df_base.sample_type == "manual"],"manual","manual",
                  l_metrics_manual,"loss_computation",["BASE","completion","full"])

    # ### config ###

    # compares the configuration used during fine tuning (and the base model)
    display_table_model(df_ft[df_ft.loss_computation == "completion"], df_base,"all", "manual", l_metrics_manual, "config",["BASE","config-1","config-2"])
    display_table_model(df_ft[df_ft.loss_computation == "completion"], df_base,"all", "automatic", l_metrics_auto, "config",["BASE","config-1","config-2"])
    #
    display_table_model(df_ft[(df_ft.sample_type == "automatic") & (df_ft.loss_computation == "completion")],df_base[df_base.sample_type == "automatic"], "automatic",
                  "automatic", l_metrics_auto, "config",["BASE","config-1","config-2"])
    display_table_model(df_ft[(df_ft.sample_type=="manual") & (df_ft.loss_computation == "completion")],df_base[df_base.sample_type == "manual"], "manual", "automatic",
                  l_metrics_auto, "config",["BASE","config-1","config-2"])

    display_table_model(df_ft[(df_ft.sample_type == "automatic") & (df_ft.loss_computation == "completion")],df_base[df_base.sample_type == "automatic"], "automatic",
                  "manual", l_metrics_manual, "config",["BASE","config-1","config-2"])
    display_table_model(df_ft[(df_ft.sample_type=="manual") & (df_ft.loss_computation == "completion")],df_base[df_base.sample_type == "manual"],"manual","manual",
                  l_metrics_manual,"config",["BASE","config-1","config-2"])


if __name__ == '__main__':
    main()