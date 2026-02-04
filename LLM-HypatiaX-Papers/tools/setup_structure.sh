#!/bin/bash

# Create experiments/hypatiax structure
mkdir -p experiments/hypatiax/{core,tools,data,results,visualizations}

# Create core subdirectories
mkdir -p experiments/hypatiax/core/{preprocessing,training,deployment,evaluation}

# Create latex/Bib directory
mkdir -p latex/Bib

echo "LLM-HypatiaX-Colab structure created!"
