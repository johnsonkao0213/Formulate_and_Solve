import re
import json
import torch
import random
import numpy as np
import multiprocessing
from statistics import mean
from torch.utils.data import Dataset
from utils.utils import *

def data_reader(args):
    questions = []
    answers = []
    question_num = []
    rationales = []
    decoder = json.JSONDecoder()

    if args.dataset == "aqua":
        with open(args.dataset_path) as f:
            lines = f.readlines()
            for index, line in enumerate(lines):
                json_res = decoder.raw_decode(line)[0]
                choice = "(" + "(".join(json_res["options"])
                choice = choice.replace("(", " (").replace(")", ") ")
                choice = "Answer Choices:" + choice
                questions.append(json_res["question"].strip() + " " + choice)
                answers.append([json_res["correct"]])
                question_num.append(index)
                rationales.append([json_res["rationale"]])

    elif args.dataset == "gsm8k":
        with open(args.dataset_path) as f:
            lines = f.readlines()
            for index, line in enumerate(lines):
                json_res = decoder.raw_decode(line)[0]
                questions.append(json_res["question"].strip())
                answers.append([json_res["answer"].split("#### ")[-1]])
                question_num.append(index)
                rationales.append([json_res["answer"].split("#### ")[0]])

    elif args.dataset in ("addsub", "multiarith", "singleeq"):
        with open(args.dataset_path) as f:
            json_data = json.load(f)
            for line in json_data:
                q = line["sQuestion"].strip()
                a = str(line["lSolutions"][0])
                if a[-2:] == ".0":
                    a = a[:-2]
                questions.append(q)
                answers.append([a])
                question_num.append(line['iIndex'])
                rationales.append(line["lEquations"])

    elif args.dataset in ("draw1k", "alg514", "dolphin"):
        with open(args.dataset_path) as f:
            json_data = json.load(f)
            for line in json_data:
                q = line["sQuestion"].strip()
                a = [str(i)[:-2] if str(i)[-2:] == ".0" else str(i)
                    for i in line["lSolutions"]]
                questions.append(q)
                answers.append(a)
                question_num.append(line['iIndex'])
                rationales.append(line['lEquations'].split(';'))

    elif args.dataset in ("hmwp", "hmwp_old"):
        with open(args.dataset_path) as f:
            json_data = json.load(f)
            for line in json_data:
                q = line["new_text"].strip()
                a = [str(i)[:-2] if str(i)[-2:] == ".0" else str(i)
                    for i in line["ans"]]
                questions.append(q)
                answers.append(a)
                question_num.append(line['id'])
                rationales.append(line['equation'].split(';'))
    
    elif args.dataset in ("MU_3", "MU_4", "MU_5"):
        with open(args.dataset_path) as f:
            json_data = json.load(f)
            for line in json_data:
                q = line["problem"].strip()
                a = [str(i)[:-2] if str(i)[-2:] == ".0" else str(i)
                    for i in line["ans"]]
                questions.append(q)
                answers.append(a)
                question_num.append(line['id'])
                rationales.append(line['system_of_equations'])
    
    elif args.dataset == "asdiv":
        with open(args.dataset_path) as f:
            json_data = json.load(f)
            for line in json_data:
                q = line["sQuestion"].strip()
                sol = line["lSolutions"].replace(";", "")
                a = [s for s in re.findall(r'-?\d+\.?\d*', sol)]
                if line["Type"] == "Algebra-1":
                    eqs = [line['lEquations'].split(';')[-1].strip()]
                else:
                    eqs = [i.strip() for i in line['lEquations'].split(';')[-2:]]
                questions.append(q)
                answers.append(a)
                question_num.append(line['id'])
                rationales.append(eqs)

    elif args.dataset == "svamp":
        with open(args.dataset_path) as f:
            json_data = json.load(f)
            for line in json_data:
                q = line["Body"].strip() + " " + line["Question"].strip()
                a = str(line["Answer"])
                if a[-2:] == ".0":
                    a = a[:-2]
                questions.append(q)
                answers.append([a])
                question_num.append(line['ID'])
                rationales.append([line['Equation']])

    else:
        raise ValueError("dataset is not properly defined ...")

    q_len_list = []
    for q in questions:
        q_len_list.append(len(q.split(" ")))
    q_len_mean = mean(q_len_list)
    
    a_len_list = []
    for a in answers:
        a_len_list.append(len(a))
    a_len_mean = mean(a_len_list)

    print("dataset : {}".format(args.dataset))
    print("data size : {}".format(len(answers)))
    print("average num of words for each sample : {}".format(q_len_mean))
    print("average num of unknowns for each sample : {}".format(a_len_mean))

    return questions, answers, question_num, rationales

# Create dataset object before dataloader ...
class MyDataset(Dataset):
    def __init__(self, args):
        super().__init__()
        self.questions, self.answers, self.question_num, self.rationales = data_reader(args)
        self.len = len(self.questions)

    def __len__(self):
        return self.len

    def __getitem__(self, index):
        input = self.questions[index]
        output = self.answers[index]
        question_num = self.question_num[index]
        rationale = self.rationales[index]
        return input, output, question_num, rationale


def setup_data_loader(args):
    # fix randomness of dataloader to ensure reproducibility
    # https://pytorch.org/docs/stable/notes/randomness.html
    fix_seed(args.random_seed)
    worker_seed = torch.initial_seed() % 2**32
    print("worker_seed : {}".format(worker_seed))

    def seed_worker(worker_id):
        np.random.seed(worker_seed)
        random.seed(worker_seed)
    g = torch.Generator()
    g.manual_seed(worker_seed)

    dataloader_num_workers = multiprocessing.cpu_count()
    dataloader_num_workers = min(dataloader_num_workers, args.max_num_worker)
    print("dataloader_num_workers: " + str(dataloader_num_workers))

    dataset = MyDataset(args)

    dataloader = torch.utils.data.DataLoader(dataset,
                                             shuffle=True,
                                             batch_size=args.minibatch_size,
                                             drop_last=False,
                                             num_workers=dataloader_num_workers,
                                             worker_init_fn=seed_worker,
                                             generator=g,
                                             pin_memory=True)

    return dataloader

