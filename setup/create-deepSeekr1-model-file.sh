#!/bin/bash

# Variables
model_name="deepseek-r1:8b"
custom_model_name="crewai-DeepSeekr1"

# Get the base model
ollama pull $model_name

# Create the model file
ollama create $custom_model_name -f ./Llama3Modelfile