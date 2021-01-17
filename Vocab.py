import requests
import bs4
import pickle
import random


URL = 'https://dictionary.com/'
words = []
letters = [chr(i) for i in range(65, 91)]

# HTML ID Strings
LAST_PAGE_ID = 'css-3w1ibo e1wvt9ur6'
WORD_LIST_ID = 'css-1y59cbu e1j8zk4s0'
WORD_ID = 'css-2m2rhw e1wg9v5m4'
PRON_ID = 'pron-spell-content css-1k8pnqm evh0tcl2'
WORD_CLASS_ID = 'css-chpztc e1hk9ate2'
TOP_MEANING_ID = 'css-1o58fj8 e1hk9ate4'
MEANING_ID = 'one-click-content css-17f75g0 e1q3nk1v4'
SYN_ID = 'css-cilpq1 e15p0a5t1'
EX_ID = 'one-click-content css-1pfxpp4 e15kc6du6'


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


def fetch(rand=True, inp=None):
	if rand:
		let = random.choice(letters)
		pre = requests.get(f'{URL}list/{let}')
		soup = bs4.BeautifulSoup(pre.text, 'html.parser')
		last = soup.find(class_= LAST_PAGE_ID).contents[0]
		num = ''
		for i in last['href'][::-1]:
			if i == '/':
				break
			num = i + num
		num = random.randint(1, int(num))

		pre = requests.get(f'{URL}list/{let}/{num}')
		soup = bs4.BeautifulSoup(pre.text, 'html.parser')
		lis = soup.find(class_= WORD_LIST_ID).contents
		num = random.randint(1, len(lis))
		inp = lis[num].contents[0].contents[0]
	elif inp == None:
		inp = input('Word? ')
	
	page = requests.get(f'{URL}browse/{inp}')
	soup = bs4.BeautifulSoup(page.text, 'html.parser')
	body = soup.find('body')

	word = str(body.find(class_= WORD_ID).contents[0])

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
			fetch(False, searchWord)
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
				fetch(False, searchWords)
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


def dispVocab():
	for i, w in enumerate(words):
		if i % 10 == 0:
			print()
		print('{:<3} {:<19}'.format(i, w.word), end='')
	print(f'\n\nThere are {len(words)} words in your vocabulary')


def main():
	opCount = 0
	loadData()

	while True:
		opCount += 1
		try:
			ch = input('''
1. Take a test
2. Take a reverse test
3. Search for a word in your vocab
4. Search for a word through keywords in its meaning
5. Look up a new word online
6. Look up a new random word online
7. Explore your vocab
8. Update a word
9. Save progress made in current session
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
				fetch(False)
			elif ch == '6':
				fetch()
			elif ch == '7':
				dispVocab()
			elif ch == '8':
				update()
			elif ch == '9':
				storeData()
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
