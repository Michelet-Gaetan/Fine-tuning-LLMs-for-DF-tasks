import evaluate
import json
from datetime import datetime
import bert_score
import torch

#takes the different evaluators, s prediction and a reference and compute the score
def compute_bleu_rouge_bertscore(bleu, rouge, bertscore, reference, prediction):
    bert = bertscore.compute(predictions=[prediction], references=[reference], lang="en",
                             model_type="bert-large-uncased")
    roberta = bertscore.compute(predictions=[prediction], references=[reference], lang="en")

    bleu_1 = bleu.compute(predictions=[prediction], references=[reference], max_order=1)
    bleu_2 = bleu.compute(predictions=[prediction], references=[reference], max_order=2)
    bleu_3 = bleu.compute(predictions=[prediction], references=[reference], max_order=3)
    bleu_4 = bleu.compute(predictions=[prediction], references=[reference], max_order=4)
    rouge_all = rouge.compute(predictions=[prediction], references=[reference])

    #return all the scores computed
    return {"bertscore_bert": bert, "bertscore_roberta": roberta, "bleu_1": bleu_1, "bleu_2": bleu_2, "bleu_3": bleu_3,
            "bleu_4": bleu_4, "rouge": rouge_all}

#helps to load data from json files
def load_json(file_path):
    with open(file_path, "r") as file:
        dataset = json.load(file)

    return dataset

#helps to save data to json files
def dump_json(dataset, file_path):
    with open(file_path, "w") as file:
        json.dump(dataset, file,indent=5)

    return 0

#for each sample in a file, computes the evaluation (against manual and ato reference summaries)
#a checkpointing system is implemented, saving the current state each 100 samples
#note that everything went smooth and the everything was done in 1 run (for output and 1 run for output_base)
def eval_file_checkpoint_ez(input,output,num=100,start=0):
    complete_json = []
    #load the dataset
    json_input = load_json(file_path=input)
    counter = start

    #here there is an existing checkpoint tat must be loaded
    if start!=0:
        complete_json = load_json(output)

    #time taken for information
    t1 = datetime.now()
    print(f'samples to be dealt with:{str(len(json_input))}')
    #if start is different start from there otherwise start from 0
    #loop on all the samples
    for sample in json_input[start:]:
        #if the current sample is 100, 200, ... save the current state of the dataset
        if (counter)%num==0:
            offset = (counter)//num
            output_new = output.replace(output.split("/")[-1],
                                               f'{output.split("/")[-1].strip(".json")}_{str(offset)}.json')
            print(f'saving with counter:{str(counter)}')
            dump_json(complete_json,output_new)

        #in any case run the evaluation on the sample
        print(f'counter:{str(counter)}')
        complete_json.append(eval_sample(sample))
        counter += 1
    
    #when finished, save the dataset
    dump_json(complete_json,output)

    t2 = datetime.now()
    print((t2-t1).total_seconds())
    return 0

#given a sample, computes all the scores and return the result
def eval_sample(sample):
    #load the evaluators
    bleu = evaluate.load("bleu")
    rouge = evaluate.load("rouge")
    bertscore = evaluate.load("bertscore")

    #copy the sample
    new_sample = sample
    #if task 2, two  auto and two manual references are present (also the field name changes)
    if sample["task"]=="task-2":
        #compare the prediction 1 against auto reference 1
        reference = sample["expected_result_1_auto"]
        prediction = sample["result_1"]
        new_sample["bleu_rouge_bert_1_auto"]=compute_bleu_rouge_bertscore(bleu, rouge, bertscore, reference, prediction)

        #compare the prediction 2 against auto reference 2
        reference = sample["expected_result_2_auto"]
        prediction = sample["result_2"]
        new_sample["bleu_rouge_bert_2_auto"]=compute_bleu_rouge_bertscore(bleu, rouge, bertscore, reference, prediction)

        #compare the prediction 1 against manual reference 1
        reference = sample["expected_result_1_manual"]
        prediction = sample["result_1"]
        new_sample["bleu_rouge_bert_1_manual"]=compute_bleu_rouge_bertscore(bleu, rouge, bertscore, reference, prediction)

        #compare the prediction 2 against manual reference 2
        reference = sample["expected_result_2_manual"]
        prediction = sample["result_2"]
        new_sample["bleu_rouge_bert_2_manual"]=compute_bleu_rouge_bertscore(bleu, rouge, bertscore, reference, prediction)
    else:
        #compare the prediction against auto reference 
        reference = sample["expected_result_auto"]
        prediction = sample["result"]
        new_sample["bleu_rouge_bert_auto"]=compute_bleu_rouge_bertscore(bleu, rouge, bertscore, reference, prediction)

        #compare the prediction against auto reference 
        reference = sample["expected_result_manual"]
        prediction = sample["result"]
        new_sample["bleu_rouge_bert_manual"]=compute_bleu_rouge_bertscore(bleu, rouge, bertscore, reference, prediction)

    return new_sample


def main():
    #load the input and output paths (must be done for output and output_base)
    input = "./data_filtered_organized/filtered/output.json"
    output = "./data_with_evaluation/brb/brb_eval.json"

    #run the evaluation
    eval_file_checkpoint_ez(input,output)

if __name__ == "__main__":
    main()