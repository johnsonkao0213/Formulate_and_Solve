import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Formulate-and-Solve")

    parser.add_argument(
        "--api_log_file_name", type=str, default=None, help="mandatory argument ! json['i>=1']['j==1']['k={1,2}'][{'request', response'}]"
    )

    parser.add_argument("--random_seed", type=int,
                        default=1, help="random seed")

    parser.add_argument(
        "--dataset", type=str, default="alg514", choices=["gsm8k", "addsub", "multiarith", "svamp", "singleeq", "alg514", "draw1k", "hmwp", "asdiv", "BeyondX_3", "BeyondX_4", "BeyondX_5"], help="dataset used for experiment"
    )

    parser.add_argument("--minibatch_size", type=int, default=1, choices=[
                        1], help="minibatch size should be 1 because GPT-3 API takes only 1 input for each request")

    parser.add_argument("--max_num_worker", type=int, default=3,
                        help="maximum number of workers for dataloader")

    parser.add_argument(
        "--model", type=str, default="gpt3", choices=["gpt3", "gpt4", "gemini", "deepseek", "llama2", "llama3", "llama3-instruct", "mistral", "xwin", "abel", "metamath", "wizard", "arithmo2", "mmiqc", "mammoth", "mammoth2", "openmath"], help="model used for decoding. Note that 'gpt3' are the smallest models."
    )

    parser.add_argument(
        "--method", type=str, default="zero_shot_cot", choices=["zero_shot_cot", "zero_shot_plan_and_solve", "few_shot_cot", "few_shot_pot", "few_shot_eot", "few_shot_declarative", "auto_analogical", "auto_zero_shot_cot", "auto_formulate_and_solve"], help="method"
    )

    parser.add_argument(
        "--exp_name", type=str, default="add_instruction", help="exp name"
    )

    parser.add_argument(
        "--max_length_cot", type=int, default=2048, help="maximum length of output tokens by model for reasoning extraction"
    )

    parser.add_argument(
        "--max_length_direct", type=int, default=512, help="maximum length of output tokens by model for answer extraction"
    )

    parser.add_argument(
        "--limit_dataset_size", type=int, default=10, help="whether to limit test dataset size. if 0, the dataset size is unlimited and we use all the samples in the dataset for testing."
    )

    parser.add_argument(
        "--api_time_interval", type=float, default=1.0, help=""
    )

    parser.add_argument(
        "--log_dir", type=str, default="./log/", help="log directory"
    )

    args = parser.parse_args()

    if args.dataset == "gsm8k":
        args.dataset_path = "./dataset/grade-school-math/test.jsonl"
        args.direct_answer_trigger = "\nTherefore, the answer (arabic numerals) is"
    elif args.dataset == "addsub":
        args.dataset_path = "./dataset/AddSub/AddSub.json"
        args.direct_answer_trigger = "\nTherefore, the answer (arabic numerals) is"
    elif args.dataset == "multiarith":
        args.dataset_path = "./dataset/MultiArith/MultiArith.json"
        args.direct_answer_trigger = "\nTherefore, the answer (arabic numerals) is"
    elif args.dataset == "svamp":
        args.dataset_path = "./dataset/SVAMP/SVAMP.json"
        args.direct_answer_trigger = "\nTherefore, the answer (arabic numerals) is"
    elif args.dataset == "singleeq":
        args.dataset_path = "./dataset/SingleEq/questions.json"
        args.direct_answer_trigger = "\nTherefore, the answer (arabic numerals) is"
    elif args.dataset == "draw1k":
        args.dataset_path = "./dataset/draw1k/draw1k_test_processed.json"
        args.direct_answer_trigger = "\nTherefore, the answer (arabic numerals) is:"
    elif args.dataset == "alg514":
        args.dataset_path = "./dataset/alg514/alg514_processed.json"
        args.direct_answer_trigger = "\nTherefore, the answer (arabic numerals) is:"
    elif args.dataset == "BeyondX_3":
        args.dataset_path = "./dataset/BeyondX/BeyondX_3.json"
        args.direct_answer_trigger = "\nTherefore, the answer (arabic numerals) is:"
    elif args.dataset == "BeyondX_4":
        args.dataset_path = "./dataset/BeyondX/BeyondX_4.json"
        args.direct_answer_trigger = "\nTherefore, the answer (arabic numerals) is:"
    elif args.dataset == "BeyondX_5":
        args.dataset_path = "./dataset/BeyondX/BeyondX_5.json"
        args.direct_answer_trigger = "\nTherefore, the answer (arabic numerals) is:"
    elif args.dataset == "hmwp":
        args.dataset_path = "./dataset/hmwp/hmwp_testset.json"
        args.direct_answer_trigger = "\nTherefore, the answer (arabic numerals) is:"
    elif args.dataset == "asdiv":
        args.dataset_path = "./dataset/asdiv/Asdiv_algebra.json"
        args.direct_answer_trigger = "\nTherefore, the answer (arabic numerals) is:"
    else:
        raise ValueError("dataset is not properly defined ...")

    args.direct_answer_trigger_for_zeroshot_cot = args.direct_answer_trigger
    args.direct_answer_trigger_for_fewshot = "The answer is:"

    return args
