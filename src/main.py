import os
import copy
from model.brain import *
from utils.utils import *
from utils.logger import *
from utils.solver import *
from utils.load_data import *
from utils.arg_parser import *
from utils.auto_demo_generation import *
from prompts.cot import *
from prompts.eot import *
from prompts.pot import *
from prompts.analogical import *
from prompts.declarative import *
from prompts.best_prompt import *

def main():
    args = parse_arguments()
    log_name = args.model + "_" + args.dataset + "_" + args.method + "_" + args.exp_name
    path = args.log_dir + log_name
    if not os.path.exists(path):
        os.mkdir(path)

    log_data('*****************************', path)
    log_data(str(args), path)
    fix_seed(args.random_seed)

    # initialize decoder class (load model and tokenizer) ...
    decoder = Decoder(args)
    # load data
    dataloader = setup_data_loader(args)
    print_now()

    # creato auto demo generation
    if args.method in ("auto_zero_shot_cot", "auto_formulate_and_solve"):
        # demo = auto_demo_generation(args)
        if args.method == "auto_formulate_and_solve" and args.dataset in ("gsm8k", "addsub", "multiarith", "svamp", "singleeq"):
            pass
        else:
            demo = auto_demo_selection(args, decoder, dataloader)
            log_data(demo, path)
    else:
        pass

    total = 0
    total_1 = 0
    total_2 = 0
    correct = 0
    correct_1 = 0
    correct_2 = 0
    json_data = {}
    for i, data in enumerate(dataloader):
        log_data('*************************', path)
        log_data("{}st data".format(i + 1), path)

        # prepare question template ...
        x, y, question_num, rationale = data
        id = question_num[0]
        log_data("Index: {}".format(id), path)
        # x = "Q: " + x[0] + "\n" + "A: "
        copy_x = copy.copy(x[0])
        log_data("Question: {}".format(copy_x), path)
        y = [i[0].strip() for i in y]
        # rationale = [i[0].strip() for i in rationale]

        # add prefix
        if args.method == "zero_shot_cot":
            x = "Q: " + x[0] + "\n" + "A: " + " " + "Let's think step by step."
        elif args.method == "zero_shot_plan_and_solve":
            x = "Q: " + x[0] + "\n" + "A: " + " " + "Let's first understand the problem and devise a plan to solve the problem. Then, let's carry out the plan and solve the problem step by step."
        elif args.method == "few_shot_cot":
            x = COT.format(question=x[0])
        elif args.method == "few_shot_pot":
            x = POT.format(question=x[0])
        elif args.method == "few_shot_eot":
            x = EOT.format(question=x[0])
        elif args.method == "few_shot_declarative":
            x = DECLARATIVE.format(question=x[0])
        elif args.method == "auto_analogical":
            x = ANALOGICAL.format(question=x[0])
        elif args.method in ("auto_zero_shot_cot", "auto_formulate_and_solve"):
            if args.method == "auto_formulate_and_solve" and args.dataset in ("gsm8k", "addsub", "multiarith", "svamp", "singleeq"):
                x2 = copy.copy("Q: " + x[0] + "\n" + "A: ")
                x = MATH_COT_NEW.format(question=x[0])
            else:
                x2 = copy.copy("Q: " + x[0] + "\n" + "A: ")
                x = demo + "Q: " + x[0] + "\n" + "A: "
        else:
            raise ValueError("method is not properly defined ...")

        # answer prediction by generating text ...
        z = decoder.decode(args, x, args.max_length_cot)

        # second iteration for zero-shot-cot related method ...
        if args.method in ("zero_shot_cot", "zero_shot_plan_and_solve"):
            z2 = x + z + " " + args.direct_answer_trigger_for_zeroshot_cot
            pred = decoder.decode(args, z2, args.max_length_direct)
            log_data(z2 + pred, path)
        else:
            pred = z
            log_data(copy_x + pred, path)
        
        if args.method == "few_shot_pot":
            pred_ans = solve_pot(pred)
        elif args.method == "few_shot_eot":
            pred_ans = solve_eot(pred)
        elif args.method == "few_shot_declarative":
            pred_ans = solve_declarative(pred)
        elif args.method in ("zero_shot_cot", "zero_shot_plan_and_solve", "few_shot_cot", "auto_analogical", "auto_zero_shot_cot"):
            pred_ans = answer_cleansing_multi_var(args, pred)
        elif args.method == "auto_formulate_and_solve":
            computed_pred = solve_formulate_and_solve(pred)
            if isinstance(computed_pred, dict):
                tmp_ans = list(computed_pred.values())
            else:
                tmp_ans = computed_pred
            log_data(str(tmp_ans), path)

            if check_solving_error(tmp_ans):
                z3 = x2 + z + "\n\nThe ultimate answer must be enclosed in \\boxed{}.\nThe ultimate answer (convert fractions to decimals form) is:"
            else:
                z3 = x2 + z + "\n\n" + "Given the solution of the system of equations: " + str(computed_pred) \
                + "\nDo not solve the system of equations.\nThe ultimate answer must be enclosed in \\boxed{} in one line with number(s) only.\nThe ultimate answer (convert fractions to decimals form) is:"
            second_stage = decoder.decode(args, z3, args.max_length_direct)
            log_data(second_stage, path)
            pred_ans = answer_cleansing_multi_var(args, second_stage)
        else:
            raise ValueError("method is not properly defined ...")
        
        total += 1
        if len(y) == 1:
            total_1 += 1
        else:
            total_2 += 1
        
        if check_small_difference(pred_ans, y):
            correct += 1
            if len(y) == 1:
                correct_1 += 1
            else:
                correct_2 += 1
        else:
            log_error_data("{}st data".format(i + 1), path)
            log_error_data("Index: {}".format(id), path)
            log_error_data(copy_x + z, path)
            log_error_data("Rationale : {}".format(rationale), path)
            log_error_data("pred : {}".format(pred_ans), path)
            log_error_data("GT : {}".format(y), path)
            log_error_data('*************************', path)
        
        log_data("Rationale: {}".format(rationale), path)
        log_data("pred : {}".format(pred_ans), path)
        log_data("GT : {}".format(y), path)
        log_data('*************************', path)

        accuracy = (correct / total) * 100
        log_data("current ans accuracy : {}".format(accuracy), path)
        if args.dataset == "MU_3":
            json_data[str(id)] = {
                "response": z
            }
        elif args.dataset == "MU_4":
            json_data[str(id+200)] = {
                "response": z
            }
        elif args.dataset == "MU_5":
            json_data[str(id+360)] = {
                "response": z
            }
        
        if (args.limit_dataset_size != 0) and ((i+1) >= args.limit_dataset_size):
            break

    if args.dataset in ("MU_3", "MU_4", "MU_5", "gsm8k", "addsub", "multiarith", "svamp", "singleeq"):
        accuracy = (correct / total) * 100
        with open(path + '/data.json', "w") as outfile:
            json.dump(json_data, outfile, indent=4)
        log_data("Total : {}".format(total), path)
        log_data("ans accuracy : {}".format(accuracy), path)
        log_exp_data(log_name, "accuracy : {}".format(accuracy), args.log_dir)
    else:
        accuracy = (correct / total) * 100
        accuracy_1 = (correct_1 / total_1) * 100
        accuracy_2 = (correct_2 / total_2) * 100
        log_data("Total : {}".format(total), path)
        log_data("Total_1 : {}".format(total_1), path)
        log_data("Total_2 : {}".format(total_2), path)
        log_data("ans accuracy : {}".format(accuracy), path)
        log_data("ans_1 accuracy : {}".format(accuracy_1), path)
        log_data("ans_2 accuracy : {}".format(accuracy_2), path)
        log_exp_data(log_name, "accuracy : {}".format(accuracy), args.log_dir)
        log_exp_data(log_name, "ans_1 accuracy : {}".format(accuracy_1), args.log_dir)
        log_exp_data(log_name, "ans_2 accuracy : {}".format(accuracy_2), args.log_dir)

if __name__ == "__main__":
    main()
