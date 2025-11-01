# Model Folder

Place your GGUF model file here and name it `model.gguf`

## How to Get a GGUF Model

You can download GGUF models from:
- **Hugging Face**: https://huggingface.co/models?search=gguf
- Popular models:
  - Llama 3.2 (3B): https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF
  - Phi-3 (3.8B): https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf
  - Mistral (7B): https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF

## Recommended Models

For best performance:
- **Small models (3-4GB RAM)**: Llama-3.2-3B, Phi-3-mini
- **Medium models (8GB RAM)**: Mistral-7B, Llama-2-7B
- **Large models (16GB+ RAM)**: Llama-2-13B, Mistral-7B-Q8

## Instructions

1. Download a GGUF model file (`.gguf` extension)
2. Rename it to `model.gguf`
3. Place it in this `model` folder
4. Restart the application

The chatbot will automatically load and use this local model!
