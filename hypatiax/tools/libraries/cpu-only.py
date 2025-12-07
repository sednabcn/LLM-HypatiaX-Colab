# Option 1: Use CPU-Only (Simplest)
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Force CPU usage
device = torch.device("cpu")

# Load model on CPU
model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device)

# Use the model
inputs = tokenizer("Hello, world!", return_tensors="pt").to(device)
outputs = model(**inputs)

# ==============================================
# KEY SETTINGS

# In your training loop
model.to("cpu")

# Or set environment variable before importing
import os

os.environ["CUDA_VISIBLE_DEVICES"] = ""

# ==============================================
