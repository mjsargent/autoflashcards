# Podcast Flashcard Generator

Generate Anki-compatible flashcards from podcast transcripts using AI models (OpenAI or Ollama).

## Features

- Convert podcast transcripts into study-ready flashcards
- Support for both OpenAI and Ollama AI models
- Anki-compatible output format
- Configurable chunk sizes and model parameters

This is very much a work in progress. This will not work for you out of the box - I currently have PodcastAddict syncing backup files to the cloud and then downloading them to my local machine, which I parse to get RSS URLs. I'll work on a more generic solution in the future.

## Prerequisites

- Python 3.9+
- Conda package manager
- OpenAI API key (if using OpenAI)
- Ollama installed locally (if using Ollama)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/podcast-flashcard-generator
   cd podcast-flashcard-generator
   ```

2. Create and activate the conda environment:
   ```bash
   conda env create -f environment.yml
   conda activate flashcard-generator
   ```

3. Configure API keys:
   - For OpenAI:
     ```bash
     export OPENAI_API_KEY='your-api-key-here'
     ```
   - For Ollama:
     Ensure Ollama is installed and running locally

## Usage

1. Place your transcript file in the `transcripts` directory

2. Generate flashcards:
   ```bash
   python generate_flashcards.py --transcript transcripts/your_file.txt --output output/flashcards.txt
   ```

### Command Line Options

- `--transcript`: Path to the transcript file (default: 'ep1_1.txt')
- `--output`: Path for the output flashcards (default: 'flashcards.txt')
- `--model`: AI model to use ('openai' or 'ollama', default: 'openai')
- `--model-name`: Specific model name (default: 'gpt-3.5-turbo')
- `--chunk-size`: Maximum tokens per chunk (default: 3000)

## Directory Structure
