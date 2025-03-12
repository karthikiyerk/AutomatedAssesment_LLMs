#!/bin/bash

# Variables
model_name="dolphin-llama3"
custom_model_name="crewai-dolphin"

# Get the base model
ollama pull $model_name

# Create the model file
ollama create $custom_model_name -f ./DolphinModelfile