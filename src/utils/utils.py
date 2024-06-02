import torch
import random
import numpy as np
from sympy import Float, Rational, Integer

def fix_seed(seed):
    # random
    random.seed(seed)
    # Numpy
    np.random.seed(seed)
    # Pytorch
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True

def has_sympy_number(lst):
    flag = False
    for element in lst:
        if isinstance(element, float) or isinstance(element, int) or isinstance(element, Float) or isinstance(element, Rational) or isinstance(element, Integer):
            continue
        else:
            flag = True
    return flag

def check_solving_error(pred):
    if pred == None or pred == "error" or pred == [] or pred == ["-100000"] or has_sympy_number(pred):
        return True
    else:
        return False

def check_small_difference(pred_ans, ans_list):
    ans_ac = True

    if len(ans_list) == 0:
        ans_ac = False
    elif len(ans_list) == 1:
        change = False
        for a in ans_list:
            find = False
            for t_a in pred_ans:
                try:
                    if abs(float(a) - float(t_a)) < 1e-1:
                        find = True
                        break
                except Exception as e:
                    pass
            if find:
                continue
            else:
                change = True
                break
        if change:
            ans_ac = False
    else:
        if len(ans_list) > len(pred_ans):
            change = False
            for t_a in pred_ans:
                find = False
                for a in ans_list:
                    try:
                        if abs(float(a) - float(t_a)) < 1e-1:
                            find = True
                            break
                    except Exception as e:
                        pass
                if find:
                    continue
                else:
                    change = True
                    break
            if change or len(pred_ans)==0:
                ans_ac = False
        else:
            change = False
            for a in ans_list:
                find = False
                for t_a in pred_ans:
                    try:
                        if abs(float(a) - float(t_a)) < 1e-1:
                            find = True
                            break
                    except Exception as e:
                        pass
                if find:
                    continue
                else:
                    change = True
                    break
            if change:
                ans_ac = False

    return ans_ac
