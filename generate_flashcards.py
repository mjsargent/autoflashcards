import os
import csv
import argparse
import openai  # For OpenAI API usage
import ollama  # For Ollama package usage
import tiktoken  # For token counting
import textwrap

import os
import argparse
import openai  # For OpenAI API usage
import ollama  # For Ollama package usage
import textwrap

def read_transcript(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        transcript = file.read()
    return transcript

def escape_field(field):
    """
    Escape tabs, newlines, and double quotes in the field.
    Enclose the field in double quotes if it contains special characters.
    """
    field = field.replace('"', '""')  # Escape double quotes by doubling them
    if any(char in field for char in ['\n', '\r', '\t', ';', ',', '"']):
        field = f'"{field}"'  # Enclose in double quotes
    return field

def parse_flashcards(flashcard_text):
    # Find the first occurrence of "Question:"
    start_index = flashcard_text.find('Question:')
    if start_index == -1:
        # No flashcards found
        return []

    # Keep only the text starting from the first "Question:"
    flashcard_text = flashcard_text[start_index:]

    # Split the text into flashcard pairs
    flashcard_pairs = flashcard_text.strip().split('Question:')

    flashcards = []
    for pair in flashcard_pairs:
        if pair.strip() == '':
            continue
        # Add back the "Question:" prefix for consistency
        pair = 'Question:' + pair.strip()
        # Split into lines
        lines = pair.strip().split('\n')
        question = ''
        answer_lines = []
        collecting_answer = False
        for line in lines:
            if line.startswith('Question:'):
                question = line.replace('Question:', '').strip()
                collecting_answer = False
            elif line.startswith('Answer:'):
                answer_line = line.replace('Answer:', '').strip()
                answer_lines.append(answer_line)
                collecting_answer = True
            else:
                if collecting_answer:
                    # Append continuation lines to the answer
                    answer_lines.append(line.strip())
        if question and answer_lines:
            answer = '\n'.join(answer_lines).strip()
            flashcards.append([question, answer])
    return flashcards

def count_tokens(text, model_name):
    # Use tiktoken to count tokens
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # Use a default encoding if the model is not recognized
        encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(text))
    return num_tokens

def generate_flashcards_openai(transcript, openai_model):
    flashcards = []
    print(f"Processing the transcript using OpenAI model '{openai_model}'...")
    prompt = f"""
You are a knowledgeable assistant that creates educational flashcards.

From the following transcript, generate as many flashcards as possible covering key historical points. Output only the flashcards in the following format:

Question: [Question]
Answer: [Answer]

Do not include any introductions, conclusions, or comments—only the flashcards.

Ensure that:
- The questions are clear.
- The answers are accurate and concise.

Transcript:
\"\"\"
{transcript}
\"\"\"
"""
    try:
        response = openai.ChatCompletion.create(
            model=openai_model,
            messages=[
                {"role": "system", "content": "You create educational flashcards for studying."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7,
        )

        flashcard_text = response['choices'][0]['message']['content'].strip()

        # Parse the generated flashcards
        cards = parse_flashcards(flashcard_text)
        flashcards.extend(cards)

    except Exception as e:
        print(f"An error occurred: {e}")
    return flashcards

def generate_flashcards_ollama(transcript, model_name):
    flashcards = []
    print(f"Processing the transcript using Ollama model '{model_name}'...")
    prompt = f"""
You are a knowledgeable assistant that creates educational flashcards.

From the following transcript, generate as many flashcards as possible covering key historical points. Output only the flashcards in the following format:

Question: [Question]
Answer: [Answer]

Do not include any introductions, conclusions, or comments—only the flashcards.

Ensure that:
- The questions are clear.
- The answers are accurate and concise.

Transcript:
\"\"\"
{transcript}
\"\"\"
Remember to output each flash card in the exact format:

Question: [Question] \n
Answer: [Answer] \n

Do not enumerate the cards.
"""
    try:
        # Use the ollama package to generate the response
        response = ollama.generate(
            model=model_name,
            prompt=prompt,
            options={
                'temperature': 0.01,
                'max_tokens': 128000,

            }
        )
        # Extract the output from the response
        flashcard_text = response['response'].strip()
        print(flashcard_text)

        # Parse the generated flashcards
        cards = parse_flashcards(flashcard_text)
        flashcards.extend(cards)

    except ollama.ResponseError as e:
        print(f"An error occurred: {e.error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return flashcards

def main():
    parser = argparse.ArgumentParser(description='Generate Anki flashcards from a transcript.')
    parser.add_argument('--transcript', type=str, default='ep1_1.txt', help='Path to the transcript file.')
    parser.add_argument('--output', type=str, default='flashcards.txt', help='Output text file for Anki import.')
    parser.add_argument('--model_type', type=str, choices=['openai', 'ollama'], default='ollama', help='Model type to use: "openai" or "ollama".')
    parser.add_argument('--model_name', type=str, default='llama3.1:8b', help='Name of the model to use.')
    parser.add_argument('--tags', type=str, default='', help='Space-separated tags to add to each note.')
    args = parser.parse_args()

    # Read the transcript
    transcript = read_transcript(args.transcript)

    flashcards = []

    if args.model_type == 'openai':
        # Ensure OpenAI API key is set
        if not openai.api_key:
            openai.api_key = os.getenv('OPENAI_API_KEY')
            if not openai.api_key:
                print("OpenAI API key not found. Please set it as an environment variable 'OPENAI_API_KEY'.")
                return

        # Check token length
        model_context_limit = 4096  # For gpt-3.5-turbo
        if 'gpt-4' in args.model_name:
            model_context_limit = 8192  # Adjust according to the model version
        elif 'llama3.1' in args.model_name:
            model_context_limit =  128000 # Adjust according to the model version
        total_tokens = count_tokens(transcript, args.model_name) + count_tokens(prompt_template, args.model_name)
        if total_tokens > model_context_limit:
            print(f"Transcript is too long ({total_tokens} tokens) for the model context limit ({model_context_limit} tokens). Please shorten the transcript or use a model with a larger context window.")
            return

        flashcards = generate_flashcards_openai(transcript, args.model_name)

    elif args.model_type == 'ollama':
        # Note: Ollama models may have different context limits
        # You can add token counting and limit checking if needed

        flashcards = generate_flashcards_ollama(transcript, args.model_name)

    else:
        print(f"Invalid model type: {args.model_type}")
        return

    if not flashcards:
        print("No flashcards were generated.")
        return

    # Write the flashcards to a text file compatible with Anki
    with open(args.output, 'w', encoding='utf-8') as outfile:
        # Optionally, include tags at the top of the file
        if args.tags:
            outfile.write(f"tags:{args.tags}\n")

        # Define the field separator (tab)
        separator = '\t'

        for card in flashcards:
            question = escape_field(card[0])
            answer = escape_field(card[1])

            # Write the fields separated by the separator
            outfile.write(f"{question}{separator}{answer}\n")

    print(f"Generated {len(flashcards)} flashcards. Saved to '{args.output}'.")

if __name__ == '__main__':
    main()
