import json
import os
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

model2name = {
    'bert_large':'BERT-Large',
    'pubmed_bert': 'PubMedBERT',
    'bart_large':'BART-Large',
    'flan_t5_large': 'Flan-T5-Large',
    'bloom_1b7': 'BLOOM-1b7',
    'flan_t5_xl': 'Flan-T5-XL',
    'bloom_3b': 'BLOOM-3b',
    'llama_7b':'LLaMA-7B',
    'gpt3':'GPT-3',
    'chatgpt': 'GPT-3.5',
    # 'gpt4': 'GPT-4',
    'umls_flan_t5_large':'Flan-T5-Large*',
    'umls_flan_t5_xl': 'Flan-T5-XL*',
    'schemaorg_flan_t5_large': 'Flan-T5-Large*',
    'schemaorg_flan_t5_xl': 'Flan-T5-XL*',
    'geonames_flan_t5_large': 'Flan-T5-Large*',
    'geonames_flan_t5_xl':  'Flan-T5-XL*',
    'wn18rr_flan_t5_large':'Flan-T5-Large*',
    'wn18rr_flan_t5_xl':'Flan-T5-XL*',
}

dir2name = {
    'wn18rr': 'WN18RR',
    'geonames': 'GeoNames',
    'nci': 'NCI',
    'snomedct_us': 'SNOMEDCT',
    'medcin':'Medcin',
    'umls': 'UMLS',
    'schema': 'Schema.Org'
}

medical_dir2name = {
    'nci': 'NCI',
    'snomedct_us': 'SNOMEDCT',
    'medcin':'Medcin',
    'umls': 'UMLS',
}
tasks = ['A', 'B', 'C']

task_templates_name = {
    "A": [f'template-{str(index)}' for index in range(1, 9)],
    "B": [f'-{str(index)}-' for index in range(1, 9)],
    "C": [""]
}


def read_json(path: str):
    """
    Reads the ``json`` file of the given ``input_path``.

    :param input_path: Path to the json file
    :return: A loaded json object.
    """
    with open(path, encoding="utf-8") as f:
        json_data = json.load(f)
    return json_data

def rounding(score):
    return round(score+0.5)


report_catalog = {}
for task in tasks:
    report_catalog[task] = {}
    root_task_dir = f"Task{task}/results/"
    for dataset in dir2name.keys():
        if dataset in os.listdir(root_task_dir):
            report_catalog[task][dataset] = {}
            print(dir2name[dataset])
            dataset_dir_path = os.path.join(root_task_dir, dataset)
            for model_output_dir in os.listdir(dataset_dir_path):
                model_output_dir_path = os.path.join(dataset_dir_path, model_output_dir)
                if os.path.isdir(model_output_dir_path) and not '.ipynb_checkpoints' in model_output_dir_path:
                    prefix = f"report-{model_output_dir}"
                    results = []
                    for template in task_templates_name[task]:
                        for file in os.listdir(model_output_dir_path):
                            if file.startswith(prefix) and template in file:
                                json_file = read_json(path=os.path.join(model_output_dir_path, file))
                                if task == 'A':
                                    score = json_file['results']['MAP@1'] * 100
                                    results.append(score)
                                elif task == 'B':
                                    score = json_file['results']['clf-report-dict']['macro avg']['f1-score'] * 100
                                    results.append(score)
                                elif task == 'C':
                                    score = json_file['results']['clf-report']['macro avg']['f1-score'] * 100
                                    results.append(score)
                                break
                    report_catalog[task][dataset][model_output_dir] = results



markers_dict = {
    "WN18RR":"square",
    "UMLS": "star",
    "GeoNames": "circle",
    "Schema.Org": "diamond-tall",
    "NCI": "star",
    "SNOMEDCT": "star",
    "Medcin":"star"
}

colors_dict = {
    "WN18RR":"orange",
    "UMLS": "blue",
    "GeoNames": "green",
    "Schema.Org": "red",
    "NCI": "blue",
    "SNOMEDCT": "#1f77b4",
    "Medcin":"#17becf"
}
llm_no = 12

fig = go.Figure()
categories = list(model2name.values())[:llm_no]

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task A
# ----------------------------------------------------------------------------------------------------------------------------------------------
#####################################################################################################################
task = 'A'
df_file_name = 'task_a_radar.csv'
results_matrix = []
colors = ["orange", "gray", "purple", "blue", "green"]
dataset_names = []

for index, dataset in enumerate(report_catalog[task].keys()):
    dataset_names.append(dir2name[dataset])
    results = []
    for model in model2name.keys():
        for report, results_score in report_catalog[task][dataset].items():
            if model == report:
                if model == 'pubmed_bert' and dataset in ['umls', 'nci', 'medcin', 'snomedct_us']:
                    results.append(rounding(max(results_score)))
                elif model != 'pubmed_bert':
                    results.append(rounding(max(results_score)))
        if model == 'pubmed_bert' and dataset not in ['umls', 'nci', 'medcin', 'snomedct_us']:
            results.append(0)
    results_matrix.append(results)


for i in range(0, 5):
    dot_opacity = np.ones(len(results_matrix[i]))
    if list(report_catalog[task].keys())[i] in ['umls', 'nci', 'medcin', 'snomedct_us']:
        dot_opacity[1] = 1
    else:
        dot_opacity[1] = 0
    fig.add_trace(go.Scatter(
        x=categories,
        y=results_matrix[i],
        name="Task A: " + dataset_names[i],
        line_color=colors_dict[dataset_names[i]],
        mode='markers',
        marker=dict(
            size=12, symbol=markers_dict[dataset_names[i]] + "-open", opacity=dot_opacity
        )
    ))

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task B
# ----------------------------------------------------------------------------------------------------------------------------------------------
#####################################################################################################################
task = 'B'
df_file_name = 'task_a_radar.csv'
results_matrix = []
colors = ["gray", "blue", "red"]
dataset_names = []

for index, dataset in enumerate(report_catalog[task].keys()):
    dataset_names.append(dir2name[dataset])
    results = []
    for model in model2name.keys():
        for report, results_score in report_catalog[task][dataset].items():
            if model == report:
                if model == 'pubmed_bert' and dataset in ['umls', 'nci', 'medcin', 'snomedct_us']:
                    results.append(rounding(max(results_score)))
                elif model != 'pubmed_bert':
                    results.append(rounding(max(results_score)))
        if model == 'pubmed_bert' and dataset not in ['umls', 'nci', 'medcin', 'snomedct_us']:
            results.append(0)
    results_matrix.append(results)


for i in range(0, 3):
    dot_opacity = np.ones(len(results_matrix[i]))
    if list(report_catalog[task].keys())[i] in ['umls', 'nci', 'medcin', 'snomedct_us']:
        dot_opacity[1] = 1
    else:
        dot_opacity[1] = 0
    fig.add_trace(go.Scatter(
        x=categories,
        y=results_matrix[i],
        name="Task B: " + dataset_names[i],
        line_color=colors_dict[dataset_names[i]],
        mode='markers',
        marker=dict(
            size=12, symbol=markers_dict[dataset_names[i]], opacity=dot_opacity
        )
    ))

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task C
# ----------------------------------------------------------------------------------------------------------------------------------------------
#####################################################################################################################
task = 'C'
df_file_name = 'task_a_radar.csv'
results_matrix = []
colors = ["blue"]
dataset_names = []

for index, dataset in enumerate(report_catalog[task].keys()):
    dataset_names.append(dir2name[dataset])
    results = []
    for model in model2name.keys():
        for report, results_score in report_catalog[task][dataset].items():
            if model == report:
                results.append(rounding(max(results_score)))
    results_matrix.append(results)



for i in range(0, 1):
    dot_opacity = np.ones(len(results_matrix[i]))
    if list(report_catalog[task].keys())[i] in ['umls', 'nci', 'medcin', 'snomedct_us']:
        dot_opacity[1] = 1
    else:
        dot_opacity[1] = 0
    fig.add_trace(go.Scatter(
        x=categories,
        y=results_matrix[i],
        name="Task C: " + dataset_names[i],
        line_color=colors_dict[dataset_names[i]],
        mode='markers',
        marker=dict(
            size=5, symbol=markers_dict[dataset_names[i]] + "-open-dot", opacity=dot_opacity
        )
    ))

#####################################################################################################################
width = 1280
height = 400

fig.update_layout(title=None,
                  # scattermode="group",
                  width=width,
                  height=height,
                  legend=dict(
                      orientation="h",
                      y=1,
                      x=0,
                      yanchor='bottom',
                      xanchor="left"
                  ),
                  margin=dict(l=20, r=20, t=20, b=20)
                  )
fig.update_yaxes(tick0=0, dtick=10)
fig.show()


fig.write_image("images/results-figure.pdf",
                width=width,
                height=height)
fig.write_image("images/results-figure.jpeg",
                width=width,
                height=height)
