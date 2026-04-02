# Towards-LLM-based-Detection-of-Gaming-a-Generative-Tutor
Files, logs and scripts concerning the research paper Towards LLM-based Detection of Gaming a Generative Tutor

1. Logs: Contains the 780 synthetically generated logs. The initial number indicates the scenario (01 = Polite), the second number indicates strategy (.1. = always final), the final number is an ascending order of the number of times that combination was generated (each scenario and strategy combination was generated 5 times. The final letter _A, _B or _C indicates which assignment the log concerns.

Include full list of scenario, strategy and assignment codes

2. Synthetic Prompts: Text files of all the scenarios and strategies that were used to prompt Gemini to act as student for the purpose of the synthetic log generation. Subdivided as a folder structure based on strategies and scenarios.

3. Outer Loop

In this folder are all the files and instructions used for the post-task analysis. There are 1 and 2 labelled files to create two parallel pipelines for analysis. Outer Loop1 and 2 text files contain the instructions for the analysis. Claude_loop1 and 2 contain the script and further AI instructions for automatically analysing each log in sequence. This process creates Run1.csv and Run1_reasoning.csv. Run1.csv cleaned manually, and then sorted by sort_classifications.py. It is then compared to Outer Loop Truth.csv with compare_outer_loop_by_suffix.py to create the Category_Reports_Processed folder with text files containing all the various results of the analysis.
