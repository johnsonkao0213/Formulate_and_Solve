ANALOGICAL = '''Your task is to tackle mathematical problems. When presented with a math problem, recall relevant problems as examples. Afterward, proceed to solve the initial problem.

# Initial Problem:
{question}

# Instructions:
Make sure to include all of the following points:

## Relevant Problems:
Recall three examples of math problems that are relevant to the initial problem. Note that your problems should be distinct from each other and from the initial problem (e.g., involving different numbers and names). For each problem:
- After "Q: ", describe the problem
- After "A: ", explain the solution and enclose the ultimate answer only includes number in \\boxed{{}}.

## Solve the Initial Problem:
Say "Let's solve the following math problem." Then formulate your response in the following format:
Q: Copy and paste the initial problem here.
A: Explain the solution and enclose the ultimate answer only includes numbers in \\boxed{{}} here.'''
