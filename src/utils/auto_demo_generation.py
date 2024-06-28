import copy
from model.brain import *
from utils.utils import *
from utils.solver import *

# our instruction prompt for formulate_and_solve
INSTRUCTION_PROMPT = '''Let's translate mathematical word problems into the system of equations in a careful, formal manner. The system of equations will follow the following solving steps: 
1- Determine what the question is asking.
2- Write down the relevant information in simple statements.
3- Assign symbols (must be an alphabetic character e.g., x, y, z etc.) to unknown values that need to be found.
4- Determine how the statements relate to each other mathematically.
5- Give the system of equations only here, with each equation on a new line.'''

# INSTRUCTION_PROMPT = '''Let's translate mathematical word problems into the system of equations in a careful, formal manner. The system of equations will follow the following solving steps: 
# Step 1: Determine what the question is asking.
# Step 2: Write down the relevant information in simple statements.
# Step 3: Assign symbols (must be an alphabetic character e.g., x, y, z etc.) to unknown values that need to be found.
# Step 4: Determine how the statements relate to each other mathematically.
# Step 5: Give the system of equations only here, with each equation on a new line.'''


def auto_demo_generation(args, decoder):
    if args.dataset == "BeyondX_5":
        demos = [
            "Q: Suppose you invested 16,000 dollars in five different ways: part at 6 % annual interest, part at 9 % annual interest, part at 4 % annual interest, part at 3 % annual interest, and the rest at 2 % annual interest. After one year, you received 864 dollars in interest. Also, the amount invested at 6% annual interest plus the amount invested at 9% annual interest equals five times the amount invested at 4% annual interest. The amount invested at 6% annual interest plus the amount invested at 9% annual interest plus the amount invested at 4% annual interest equals six times the amount invested at 3% annual interest. The amount invested at 6% annual interest plus the amount invested at 9% annual interest plus the amount invested at 4% annual interest plus the amount invested at 3% annual interest equals seven times the amount invested at 2% annual interest. How much did you invest at each rate?",
            "Q: At a fast food restaurant, one pan pizza, two cheeseburgers, one milkshake, and three chicken sandwiches provide 4260 calories. Two pan pizzas, one cheeseburger, one milkshake, two chicken sandwiches, and one serving of french fries provide 4690 calories. One pan pizza, one cheeseburger, two milkshakes, one chicken sandwich, and one serving of french fries provide 3850 calories. Two pan pizzas, two cheeseburgers, one milkshake, one chicken sandwich, and one serving of french fries provide 5300 calories. One of each item plus an additional serving of french fries provide 4500 calories. Find the caloric content of each item.",
            "Q: At a local event, tickets are sold at different prices: 4 dollars for students, 6 dollars for general admission, 3 dollars for seniors, 2 dollars for children, and 10 dollars for VIPs. In total, 725 tickets were sold, collecting 3776 dollars. It is known that twice the number of student tickets plus the number of general admission tickets plus half the number of senior tickets plus half the number of child tickets plus half the number of VIP tickets equals 762. The number of student tickets plus the number of general admission tickets plus the number of senior tickets plus twice the number of child tickets plus the number of VIP tickets equals 775. The number of each type of ticket plus twice the number of VIP tickets equals 775. How many student, general admission, senior, child, and VIP tickets were sold?",
            "Q: In a school, the ratio of boys to girls is 9 to 4. Including the teachers, staff, and administrators, there are 147 people in total. The ratio of boys to teachers is 9 to 2. The number of boys and girls combined is three times the number of staff members. The number of boys, girls, and teachers combined is seven times the number of administrators. How many boys, girls, teachers, staff members, and administrators are there in the school?",
            "Q: 42 is divided into five parts. 7 times the first part, 5 times the second part, 3 times the third part, 2 times the fourth part, and the fifth part equals 181. Also, the sum of the first part and the second part equals four times the third part. The sum of the first part, the second part, and the third part equals six times the fourth part. The sum of the first part, the second part, the third part, and the fourth part equals five times the fifth part. Find each part."
        ]
        ans = ["7200, 2800, 2000, 2000, 2000", "1040, 910, 500, 300, 600", "137, 388, 100, 50, 50", "63, 28, 14, 27, 15", "13, 11, 6, 5, 7"]
    elif args.dataset == "BeyondX_4":
        demos = [
            "Q: Suppose you invested 14,000 dollars in four different ways: part at 6 % annual interest, part at 9 % annual interest, part at 4 % annual interest, and the rest at 3 % annual interest. After one year, you received 824 dollars in interest. Also, the amount invested at 6% annual interest plus the amount invested at 9% annual interest equals five times the amount invested at 4% annual interest. The amount invested at 6% annual interest plus the amount invested at 9% annual interest plus the amount invested at 4% annual interest equals six times the amount invested at 3% annual interest. How much did you invest at each rate?",
            "Q: At a fast food restaurant, one pan pizza, two cheeseburgers, one milkshake, and three chicken sandwiches provide 4260 calories. Two pan pizzas, one cheeseburger, one milkshake, and two chicken sandwiches provide 4090 calories. One pan pizza, one cheeseburger, two milkshakes, and one chicken sandwich provide 3250 calories. Two pan pizzas, two cheeseburgers, one milkshake, and one chicken sandwich provide 4700 calories. Find the caloric content of each item.",
            "Q: At a local event, tickets are sold at different prices: 4 dollars for students, 6 dollars for general admission, 3 dollars for seniors, and 2 dollars for children. In total, 675 tickets were sold, collecting 3276 dollars. It is known that twice the number of student tickets plus the number of general admission tickets plus half the number of senior tickets plus half the number of child tickets equals 737. The number of student tickets plus the number of general admission tickets plus the number of senior tickets plus twice the number of child tickets equals 725. How many student, general admission, senior, and child tickets were sold?",
            "Q: In a school, the ratio of boys to girls is 9 to 4. Including the teachers and staff, there are 132 people in total. The ratio of boys to teachers is 9 to 2. The number of boys and girls combined is three times the number of staff members. How many boys, girls, teachers, and staff members are there in the school?",
            "Q: 35 is divided into four parts. 7 times the first part, 5 times the second part, 3 times the third part, and 2 times the fourth part equals 174. Also, the sum of the first part and the second part equals four times the third part. The sum of the first part, the second part, and the third part equals six times the fourth part. Find each part.",
        ]
        ans = ["7200, 2800, 2000, 2000", "1040, 910, 500, 300", "137, 388, 100, 50", "63, 28, 14, 27", "13, 11, 6, 5"]
    elif args.dataset == "BeyondX_3":
        demos = [
            "Q: Suppose you invested 12,000 dollars in three different ways: part at 6 % annual interest, part at 9 % annual interest, and the rest at 4 % annual interest. After one year, you received 764 dollars in interest. Also, the amount invested at 6% annual interest plus the amount invested at 9% annual interest equals five times the amount invested at 4% annual interest. How much did you invest at each rate?",
            "Q: At a fast food restaurant, one pan pizza, two cheeseburgers, and one milkshake provide 3360 calories. Two pan pizzas, one cheeseburger, and one milkshake provide 3490 calories. One pan pizza, one cheeseburger, and two milkshakes provide 2950 calories. Find the caloric content of each item.",
            "Q: At a local event, tickets are sold at different prices: 4 dollars for students, 6 dollars for general admission, and 3 dollars for seniors. In total, 625 tickets were sold, collecting 3176 dollars. It is known that twice the number of student tickets plus the number of general admission tickets plus half the number of senior tickets equals 712. How many student, general admission, and senior tickets were sold?",
            "Q: In a school, the ratio of boys to girls is 9 to 4. Including the teachers, there are 105 people in total. The ratio of boys to teachers is 9 to 2. How many boys, girls, and teachers are there in the school?",
            "Q: 30 is divided into three parts. 7 times the first part, 5 times the second part, and 3 times the third part equals 164. Also, the sum of the first part and the second part equals four times the third part. Find each part.",
        ]
        ans = ["7200, 2800, 2000", "1040, 910, 500", "137, 388, 100", "63, 28, 14", "13, 11, 6"]
    elif args.dataset in ("alg514", "draw1k", "hmwp", "asdiv"):
        # demos = [
        #     "Q: Mike invested $6000 for one year. He invested part of it at 9% and the rest at 11%. At the end of the year he earned $624 in interest. How much did he invest at each rate?",
        #     "Q: One pan pizza and two cheesburgers provide 2860 calories. Two pan pizzas and one cheeseburger provide 2990 calories. Find the caloric content of each item.",
        #     "Q: A theater sells adult tickets for $8 and children's tickets for $5. If a total of $236 was taken in on sales of 34 total tickets, then how many adult tickets were sold?",
        #     "Q: The ratio of boys to girls is 9 to 4. You know there are 91 total students. How many of them are boys? How many are girls?",
        #     "Q: A number added to 6 is equal to 30 less than four times the number. what is the number.",
        # ]
        # ans = ["1800, 4200", "1040, 910", "22", "63, 28", "12"]
        
        demos = [
            "Q: Mike invested $6000 for one year. He invested part of it at 9% and the rest at 11%. At the end of the year he earned $624 in interest. How much did he invest at each rate?",
            "Q: One pan pizza and two cheesburgers provide 2860 calories. Two pan pizzas and one cheeseburger provide 2990 calories. Find the caloric content of each item.",
            "Q: A number added to 6 is equal to 30 less than four times the number. what is the number.",
        ]
        ans = ["1800, 4200", "1040, 910", "12"]
        
        # demos = [
        #     "Q: Mike invested $6000 for one year. He invested part of it at 9% and the rest at 11%. At the end of the year he earned $624 in interest. How much did he invest at each rate?",
        #     "Q: One pan pizza and two cheesburgers provide 2860 calories. Two pan pizzas and one cheeseburger provide 2990 calories. Find the caloric content of each item.",
        #     "Q: A theater sells adult tickets for $8 and children's tickets for $5. If a total of $236 was taken in on sales of 34 total tickets, then how many adult tickets were sold?",
        #     "Q: The ratio of boys to girls is 9 to 4. You know there are 91 total students. How many of them are boys? How many are girls?",
        #     "Q: A number added to 6 is equal to 30 less than four times the number. what is the number.",
        #     "Q: A car radiator has a 6-liter capacity. If the liquid in the radiators 40 % antifreeze, how much liquid must be replaced with 100 % antifreeze to bring the mixture up to a 50 % solutions?",
        #     "Q: Eight years ago, Hold was 7 times older than her son. Today, she is exactly 3 times as old as her son. How old are both Mrs. Hold and her son today?",
        #     "Q: It takes you 30 minutes to rake the yard and it takes your brother 45 minutes, how long would it take for you both to rake the yard together?"
        # ]
        # ans = ["1800, 4200", "1040, 910", "22", "63, 28", "12", "1, 5", "36, 12", "18"]
        
    elif args.dataset in ("gsm8k", "addsub", "multiarith", "svamp", "singleeq"):
        demos = [
            "Q: Mike invested $6000 for one year. He invested part of it at 9% and the rest at 11%. At the end of the year he earned $624 in interest. How much did he invest at each rate?",
            "Q: One pan pizza and two cheesburgers provide 2860 calories. Two pan pizzas and one cheeseburger provide 2990 calories. Find the caloric content of each item.",
            "Q: A theater sells adult tickets for $8 and children's tickets for $5. If a total of $236 was taken in on sales of 34 total tickets, then how many adult tickets were sold?",
            "Q: The ratio of boys to girls is 9 to 4. You know there are 91 total students. How many of them are boys? How many are girls?",
            "Q: A number added to 6 is equal to 30 less than four times the number. what is the number.",
        ]
        ans = ["1800, 4200", "1040, 910", "22", "63, 28", "12"]
        # demos = [
        #     "Q: Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. How many lollipops did Jason give to Denny?",
        #     "Q: Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?",
        #     "Q: If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?",
        #     "Q: There were nine computers in the server room. Five more computers were installed each day, from monday to thursday. How many computers are now in the server room?",
        #     "Q: Olivia has $23. She bought five bagels for $3 each. How much money does she have left?",
        #     "Q: There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?",
        #     "Q: Shawn has five toys. For Christmas, he got two toys each from his mom and dad. How many toys does he have now?",
        #     "Q: Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?"
        # ]
        # ans = ["8", "33", "5", "29", "8", "6", "9", "39"]
    else:
        raise ValueError("dataset is not properly defined ...")

    if args.method == "auto_zero_shot_cot":
        demo_text = ""
        final_demo_text = ""
        for i, demo in enumerate(demos):
            demo_text += demo + "\nA: Let's think step by step."
            response = decoder.decode(args, demo_text, args.max_length_cot)
            demo_text += response + "\n\n"
            final_demo_text += demo + "\nA: Let's think step by step." + response + "\n\n" + \
                        args.direct_answer_trigger_for_fewshot + " " + ans[i] + ".\n\n"
    elif args.method == "auto_formulate_and_solve":
        final_demo_text = INSTRUCTION_PROMPT + "\n\n"
        for i, demo in enumerate(demos):
            final_demo_text += demo + "\nA: "
            response = decoder.decode(args, final_demo_text, args.max_length_cot)
            final_demo_text += response + "\n\n"
    else:
        raise ValueError("method is not properly defined ...")
    
    return final_demo_text

# run 10 samples for 10 times to select best performance demo
def auto_demo_selection(args, decoder, dataloader):
    accuracy_best = 0.0
    for _ in range(10):
        demo = auto_demo_generation(args, decoder)
        print(demo)
        total = 0
        correct = 0
        for data in dataloader:
            x, y, question_num, rationale = data
            y = [i[0].strip() for i in y]
            x2 = copy.copy("Q: " + x[0] + "\n" + "A: ")
            x = demo + "Q: " + x[0] + "\n" + "A: "
            z = decoder.decode(args, x, args.max_length_cot)

            if args.method == "auto_zero_shot_cot":
                pred_ans = answer_cleansing_multi_var(args, z)
            elif args.method == "auto_formulate_and_solve":
                computed_pred = solve_formulate_and_solve(z)
                if isinstance(computed_pred, dict):
                    tmp_ans = list(computed_pred.values())
                else:
                    tmp_ans = computed_pred

                if check_solving_error(tmp_ans):
                    # z3 = x2 + z + "\n\nThe ultimate answer must be enclosed in \\boxed{}.\nThe ultimate answer (convert fractions to decimals form) is:"
                    pred_ans = tmp_ans
                else:
                    z3 = x2 + z + "\n\n" + "Given the solution of the system of equations: " + str(computed_pred) \
                    + "\nDo not solve the system of equations.\nThe ultimate answer must be enclosed in \\boxed{} in one line with number(s) only.\nThe ultimate answer (convert fractions to decimals form) is:"
                    second_stage = decoder.decode(args, z3, args.max_length_direct)
                    pred_ans = answer_cleansing_multi_var(args, second_stage)

            total += 1
            if check_small_difference(pred_ans, y):
                correct += 1
            if total == 20:
                accuracy = correct/total
                print(accuracy)
                if accuracy > accuracy_best:
                    accuracy_best = accuracy
                    best_demo = demo
                break
    return best_demo
