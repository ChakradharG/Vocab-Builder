import requests
import bs4
import pickle
import random


URL = f'https://dictionary.com/'
words = []
letters = [chr(i) for i in range(65, 91)]

# HTML ID Strings
LAST_PAGE_ID = 'css-3w1ibo e1wvt9ur6'
WORD_LIST_ID = 'css-1y59cbu e1j8zk4s0'
WORD_ID = 'css-2m2rhw e1wg9v5m3'
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
	with open('Vocabulary', 'wb') as file:
		pickle.dump(words, file)


def loadData():
	global words
	with open('Vocabulary', 'rb') as file:
		words = pickle.load(file)


def fetch(rand=True):
	inp = ''
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

	else:
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
				else:
					if k.get('href', '') != '':
						x += k.contents[0]
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

	ch = input('Would you like to save this word?(Press y if yes) ')
	if (ch == 'y' or ch == 'Y') and not search(word, False):
		words.append(temp)


def search(searchWord, show=True):
	for w in words:
		if w.word == searchWord:
			print(w) if show else print(f'\n{searchWord} is already in your vocabulary')
			return True
	if show:
		print('Word not found')
	return False


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
	temp = words[:]
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
		print('{:<20}'.format(w.word), end='')
	print(f'\n\nThere are {len(words)} words in your vocabulary')


def main():
	loadData()

	while True:
		try:
			ch = input('''
1. Take a test
2. Take a reverse test
3. Search for a word in your vocab
4. Look up a new word online
5. Look up a new random word online
6. Explore your vocab
7. Update a word
8. Exit
''')

			if ch == '1':
				test(False)
			elif ch == '2':
				test(True)
			elif ch == '3':
				search(input('Word? '))
			elif ch == '4':
				fetch(False)
			elif ch == '5':
				fetch()
			elif ch == '6':
				dispVocab()
			elif ch == '7':
				update()
			else:
				break
		except Exception as e:
			print(e)
			ch = input('\nWould you like to exit?(Press y if yes) ')
			if (ch == 'y' or ch =='Y'):
				break

	storeData()


if __name__ == '__main__':
	main()
