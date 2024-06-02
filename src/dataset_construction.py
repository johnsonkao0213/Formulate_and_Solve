import os
import re
import json
import time
import openai
import argparse
from retry import retry
from sympy import sympify
from prompts.beyondx import THREE_UNKNOWN, FOUR_UNKNOWN, FIVE_UNKNOWN
from utils.utils import *
from utils.load_data import *


def parse_arguments():
    parser = argparse.ArgumentParser(description="BeyondX Auto-construction")

    parser.add_argument("--random_seed", type=int,
                        default=1, help="random seed")

    parser.add_argument("--minibatch_size", type=int, default=1, choices=[
                        1], help="minibatch size should be 1 because GPT-3 API takes only 1 input for each request")

    parser.add_argument("--max_num_worker", type=int, default=3,
                    help="maximum number of workers for dataloader")

    parser.add_argument(
        "--dataset", type=str, default="alg514", choices=["alg514", "draw1k", "MU_3", "MU_4"], help="source dataset used for experiment"
    )

    parser.add_argument(
        "--api_time_interval", type=float, default=1.0, help=""
    )

    parser.add_argument(
        "--limit_dataset_size", type=int, default=10, help="whether to limit dataset size. if 0, the dataset size is unlimited and we use all the samples in the dataset for generating."
    )

    args = parser.parse_args()

    if args.dataset == "draw1k":
        args.dataset_path = "./dataset/draw1k/draw1k_test_processed.json"
        args.unknown = "three"
        args.problem_extractor = "The new math word problem is:"
        args.output_file = "./dataset/beyondx/mu_3_draw1k_test.json"
    elif args.dataset == "alg514":
        args.dataset_path = "./dataset/alg514/alg514_processed.json"
        args.unknown = "three"
        args.problem_extractor = "The new math word problem is:"
        args.output_file = "./dataset/beyondx/mu_3_alg514_test.json"
    elif args.dataset == "MU_3":
        args.dataset_path = "./dataset/beyondx/mu_3.json"
        args.unknown = "four"
        args.problem_extractor = "Step 5: Formulate and Rephrase the Statements and Scenario"
        args.output_file = "./dataset/beyondx/mu_4_test.json"
    elif args.dataset == "MU_4":
        args.dataset_path = "./dataset/beyondx/mu_4.json"
        args.unknown = "five"
        args.problem_extractor = "Step 5: Formulate the New Problem"
        args.output_file = "./dataset/beyondx/mu_5_test.json"
    else:
        raise ValueError("dataset is not properly defined ...")

    return args

def prompt_construction(args, x, y, rationale):
    if args.unknown == "three":
        prompt =  THREE_UNKNOWN + "System of Equations:\n" + rationale[0] + "\n" + rationale[1] + "\n\nSolution of System of Equations:\n" + "x = " + y[0] + "\ny = " + y[1] + "\n\nProblem:\n" + x[0]
    elif args.unknown == "four":
        prompt =  FOUR_UNKNOWN + "System of Equations:\n" + rationale[0] + "\n" + rationale[1] + "\n" + rationale[2] + "\n\nSolution of System of Equations:\n" + "x = " + y[0] + "\ny = " + y[1] + "\nz = " + y[2] + "\n\nProblem:\n" + x[0]
    elif args.unknown == "five":
        prompt =  FIVE_UNKNOWN + "System of Equations:\n" + rationale[0] + "\n" + rationale[1] + "\n" + rationale[2] + "\n" + rationale[3] + "\n\nSolution of System of Equations:\n" + "x = " + y[0] + "\ny = " + y[1] + "\nz = " + y[2] + "\nw = " + y[3] + "\n\nProblem:\n" + x[0]

    return prompt

@retry(tries=1, delay=20)
def decoder_for_gpt4(args, input, max_length, stop_word):
    # GPT-4 API allows each users execute the API within 60 times in a minute ...
    time.sleep(args.api_time_interval)

    # https://beta.openai.com/account/api-keys
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.organization = os.getenv("OPENAI_ORGANIZATION")
    
    completion = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": input}
        ],
        max_tokens=max_length,
        temperature=0,
        seed=0,
        stop=stop_word
    )
    return completion.choices[0].message['content']

def modify_correct_system_of_equations(args, second_part, y):
    text = second_part[0]
    if args.unknown == "three":
        match = re.search(r'z = (\d+)', text)
    elif args.unknown == "four":
        match = re.search(r'w = (\d+)', text)
    elif args.unknown == "five":
        match = re.search(r'v = (\d+)', text)

    if match:
        # Extracting the number
        new_var = match.group(1)
    eq_sys = (second_part[1].split(":")[-1]).strip().rstrip()
    new_eq_sys = ""
    new_eq_sys_list = []
    if args.unknown == "three":
        subs_dict = {'x': float(y[0]), 'y': float(y[1]), 'z': float(new_var)}
    elif args.unknown == "four":
        subs_dict = {'x': float(y[0]), 'y': float(y[1]), 'z': float(y[2]), 'w': float(new_var)}
    elif args.unknown == "five":
        subs_dict = {'x': float(y[0]), 'y': float(y[1]), 'z': float(y[2]), 'w': float(y[3]), 'v': float(new_var)}

    for equ_str in eq_sys.split("\n"):
        equ_str_split = equ_str.split("=")
        sub_str = equ_str_split[0] + ' - ( ' + equ_str_split[1].strip() + ' )'
        sub_str = sympify(sub_str)
        result = sub_str.subs(subs_dict)
        new_right = str(sympify(equ_str_split[1] + ' + ( ' + str(result) + ' )'))
        new_right = new_right.replace('*', ' * ')
        sub_eq_sys = equ_str_split[0] + ' = ' + new_right
        new_eq_sys_list.append(sub_eq_sys)
        new_eq_sys += (sub_eq_sys + "\n")
    y.append(new_var)
    return new_eq_sys, new_eq_sys_list, y

def output_json_data(args, response, y, new_eq_sys_list, i):
    # You can modify the pattern if model output changes
    response_json = {
        "problem": response.split(args.problem_extractor)[-1].strip().rstrip(),
        "system_of_equations": new_eq_sys_list,
        "ans": y,
        "id": str(i+1)
    }
    return response_json

def main():
    generated_dataset = []
    args = parse_arguments()
    fix_seed(args.random_seed)
    dataloader = setup_data_loader(args)


    for i, data in enumerate(dataloader):
        # prepare question template ...
        x, y, question_num, rationale = data
        y = [i[0].strip() for i in y]
        rationale = [i[0].strip() for i in rationale]
        # filer out single unknown problem (start from two unknown)
        if len(rationale) == 1:
            continue
        prompt = prompt_construction(args, x, y, rationale)
        response = decoder_for_gpt4(args, prompt, 1024, "Step 4")
        if response is None:
            continue
        second_part = response.split("Step 2:")[-1].strip()
        second_part = second_part.split("Step 3:")

        if len(second_part) == 2:
            # correct the system of equations via substitute the coefficient or constant
            new_eq_sys, new_eq_sys_list, y = modify_correct_system_of_equations(args, second_part, y)
        else:
            continue

        # second call model with modified prompt
        response_split = response.split("Step 3:")
        response_step3 = response_split[-1].split(":")[0]
        second_prompt = prompt + response_split[0] + "Step 3:" + response_step3 + ":\n\n" + new_eq_sys + "\nStep 4:"

        response = decoder_for_gpt4(args, second_prompt, 2048, None)
        if response is None:
            continue

        response_json = output_json_data(args, response, y, new_eq_sys_list, i)
        generated_dataset.append(response_json)
        if (args.limit_dataset_size != 0) and ((i+1) >= args.limit_dataset_size):
            break

    with open(args.output_file, "w") as outfile:
        json.dump(generated_dataset, outfile, indent=4)

if __name__ == "__main__":
    main()
