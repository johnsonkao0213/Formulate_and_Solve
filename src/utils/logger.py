def log_data(text, path):
    with open(path + '/loggings.txt', 'a', encoding='utf-8') as f:
        f.write(text)
        print(text)
        f.write('\n')

def log_exp_data(exp_name, text, path):
    with open(path + 'exp_result.txt', 'a', encoding='utf-8') as f:
        f.write(exp_name)
        print(exp_name)
        f.write('\n')
        f.write(text)
        print(text)
        f.write('\n')
        f.write('=================================================')
        f.write('\n')

def log_error_data(text, path):
    with open(path + '/error_loggings.txt', 'a', encoding='utf-8') as f:
        f.write(text)
        print(text)
        f.write('\n')
