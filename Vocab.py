import requests
import os
import pickle
import random
import json


URL = 'http://localhost:11434/api/generate'
MODEL = ''

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
	response = requests.post(url=URL, json=payload)
	return json.loads(response.json()['response'])


def fetch(word):

	pron = ''
	for i in body.find(class_= PRON_ID).contents:
		if type(i) == bs4.element.NavigableString:
			pron += i
		else:
			pron += i.contents[0]
	pron = pron.replace('\u2009', ' _')

	wordClass = []
	for i in body.find_all(class_= WORD_CLASS_ID):
		try:
			wordClass.append(str(i.contents[0].contents[0]))
		except:
			continue


	meaning = []
	for i in body.find_all(class_= TOP_MEANING_ID):
		for j in i.find_all(class_= MEANING_ID):
			x = ''
			for k in j.contents:
				if type(k) == bs4.element.NavigableString:
					x += k
				elif k.get('href', '') != '':
					if type(k.contents[0]) == bs4.element.NavigableString:
						x += k.contents[0]
					elif type(k.contents[0].contents[0]) == bs4.element.NavigableString:
						x += k.contents[0].contents[0]
			meaning.append(x.replace(':', '.'))
		meaning.append('**********')

	syn = []
	for i in body.find_all(class_= SYN_ID)[:5]:
		syn.append(str(i.contents[0]))

	ex = []
	for i in body.find_all(class_= EX_ID)[:3]:
		k = ''
		for j in i:
			if type(j) == bs4.element.NavigableString:
				k += j
			else:
				k += j.contents[0]
		ex.append(k)

	temp = Word(word, wordClass, pron, meaning, syn, ex)
	print(temp)
	temp.inter = input('Interpretation? ')

	ch = input('Would you like to save this word?(Press y if yes) ').lower()
	if ch == 'y':
		if trie.search(word) is not None:
			print(f'\n{word} is already in your vocabulary')
		else:
			words.append(newWord)
			trie.add(newWord)


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
5. Look up a new word online
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
				fetch()
			elif ch == '6':
				dispVocab()
			elif ch == '7':
				update(input('Word? '))
			elif ch == '8':
				storeData()
			elif ch == '9':
				recall(recalledWords)
			else:
				break
		except Exception as e:
			print(e)
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
