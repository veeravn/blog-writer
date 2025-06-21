# scripts/inference/score.py

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model = None
tokenizer = None

def init():
    global model, tokenizer
    from transformers import AutoModelForCausalLM, AutoTokenizer
    model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")

def run(input_data):
    prompt = input_data.get("prompt", "")
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=200)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"output": result}