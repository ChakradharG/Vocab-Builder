# Vocab-Builder
A comprehensive LLM-powered tool to help you improve your vocabulary. 

<br>

## Features
- AI-Powered Word Definitions
	- Generate comprehensive word definitions using local LLMs via Ollama
	- Includes usage examples, synonyms, and antonyms for each word
- Interactive Flashcards
	- Test your understanding with a flashcard-style quiz
	- Practice recalling meanings from words or vice-versa
- Personal Word Interpretations
	- Add your own interpretations for each new word
	- Enhance retention by describing your understanding in your own words
- Intelligent Word Search
	- Utilize LLM-powered search to find words in your vocabulary based on descriptions
	- Discover words that match concepts or ideas, even if you can't remember the exact term
- Auto-Save Progress
	- Automatically save your progress after each session
	- Never lose your hard work or newly learned vocabulary

<br>

## Getting Started
* Download [Ollama](https://ollama.com/) and a [model](https://ollama.com/library) of your choice
* Clone this repository
* `cd Vocab-Builder`
* Install the required modules (`pip install -r requirements.txt`)
* Update line 9 in `Vocab.py` with the name of the model you downloaded above (E.g: `MODEL = 'gemma:2b'`)

<br>

## How to Use
* Run Ollama (You can check whether Ollama is running or not by visiting http://localhost:11434/, you should see `Ollama is running` on this page)
* Run `Vocab.py`
