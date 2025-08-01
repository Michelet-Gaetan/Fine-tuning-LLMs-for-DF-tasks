Evaluation
==========
First, a few checks were run to make sure everything was correctly executed in the previous part and make sure some conditions for the reference exchange were met.

We then gathered the json together for the base and fine_tuned models. We also added for each sample the automatically and manually generated expected output (or reference). This was done as the samples existed in two version, the auto and manual one with respectively the auto and manual reference. As they have the same common elements (model and task for base / model, task, nb samples, config, loss for fine-tuned) and prompts, it was possible to group them and share the reference to the other one (auto from auto was provided to manual and manual from manual was provided to auto). It was also simplified as the sample order is the same between the files so we just had to check that they really matched and did the exchange.

Then, evaluation using the metrics of our choice was run on each sample, comparing the result against the manual and automatic reference (useful for the results obtained).

Finally, the data was grouped and specific visualizations were created.

# Checks (./creation/check_before_going_further.py)

In this script, different tests were run to control that everything is ready for the evaluation.

Results from elements generated in the output_check series were compared against the actual data. If they corresponded, the model generated the same result based on the same prompt which confirms that sampling was decativated.

When comparing two datasets where only the model or the sample_type varied, it was also checked that the samples 0 from each file had the same prompt, then that the sample 1 from each file had the same prompt, etc

The same was done when comparing base models and fine-tuned models. This time the fine-tuned model file was bigger and when the base model was finished it started again until all samples fromthe fine-tuned one were compared.

Finally another pass was done with the sample_type varying and this time the prompt was compared as well as other identifiers (except sample_type).

In the end all the checks were done and it was rwady to go further.

# Combining and completing the json (./creation/combine_and_filter.py)

In this script, the json are first grouped based on ther belonging to the four following groups: base_auto, base_manual, fine-tuned_auto, fine-tuned_manual. Note that the order of the samples between base_auto and base_manual is the same (except that one has the auto reference and the other one the manual reference). The same applies for fine-tuned.

Then, the manual and auto datasets are processed together. For each sample in auto, the sample in the same position in manual is used. There is a check to make sure they have the same prompts and identifiers (except for the sample_type). If everything is ok, the auto reference summary from the auto sample is provided to the manual sample and vice versa. In the end, each sample has both the auto and manual reference summary.

Finally, some renamed and others are filtered to simplify the next step.

The files here are compressed due to github limitations but are not in the project.

# Evaluating (./creation/evaluation.py)

For each sample in the dataset, the scores are computed. This is done for the fine-tuned models (output) and base models (output_base).

For each samples, all the scores are computed between the result (prediction) and both the auto and manual expected output (reference summaries/reference).

The score is then stored for each sample, and the result is stored for analysis and visualization.

The files here are compressed due to github limitations but are not in the project.

# Analysis (./analysis_and_visualization.py)

Here analysis will be run. First dataframes are created, then data are aggregated for task 2 (mean of the scores for the two steps), and finally visualizations aggregating different elements are generated to visualize the reuslts.

First, the dataframes are created by looping over each sample and getting the values. Note that when this is a base models and elements are not present (config, loss...) it is filled with None. Same for the scores relating to result 2 with task 1 and task 3. The model_type (base or fine-tuned) is also stored.

Then, results are averaged for task 2 (where 2 elements were generated).

Then plots are generated by filtering on the elements of interest and comparing them. Aggregations are always the average.Each plot is generated in 6 versions: all_manual were results from all models were compared against manually generated references, all_auto were results from all models were compared against automatically generated references, manual_manual were results from models fine-tuned using manual summaries were compared against manually generated references, auto_manual were results from models fine-tuned using automatic summaries were compared against manually generated references, manual_auto were results from models fine-tuned using manual summaries were compared against automatically generated references, auto_auto were results from models fine-tuned using automatic summaries were compared against automatically generated references

# Data (./data/)

The generated dataframes and plots are available. For each type of plot generated, 6 versions are provided: all_manual were results from all models were compared against manually generated references, all_auto were results from all models were compared against automatically generated references, manual_manual were results from models fine-tuned using manual summaries were compared against manually generated references, auto_manual were results from models fine-tuned using automatic summaries were compared against manually generated references, manual_auto were results from models fine-tuned using manual summaries were compared against automatically generated references, auto_auto were results from models fine-tuned using automatic summaries were compared against automatically generated references
