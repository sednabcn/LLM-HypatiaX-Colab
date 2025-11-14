#  Option 2: Use Optimized CPU Libraries
#  Intel Extension for PyTorch (Best for Intel CPUs)
bash
pip install intel-extension-for-pytorch
python

import torch
import intel_extension_for_pytorch as ipex

model = AutoModelForSequenceClassification.from_pretrained(model_name)
model = model.to('cpu')
model = ipex.optimize(model)  # Optimize for Intel CPU
ONNXRuntime (Fast inference)
bash
pip install optimum[onnxruntime]
python

from optimum.onnxruntime import ORTModelForSequenceClassification

# Convert and load as ONNX (much faster on CPU)
model = ORTModelForSequenceClassification.from_pretrained(
    model_name,
    export=True,
    provider="CPUExecutionProvider"
)

#🔧 Option 3: Use Smaller/Quantized Models
#Load Quantized Models
python

from transformers import AutoModelForSequenceClassification

# Use quantization for faster CPU inference
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    torch_dtype=torch.float16,  # Half precision
    low_cpu_mem_usage=True
)

# Or use 8-bit quantization
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    bnb_4bit_compute_dtype=torch.float16
)
# Use Smaller Models
python

# Instead of large models, use distilled versions
model_options = [
    "distilbert-base-uncased",      # 66M params (vs BERT 110M)
    "microsoft/MiniLM-L12-H384",    # 33M params
    "prajjwal1/bert-tiny",          # 4.4M params
    "sentence-transformers/all-MiniLM-L6-v2"  # Fast embeddings
]

#🚀 Option 4: For Your Specific Case (SpaCy NER)

#Since you're working with SpaCy NER, here's how to optimize:

#CPU-Optimized SpaCy Training
python

import spacy
from spacy.training import Example

# Use CPU-optimized settings
config = {
    "nlp": {
        "pipeline": ["tok2vec", "ner"],
        "disabled": [],
        "before_creation": None,
        "after_creation": None,
        "after_pipeline_creation": None,
        "batch_size": 128  # Smaller batches for CPU
    },
    "training": {
        "max_epochs": 20,
        "patience": 5,
        "eval_frequency": 100,
        "dropout": 0.5,
        "accumulate_gradient": 1,
        # Optimize for CPU
        "gpu_allocator": None,
        "seed": 0
    }
}

# Create and configure
nlp = spacy.blank("en")
nlp.add_pipe("ner")

# Train with CPU optimization
with nlp.select_pipes(enable=["ner"]):
    optimizer = nlp.resume_training()
    
    for epoch in range(20):
        for batch in spacy.util.minibatch(train_data, size=8):  # Small batches
            nlp.update(batch, sgd=optimizer, drop=0.5)


# Use SpaCy's CPU-Optimized Models

bash
# Download CPU-optimized models

python -m spacy download en_core_web_sm  # Smallest, fastest
python -m spacy download en_core_web_md  # Medium
python -m spacy download en_core_web_lg  # Large but still fast on CPU
