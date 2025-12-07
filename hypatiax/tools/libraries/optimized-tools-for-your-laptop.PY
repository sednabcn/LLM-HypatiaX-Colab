
📊 Optimization Tips for Your Laptop
1. Reduce Batch Size
python# In your training config
config_training = {
    'batchsize': 4,  # Reduce from 8 to 4 or even 2
    'niter': 400,
    'patience': 10,
}
2. Use Mixed Precision (even on CPU)
pythonfrom torch.cuda.amp import autocast

# Works on some CPUs
with autocast(device_type='cpu', dtype=torch.bfloat16):
    outputs = model(**inputs)
3. Enable Threading
pythonimport torch

# Optimize CPU threading
torch.set_num_threads(4)  # Adjust based on your CPU cores
torch.set_num_interop_threads(4)
4. Monitor Memory Usage
pythonimport psutil

def log_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")

# Call this during training
log_memory_usage()
