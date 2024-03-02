import requests
import os
import pickle
import random
import json


URL = 'http://localhost:11434/api/generate'
MODEL = ''
SYSTEM_PROMPT1 = '''
You are an expert linguist and educator specializing in vocabulary enhancement. Your task is to provide clear and informative definitions for words to help users expand their vocabulary. For the given word, please provide the word's:

1. part of speech
2. definitions
3. examples uses
4. synonyms
5. antonyms

Your response should be in valid JSON with the following format:

{
	"wordClass": "<part of speech>",
	"meaning": ["<definition 1>", "<definition 2>", ...],
	"examples": ["<example 1>", "<example 2>", ...],
	"synonyms": ["<synonym 1>", "<synonym 2>", ...],
	"antonyms": ["<antonym 1>", "<antonym 2>", ...]
}

Examples:

response 1: {
	"wordClass": "adjective",
	"meaning": ["Occurring at irregular intervals or only in a few places; scattered or isolated.", "Not constant, frequent, or predictable."],
	"examples": ["Sporadic rainfall during the drought period is not uncommon.", "The patient's symptoms are sporadic and difficult to diagnose accurately without thorough investigation."],
	"synonyms": ["Intermittent", "Irregular", "Infrequent"],
	"antonyms": ["Consistent", "Regular", "Frequent"]
}

response 2: {
	"wordClass": "noun",
	"meaning": ["A situation or problem that is impossible to solve.", "An overwhelming obstacle, challenge, or difficulty."],
	"examples": ["The mountain was so insurmountable; no one dared attempt it without proper equipment and training.", "Many found the political situation in certain countries to be an insurmountable task due to pervasive corruption and unrest."],
	"synonyms": ["insuperable", "unassailable"],
	"antonyms": ["solvable situation", "assailable"]
}
'''
SYSTEM_PROMPT2 = '''
You are an expert linguist. You will be provided with a list of words and a description in the following format:
{
	"words": ["word 1", "word 2", ...],
	"description": "description of some word"
}

Your task is to identify which words in the list strongly match the description, if a lot of words match then return the top 3 closest words. Your response should be in valid JSON with the following format:

{
	"matches": ["matching word 1", "matching word 2", "matching word 3"]
}

Examples:

response 1: {
	"matches": ["assiduous", "dilligent"]
}

response 2: {
	"matches": ["opulent", "ostentatious", "lavish"]
}
'''


class Word:
	def __init__(self, word, wordClass, meaning, examples, synonyms, antonyms):
		self.word = word
		self.wordClass = wordClass
		self.meaning = meaning
		self.inter = None
		self.examples = examples
		self.synonyms = synonyms
		self.antonyms = antonyms
		self.index = Word.n
		Word.n += 1

	def __str__(self):
		s = f'''\n
Word: {self.word}\n
Type: {self.wordClass}\n
Meaning: {self.meaning}\n
My Interpretation: {self.inter}\n
Examples: {self.examples}\n
Synonyms: {self.synonyms}\n
Antonyms: {self.antonyms}\n
--------------------------------------------------
'''
		return s


def storeData():
	print('Saving your work')
	with open('Vocabulary', 'wb') as file:
		pickle.dump(words, file)


def loadData():
	if os.path.exists('./Vocabulary'):
		with open('Vocabulary', 'rb') as file:
			return pickle.load(file)
	else:
		return {}


def callAPI(payload):
	try:
		response = requests.post(url=URL, json=payload)
		response.raise_for_status()
		return json.loads(response.json()['response'])
	except json.JSONDecodeError:
		ch = input('The model did not return valid JSON, do you want to try again?(Press y if yes) ').lower()
		if ch == 'y':
			return callAPI(payload)
		else:
			raise Exception('Invalid JSON Error')
	except:
		raise Exception('Ollama is not running')


def fetch(word):
	body = callAPI({
			'model': MODEL,
			'system': SYSTEM_PROMPT1,
			'prompt': word,
			'temperature': 0.0,
			'format': 'json',
			'stream': False
	})

	wordClass = body['wordClass']
	meaning = body['meaning']
	examples = body['examples']
	synonyms = body['synonyms']
	antonyms = body['antonyms']

	newW = Word(word, wordClass, meaning, examples, synonyms, antonyms)
	print(newW)
	newW.inter = input('Interpretation? ')

	ch = input('Would you like to save this word?(Press y if yes) ').lower()
	if ch == 'y':
		w = words.get(word, None)
		if w is not None:
			print(f'\n{word} is already in your vocabulary')
		else:
			words[word] = newW


def findByWord(word):
	w = words.get(word, None)
	if w is not None:
		print(w)
	else:
		ch = input('Word not found. Would you like to add it?(Press y if yes) ').lower()
		if ch == 'y':
			fetch(word)


def findByDescription(description):
	matches = []
	BATCH_SIZE = 200
	keys = list(words.keys())
	for i in range(0, Word.n, BATCH_SIZE):
		matches.extend(callAPI({
			'model': MODEL,
			'system': SYSTEM_PROMPT2,
			'prompt': '{' + f'"words": ["{"\", \"".join(keys[i:i+BATCH_SIZE])}"], "description": "{description}"' + '}',
			'temperature': 0.0,
			'format': 'json',
			'stream': False
		})['matches'])

	if matches == []:
		print('\nNo matching words found')
	else:
		print(f'\n{matches}')
		for word in matches:
			ch = input('\nContinue with the definitions?(Press n if no) ').lower()
			if ch == 'n':
				break
			print(words[word])


def update(word):
	w = words.get(word, None)
	if w is not None:
		print(w)
		w.inter = input('New Interpretation? ')
	else:
		print('Word not found')


def test(reverse):
	qCnt = int(input('How many questions? '))
	index = int(input('Sample from how many recent words?(Press 0 to include the entire Vocab) '))
	temp = list(words.values())[-index:]
	random.shuffle(temp)
	for i in range(min(qCnt, len(temp))):
		if reverse:
			print(f'\n\n{temp[i].inter}\n', f'\n{temp[i].meaning[:-1]}')
		else:
			print(temp[i].word)
		input('Check (Press Enter) ')
		print(temp[i])


def recall(recalledWords):
	remaining = Word.n - len(recalledWords)
	while remaining > 0:
		word = input(f'Word?({remaining} words left. Press n to stop) ').lower()
		if word == 'n':
			break
		if word in words:
			if word not in recalledWords:
				recalledWords.add(word)
				remaining -= 1
			else:
				print('You already recalled this word')
		else:
			print('Word not found')
	print(f'\nYou recalled {Word.n - remaining} words')
	if len(recalledWords) == Word.n:
		recalledWords.clear()


def dispVocab():
	for w in words.values():
		if w.index % 5 == 0:
			print()
		print('{:<3} {:<19}'.format(w.index, w.word), end='')
	print(f'\n\nThere are {len(words)} words in your vocabulary')


def main():
	opCount = 0
	recalledWords = set()

	while True:
		opCount += 1
		try:
			ch = input('''
1. Take a test
2. Take a reverse test
3. Search for a word in your vocab
4. Search for a word in your vocab by describing it
5. Look up the definition of a new word
6. Explore your vocab
7. Update a word
8. Save progress made in current session
9. Recall all words in your vocab
0. Exit
''')

			if ch == '1':
				test(False)
			elif ch == '2':
				test(True)
			elif ch == '3':
				findByWord(input('Word? '))
			elif ch == '4':
				findByDescription(input('How would you describe the word? '))
			elif ch == '5':
				fetch(input('Word? '))
			elif ch == '6':
				dispVocab()
			elif ch == '7':
				update(input('Word? '))
			elif ch == '8':
				storeData()
				opCount = 0
			elif ch == '9':
				recall(recalledWords)
			else:
				break
		except Exception as e:
			print(f'Encountered error: {e}')
			ch = input('\nWould you like to exit?(Press y if yes) ').lower()
			if ch == 'y':
				break
		if opCount == 5:
			storeData()
			opCount = 0

	storeData()


if __name__ == '__main__':
	words = loadData()
	Word.n = len(words)
	main()
