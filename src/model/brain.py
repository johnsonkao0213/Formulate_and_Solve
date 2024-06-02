import os
import time
import torch
import openai
import datetime
from retry import retry
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig, BitsAndBytesConfig

def print_now(return_flag=0):
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    now = now.strftime('%Y/%m/%d %H:%M:%S')
    if return_flag == 0:
        print(now)
    elif return_flag == 1:
        return now
    else:
        pass

@retry(tries=1, delay=20)
def decoder_for_response(args, input, max_length):
    # GPT-3 API allows each users execute the API within 60 times in a minute ...
    time.sleep(args.api_time_interval)

    # https://beta.openai.com/account/api-keys
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.organization = os.getenv("OPENAI_ORGANIZATION")
    # GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_API_KEY="AIzaSyBG96tVItiwBVzHKHHcQJ6wyFxYK1B4PZA"

    # Specify engine ...
    if args.model == "gpt3":
        engine = "gpt-3.5-turbo-1106"
    elif args.model == "gpt4":
        engine = "gpt-4-1106-preview"
    elif args.model == "gemini":
        engine = "gemini-pro"
    elif args.model == "deepseek":
        engine = "deepseek-ai/deepseek-math-7b-instruct"
    elif args.model == "mistral":
        engine = "mistralai/Mistral-7B-v0.1"
    elif args.model == "llama2":
        engine = "meta-llama/Llama-2-7b-hf"
    elif args.model == "llama3":
        engine = "meta-llama/Meta-Llama-3-8B"
    elif args.model == "llama3-instruct":
        engine = "meta-llama/Meta-Llama-3-8B-Instruct"
    elif args.model == "xwin":
        engine = "Xwin-LM/Xwin-Math-7B-V1.1"
    elif args.model == "abel":
        engine = "GAIR/Abel-7B-002"
    elif args.model == "wizard":
        engine = "WizardLM/WizardMath-7B-V1.1"
    elif args.model == "metamath":
        engine = "meta-math/MetaMath-Mistral-7B"
    elif args.model == "arithmo2":
        engine = "akjindal53244/Arithmo-Mistral-7B"
    elif args.model == "mmiqc":
        engine = "Vivacem/Mistral-7B-MMIQC"
    elif args.model == "mammoth":
        engine = "TIGER-Lab/MAmmoTH-7B-Mistral"
    elif args.model == "mammoth2":
        engine = "TIGER-Lab/MAmmoTH2-7B"
    elif args.model == "openmath":
        engine = "nvidia/OpenMath-Mistral-7B-v0.1-hf"
    else:
        raise ValueError("model is not properly defined ...")

    if args.model == "gpt4" or args.model == "gpt3":
        completion = openai.ChatCompletion.create(
            model=engine,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": input}
            ],
            max_tokens=max_length,
            temperature=0,
            seed=0,
            stop=None
        )
        return completion.choices[0].message['content']
    elif args.model == "gemini":
        generation_config = {
            'temperature': 0.0,
            'top_p': 1.0,
            'max_output_tokens': max_length,
        }
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        }

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(model_name=engine)
        response = model.generate_content(input,
            generation_config=generation_config,
            safety_settings=safety_settings 
        )
        print(response)
        return response
    elif args.model == "deepseek":
        tokenizer = AutoTokenizer.from_pretrained(engine)
        model = AutoModelForCausalLM.from_pretrained(engine, torch_dtype=torch.bfloat16, device_map="auto")
        model.generation_config = GenerationConfig.from_pretrained(engine)
        model.generation_config.pad_token_id = model.generation_config.eos_token_id

        messages = [
            {"role": "user", "content": input}
        ]
        input_tensor = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
        outputs = model.generate(input_tensor.to(model.device), max_new_tokens=max_length)

        response = tokenizer.decode(outputs[0][input_tensor.shape[1]:], skip_special_tokens=True)
        return response
    elif args.model in ["mistral", "llama2", "llama3", "llama3-instruct", "xwin", "abel", "metamath", "wizard", "arithmo2", "mmiqc", "mammoth", "mammoth2", "openmath"]:
        use_4bit = True
        # Compute dtype for 4-bit base models
        bnb_4bit_compute_dtype = "bfloat16"  # Efficient. Newer GPUs support bfloat16 
        # Quantization type (fp4 or nf4)
        bnb_4bit_quant_type = "nf4"
        # Activate nested quantization for 4-bit base models (double quantization)
        use_nested_quant = False
        
        compute_dtype = getattr(torch, bnb_4bit_compute_dtype)

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=use_4bit,
            bnb_4bit_quant_type=bnb_4bit_quant_type,
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_use_double_quant=use_nested_quant,
        )
        model = AutoModelForCausalLM.from_pretrained(
            engine,
            quantization_config=bnb_config,
            device_map="auto",
        )
        
        tokenizer = AutoTokenizer.from_pretrained(engine, device_map="auto", trust_remote_code=True, use_fast=False)
        model.generation_config = GenerationConfig.from_pretrained(engine)
        model.generation_config.pad_token_id = model.generation_config.eos_token_id
        input_tensor = tokenizer(input, return_tensors="pt")
        outputs = model.generate(**input_tensor.to(model.device), max_new_tokens=max_length, do_sample=True, temperature=0.0001)
        response = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        return response
    else:
        raise ValueError("model is not properly defined ...")


class Decoder():
    def __init__(self, args):
        print_now()

    def decode(self, args, input, max_length):
        try:
            if args.model == "gpt4" or args.model == "gpt3":
                while True:
                    try:
                        ret = decoder_for_response(args, input, max_length)
                        break
                    except Exception as e:
                        print(f"Failed to connect to OpenAI API: {e}")
                return ret
            elif args.model == "gemini":
                ret = None
                while True:
                    try:
                        response = decoder_for_response(args, input, max_length)
                        assert hasattr(response, 'text')
                        ret = response.text
                        break
                    except Exception as e:
                        if 'Resource has been exhausted' in str(e) or '429 Quota exceeded' in str(e):
                            continue
                        elif 'block_reason: OTHER' in str(e):
                            if ret is None:
                                print(f'[ERROR] blocked, output random prediction')
                                ret = "no response"
                            break
                        elif 'if the prompt was blocked' in str(e):
                            if ret is None:
                                print(f'[ERROR] blocked, output random prediction')
                                ret = "no response"
                            break
                        else:
                            print(f'[ERROR] gemini failed: {e}')
                            ret = "no response"
                            break
                return ret
            elif args.model in ["deepseek", "llama2", "llama3", "llama3-instrcut", "mistral", "xwin", "abel", "metamath", "wizard", "arithmo2", "mmiqc", "mammoth", "mammoth2", "openmath"]:
                while True:
                    try:
                        ret = decoder_for_response(args, input, max_length)
                        break
                    except Exception as e:
                        print(f"Failed to connect to OpenAI API: {e}")
                return ret
            else:
                raise ValueError("model is not properly defined ...")
        except Exception as e:
            raise Exception(e)
            return None, e

