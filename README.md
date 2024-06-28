# Formulate-and-Solve

This is the official implementation of `Solving for X and Beyond: Can Large Language Models Solve Complex
Math Problems with More-Than-Two Unknowns?`.

## About Formulate-and-Solve

<div align="center">
<img src="docs/static/images/mwp_solver.png">
</div>

## Installation
Make sure you have Python>=3.10 installed on your machine.
```
pip install -r requirements.txt
```

## Set your OpenAI and Gemini API key
```
export OPENAI_API_KEY=(YOUR OPENAI API KEY)
export GEMINI_API_KEY=(YOUR GEMINI API KEY)
```

## Quick Start

### BeyondX Dataset Construction
```
# dataset_name = {"alg514", "draw1k", "BeyondX_3", "BeyondX_4"}
bash scripts/create_dataset.sh ${dataset_name}
```

### Formulate-and-Solve
```
# model_name = {"gpt3", "gpt4", "gemini", "deepseek", "llama2", "llama3", "llama3-instruct",
 "mistral", "xwin", "abel", "metamath", "wizard", "arithmo2", "mmiqc",
 "mammoth", "mammoth2", "openmath"}
# dataset_name = {"gsm8k", "addsub", "multiarith", "svamp", "singleeq", "alg514", "draw1k",
 "hmwp", "asdiv", "BeyondX_3", "BeyondX_4", "BeyondX_5"}
bash scripts/run.sh ${model_name} ${dataset_name}
```
