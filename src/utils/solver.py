import re
import string
import numpy as np
import func_timeout
from sympy import S, Eq, solve, sympify, Symbol
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

#solver for each prompting method to extract final answer

def solve_formulate_and_solve(pred):
    def contains_alphabet(input_str):
        return any(char.isalpha() for char in input_str)

    def compute_expressions(equations):
        filtered_var_list = set()
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        var_list = [i for i in alphabet]
        equations = [x.lower() for x in equations]
        for equation in equations:
            for elem in equation:
                if elem in var_list:
                    filtered_var_list.add(elem)
        
        if len(filtered_var_list) == 0:
            equations_str = ' '.join(equations)
            equations_str = 'x = ' + equations_str
            print("no var: {}".format(equations_str))
            filtered_var_list = ['x']
            ans = get_result_from_sympy([equations_str], filtered_var_list)
        else:
            equations_str_list = []
            for equation in equations:
                if '>' in equation or '<' in equation:
                    continue
                if '=' not in equation and '>' not in equation and '<' not in equation:
                    equations_str_list.append("0 = " + equation)
                else:
                    equations_str_list.append(equation)
            ans = get_result_from_sympy(equations_str_list, list(filtered_var_list))
        return ans

    def solve_linear_equation_with_multiple_unknown(equations_str_list, var_str):
        transformations = (standard_transformations + (implicit_multiplication_application,) + (convert_xor,))
        var_list = S(var_str.split())
        equation_list = []
        for equation in equations_str_list:
            equation_split = equation.split('=')
            if len(equation_split) == 1:
                equation_list.append(parse_expr(equation_split[0], transformations=transformations))
            else:
                equation_split = [i.replace(",", "") for i in equation_split]
                equation_split = [i.replace("$", "") for i in equation_split]
                equation_split = [i.replace("%", " * 0.01") for i in equation_split]
                sub_str = equation_split[0] + ' - ( ' + equation_split[1] + ' )'
                sub_str = parse_expr(sub_str, transformations=transformations)
                sub_str = sympify(sub_str)
                equation_list.append(sub_str)
        
        ans = solve(equation_list, var_list)
        if isinstance(ans, dict):
            new_ans = {}
            for k, v in ans.items():
                if contains_alphabet(str(v)):
                    new_ans[k] = v
                else:
                    new_ans[k] = float(v)
            return new_ans
        elif isinstance(ans, list):
            new_ans = []
            for a in ans:
                if isinstance(a, tuple):
                    new_ans.extend(a)
                else:
                    new_ans.append(a)
            return new_ans

    def get_result_from_sympy(equations_list, var_list):
        equations_str_list = []
        for equation in equations_list:
            equations_str_list.append(equation)
        var_str =' '.join(var_list)
        try:
            ans = func_timeout.func_timeout(30, solve_linear_equation_with_multiple_unknown, args=(equations_str_list, var_str))
        except func_timeout.FunctionTimedOut:
            ans = "error"
        # try:
        #     gen_ans = solve_linear_equation_with_multiple_unknown(expression_str_list, var_str)
        except Exception as e:
            print(e)
            ans = "error"
        return ans

    preds = pred.split('5-')
    # preds = pred.split("Step 5:")
    answer_flag = True if len(preds) > 1 else False
    pred = preds[-1].strip()
    
    # if not answer_flag:
    #     pred = pred.split(':')
    #     pred = pred[-1].strip()
    #     pred = pred.split('\n')[-1]
    #     pred = pred.replace(",", "")
    #     if re.search(r'-?\d+\.?\d*', pred):
    #         pred = [s for s in re.findall(r'-?\d+\.?\d*', pred)][-1]
    #     else:
    #         pred = "-100000"

    if pred != "":
        if pred[-1] == ".":
            pred = pred[:-1]

    if answer_flag:
        # equations = []
        equations = set()
        for line in pred.split('\n'):
            if '=' in line:
                line = '='.join(line.split('=')[:2])
                # equations.append(line.strip())
                equations.add(line.strip())
            else:
                continue
    else:
        # pred = pred.split(':')
        # answer_flag_two = True if len(pred) > 1 else False
        # pred = pred[-1].strip()
        # if answer_flag_two:
        #     # print(pred)
        #     # equations = []
        #     equations = set()
        #     for line in pred.split('\n'):
        #         if '=' in line:
        #             line = '='.join(line.split('=')[:2])
        #             # equations.append(line.strip())
        #             equations.add(line.strip())
        #         else:
        #             continue
        # else:
        #     equations = ["error"]
        equations = ["error"]

    ans = compute_expressions(list(equations))
    return ans

def answer_cleansing_multi_var(args, pred):
    def remove_boxed(s):
        left = "\\boxed{"
        try:
            assert s[:len(left)] == left
            assert s[-1] == "}"
            answer = s[len(left):-1]
            if "=" in answer:
                answer = answer.split("=")[-1].lstrip(" ")
            return answer
        except:
            return None

    def last_boxed_only_string(s):
        pattern = r"\\boxed\{([^}]*)\}"
        matches = re.findall(pattern, s)
        full_strings = [f"\\boxed{{{match}}}" for match in matches]
        return full_strings
    
    answer_flag = False
    if args.method in ("few_shot_cot", "auto_zero_shot_cot"):
        preds = pred.split(args.direct_answer_trigger_for_fewshot)
        answer_flag = True if len(preds) > 1 else False
        pred = preds[-1]

    if not answer_flag:
        # extract last line
        pred = pred.split('\n')[-1]
        # formulate-and-plan & analogical
        if "\\boxed" in pred:
            res = []
            for i in last_boxed_only_string(pred):
                # res.append(remove_boxed(i))
                i = i.replace(",", "")
                for s in re.findall(r'-?\d+\.?\d*', remove_boxed(i)):
                    res.append(s)
            if len(res) == 0:
                pred = pred.replace(",", "")
                res = [s for s in re.findall(r'-?\d+\.?\d*', pred)]
        # zero-shot-cot & plan-and-solve
        else:
            pred = pred.replace(",", "")
            res = [s for s in re.findall(r'-?\d+\.?\d*', pred)]
    # few-shot-cot & auto_zero_shot_cot 
    else:
        pred = pred.replace(",", "")
        res = [s for s in re.findall(r'-?\d+\.?\d*', pred)]

    # If there is no candidate in list, null is set.
    if len(res) == 0:
        new_pred = ""
    else:
        new_pred = []
        for i in res:
            if i != "":
                if i[-1] == ".":
                    i = i[:-1]
                new_pred.append(i)
        new_pred = set(new_pred)

    return new_pred

def solve_eot(raw_string):
    def safe_solve_equation_system(equations):
        # pattern = r'^(\d+)([a-zA-Z])(?![0-9])'
        pattern = r'^([\d+\.]+)([a-zA-Z])'
        # digit_pattern = r'^([\d+\.]+)(\([\d+]+\))'  # 3(10) -> 3*10
        digit_pattern = r'^([\d+\.]+)\(([\d+]+)\)'

        def add_multiplication(match):
            return match.group(1) + '*' + match.group(2)

        def solve_equation_system(x):
            symbols = set()
            eqs = []
            for eq in x:
                clean_eq = [re.sub(digit_pattern, add_multiplication, seg) for seg in eq.split()]
                clean_eq = ' '.join(clean_eq)
                left, right = clean_eq.replace('(', ' ( ').replace(')', ' ) ').split('=')
                left = [re.sub(pattern, add_multiplication, c) for c in left.strip().split()]
                left = ' '.join(left)

                right = [re.sub(pattern, add_multiplication, c) for c in right.strip().split()]
                right = ' '.join(right)

                eqs.append(Eq(sympify(left), sympify(right)))
                symbols |= eqs[-1].free_symbols

            solutions = solve(eqs, symbols, dict=True)
            return {str(k): v for k, v in solutions[0].items()}

        try:
            ans = func_timeout.func_timeout(10, solve_equation_system, args=(equations,))
        except func_timeout.FunctionTimedOut:
            ans = None
        except Exception as e:
            print(e)
            ans = "error"
        
        return ans

    def floatify_ans(ans):
        if ans is None:
            return "error"
        elif type(ans) == dict:
            ans = list(ans.values())
        elif type(ans) == bool:
            ans = ans
        elif type(ans) in [list, tuple]:
            if not ans:
                return None
            else:
                try:
                    ans = [float(ans[0])]
                except Exception:
                    ans = [str(ans[0])]
        else:
            try:
                ans = [float(ans)]
            except Exception:
                ans = [str(ans)]
        return ans

    equations = []
    for line in raw_string.split('\n'):
        if '=' in line:
            line = '='.join(line.split('=')[:2])
            equations.append(line.strip())
        else:
            continue

    try:
        solutions = safe_solve_equation_system(equations)
        pred = floatify_ans(solutions)
    except Exception as e:
        print(e)
        pred = "error"
    return pred

def solve_pot(raw_string):
    def safe_execute(code_string: str, keys=None):
        def execute(x):
            try:
                exec(x)
                locals_ = locals()
                if keys is None:
                    return locals_.get('ans', None)
                else:
                    return [locals_.get(k, None) for k in keys]
            except Exception as e:
                print(e)
                return None

        try:
            ans = func_timeout.func_timeout(20, execute, args=(code_string,))
        except func_timeout.FunctionTimedOut:
            ans = None

        return ans

    def floatify_ans(ans):
        if ans is None:
            return "error"
        elif type(ans) == dict:
            ans = list(ans.values())
        elif type(ans) == bool:
            ans = "error"
        elif type(ans) in [list, tuple]:
            if not ans:
                return "error"
            else:
                try:
                    ans = [float(ans[0])]
                except Exception:
                    ans = [str(ans[0])]
        else:
            try:
                ans = [float(ans)]
            except Exception:
                ans = [str(ans)]
        return ans
    
    try:
        if '```python' in raw_string:
            raw_string = raw_string.split('```python')[1].split('```')[0]
        elif '```' in raw_string:
            raw_string = raw_string.split('```')[1].split('```')[0]
        solutions = safe_execute(raw_string)
        pred = floatify_ans(solutions)
    except Exception as e:
        print(e)
        pred = "error"
    return pred

def solve_declarative(raw_string):
    def get_final_using_sympy(equations):
        try:
            transformations = (standard_transformations + (implicit_multiplication_application,) + (convert_xor,))
            if str(equations) == 'nan':
                return np.nan
            equation_list = equations.split(',')
            for eq in equation_list:
                for c in range(len(eq)):
                    if c < len(eq) - 2:
                        if eq[c].isalpha() and eq[c + 1].isalpha() and eq[c + 2].isalpha():
                            return 'invalid equations'

            goal_var = None
            goal_expression_list = []

            if equation_list[-1].split('=')[0].strip().isalpha() or len(equation_list[-1].split('=')[0].strip()) == 2:
                goal_var = equation_list[-1].split('=')[0].strip()
            elif '=' in equation_list[-1]:
                for l in list(string.ascii_lowercase) + list(string.ascii_uppercase):
                    if l not in equation_list[-1]:
                        goal_var = l
                        break
                if goal_var is not None:
                    goal_expression = goal_var + ' - (' + equation_list[-1].split('=')[0].strip() + ')'
                    goal_expression = parse_expr(goal_expression, transformations=transformations)
                    goal_expression = sympify(goal_expression)
                    try:
                        return float(solve(goal_expression)[0])
                    except Exception as e:
                        pass
                    goal_expression_list.append(goal_expression)
                else:
                    return 'invalid equations'

            if len(equation_list) == 1:
                try:
                    goal_expression = parse_expr(equation_list[0].split('=')[0], transformations=transformations)
                    return float(sympify(goal_expression))
                except Exception as e:
                    return 'invalid equations'

            if goal_var == None:
                return 'no goal found'

            for i in range(len(equation_list) - 1):
                sub_eqs = equation_list[i]
                if '?' not in sub_eqs:
                    try:
                        sub_eqs_split = sub_eqs.split('=')
                        sub_eqs = sub_eqs_split[0].strip() + ' - (' + sub_eqs_split[1].strip() + ')'
                        sub_eqs = parse_expr(sub_eqs, transformations=transformations)
                        sub_eqs = sympify(sub_eqs)
                    except Exception as e:
                        return 'invalid equations'
                    goal_expression_list.append(sub_eqs)

                    try:
                        try:
                            return float(solve(goal_expression_list)[Symbol(goal_var)])
                        except Exception as e:
                            return float(solve(goal_expression_list)[0][Symbol(goal_var)])
                    except Exception as e:
                        pass

            return 'no solution'
        except Exception as e:
            print(e)
            return 'bug'
    
    def reformat_incre_equations(x):
        result = ''
        if len(x) >= 1:
            for eq in x:
                if len(result) == 0:
                    result += eq[2: -2]
                else:
                    result += ', ' + eq[2: -2]
        return result

    def reformat_equations_from_peano(eq_list):
        result = ''
        for eq in eq_list.split(','):
            if 'eq' in eq:
                if len(result) == 0:
                    result += eq[eq.index('eq') + 2:]
                else:
                    result += ', ' + eq[eq.index('eq') + 2:]
            elif 'answer' in eq:
                if len(result) == 0:
                    result += eq[eq.index('answer') + 6:].strip() + ' = ?'
                else:
                    result += ', ' + eq[eq.index('answer') + 6:].strip() + ' = ?'
        return result

    eq_list = re.findall(r'\[\[.*?\]\]', raw_string)
    if len(eq_list) > 0:
        eq_list = reformat_equations_from_peano(reformat_incre_equations(eq_list))

    pred = [get_final_using_sympy(eq_list)]
    return pred
    
# def solve_analogical(raw_string):
#     def extract_last_line(s):
#         lines = s.split('\n')
#         for item in lines[::-1]:
#             if item.strip() != "":
#                 last_match = item
#                 break
#         return last_match

#     def remove_boxed(s):
#         left = "\\boxed{"
#         try:
#             assert s[:len(left)] == left
#             assert s[-1] == "}"
#             answer = s[len(left):-1]
#             if "=" in answer:
#                 answer = answer.split("=")[-1].lstrip(" ")
#             return answer
#         except:
#             return None

#     def last_boxed_only_string(s):
#         pattern = r"\\boxed\{([^}]*)\}"
#         matches = re.findall(pattern, s)
#         full_strings = [f"\\boxed{{{match}}}" for match in matches]
#         return full_strings

#     def get_answer_with_dollar_sign(s):
#         first_pattern = "\$(.*)\$"
#         last_match = None
#         matches = re.findall(first_pattern, s)
#         if matches:
#             last_match = matches[-1]
#             if "=" in last_match:
#                 last_match = last_match.split("=")[-1].lstrip(" ")
#         return last_match

#     def get_answer_without_dollar_sign(s):
#         last_match = None
#         if "=" in s:
#             last_match = s.split("=")[-1].lstrip(" ").rstrip(".")
#             if "\\n" in last_match:
#                 last_match = last_match.split("\\n")[0]
#         else:
#             pattern = "(?:\\$)?\d+(?:\.\d+)?(?![\w\d])"
#             matches = re.findall(pattern, s)
#             if matches:
#                 last_match = matches[-1]
#         return last_match

#     raw_string = extract_last_line(raw_string)
#     answer = []
#     if "\\boxed" in raw_string:
#         for i in last_boxed_only_string(raw_string):
#             answer.append(remove_boxed(i))
#     else:
#         answer.append(get_answer_with_dollar_sign(raw_string))
#         if not answer:
#             answer.append(get_answer_without_dollar_sign(raw_string))
#     return answer
