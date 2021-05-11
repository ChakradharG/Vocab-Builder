import requests
import pickle
import random


URL = 'https://api.dictionaryapi.dev/api/v2/entries/'
words = []


class Word:
	def __init__(self, word, wordClass, pron, meaning, syn, ex):
		self.word = word
		self.wordClass = wordClass
		self.pron = pron
		self.meaning = meaning
		self.inter = None
		self.examples = ex
		self.synonyms = syn

	def __str__(self):
		s = f'''\n
Word: {self.word}\n
Type: {self.wordClass}\n
Pronunciation: {self.pron}\n
Meaning: {self.meaning[:-1]}\n
My Interpretation: {self.inter}\n
Examples: {self.examples}\n
Synonyms: {self.synonyms}\n
'''
		return s


def storeData():
	print('Saving your work')
	with open('Vocabulary', 'wb') as file:
		pickle.dump(words, file)


def loadData():
	global words
	with open('Vocabulary', 'rb') as file:
		words = pickle.load(file)


def fetch(inp=None):
	if not inp:
		inp = input('Word? ')

	page = requests.get(f'{URL}en_GB/{inp}')
	[ body ] = page.json()

	word = body.get('word')

	pron = []
	for i in body.get('phonetics'):
		pron.append(i.get('text'))

	wordClass = []
	meaning = []
	syn = []
	ex = []
	for i in body.get('meanings'):
		wordClass.append(i.get('partOfSpeech'))
		for j in i.get('definitions'):
			meaning.append(j.get('definition'))
			if j.get('synonyms'):
				syn.extend(j.get('synonyms'))
			ex.append(j.get('example'))
		meaning.append('**********')
	
	temp = Word(word, wordClass, pron, meaning, syn, ex)
	print(temp)
	temp.inter = input('Interpretation? ')

	ch = input('Would you like to save this word?(Press y if yes) ').lower()
	if ch == 'y' and not search(word, False):
		words.append(temp)


def search(searchWord, show=True):
	for w in words:
		if w.word == searchWord:
			print(w) if show else print(f'\n{searchWord} is already in your vocabulary')
			return True

	if show:
		ch = input('Word not found. Would you like to add it?(Press y if yes) ').lower()
		if ch == 'y':
			fetch(searchWord)
	return False


def keyWordSearch(searchWords):
	temp = []
	for w in words:
		if (w.word.find(searchWords) != -1):
			temp.append(w)
		elif (any(map(lambda x: x.find(searchWords) != -1, w.meaning))):
			temp.append(w)
		elif (w.inter.find(searchWords) != -1):
			temp.append(w)
		elif (any(map(lambda x: x.find(searchWords) != -1, w.synonyms))):
			temp.append(w)

	if temp == []:
		print('\nNo matching words found')
		if len(searchWords.split(' ')) == 1:
			ch = input('Would you like to add it?(Press y if yes) ').lower()
			if ch == 'y':
				fetch(searchWords)
		return

	print('\n', list(map(lambda x: x.word, temp)), sep='')
	for w in temp:
		ch = input('\nContinue with the definitions?(Press n if no) ').lower()
		if ch == 'n':
			break
		print(w)


def update():
	searchWord = input('Word? ')
	for i in range(len(words)):
		if words[i].word == searchWord:
			print(words[i])
			words[i].inter = input('New Interpretation? ')
			break
	else:
		print('Word not found')


def test(reverse):
	qCnt = int(input('How many questions? '))
	index = int(input('From how many recent words?(Press 0 to include the entire Vocab) '))
	temp = words[-index:]
	x = len(temp)
	for i in range(min(qCnt, x)):
		w = random.randrange(0, x)
		if reverse:
			print(f'\n\n{temp[w].inter}\n', f'\n{temp[w].meaning[:-1]}')
		else:
			print(temp[w].word)
		input('Check (Press Enter) ')
		print(temp[w])
		temp.pop(w)
		x -= 1


def recall(temp):
	wordCount = len(temp)
	while wordCount > 0:
		x = input(f'Word?({wordCount} words left. Press n to stop) ').lower()
		if x == 'n':
			break
		for w in temp:
			if w.word == x:
				temp.remove(w)
				wordCount -= 1
				break
		else:
			print('Word not found')
	print(f'\nYou recalled {len(words) - wordCount} words')
	return temp


def dispVocab():
	for i, w in enumerate(words):
		if i % 10 == 0:
			print()
		print('{:<3} {:<19}'.format(i, w.word), end='')
	print(f'\n\nThere are {len(words)} words in your vocabulary')


def main():
	opCount = 0
	loadData()
	tempWords = None

	while True:
		opCount += 1
		try:
			ch = input('''
1. Take a test
2. Take a reverse test
3. Search for a word in your vocab
4. Search for a word through keywords in its meaning
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
				search(input('Word? '))
			elif ch == '4':
				keyWordSearch(input('Keyword(s)? '))
			elif ch == '5':
				fetch()
			elif ch == '6':
				dispVocab()
			elif ch == '7':
				update()
			elif ch == '8':
				storeData()
			elif ch == '9':
				if not tempWords:
					tempWords = words[:]
				tempWords = recall(tempWords)
			else:
				break
		except Exception as e:
			print(e)
			ch = input('\nWould you like to exit?(Press y if yes) ').lower()
			if ch == 'y':
				break
		if opCount % 5 == 0:
			print('\nAuto-', end='')
			storeData()

	storeData()


if __name__ == '__main__':
	main()
