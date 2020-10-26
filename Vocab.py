import requests
import bs4
import pickle
import random


URL = f'https://dictionary.com/'
words = []
letters = [chr(i) for i in range(65, 91)]


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
		last = soup.find(class_='css-3w1ibo e1wvt9ur6').contents[0]
		num = ''
		for i in last['href'][::-1]:
			if i == '/':
				break
			num = i + num
		num = random.randint(1, int(num))

		pre = requests.get(f'{URL}list/{let}/{num}')
		soup = bs4.BeautifulSoup(pre.text, 'html.parser')
		lis = soup.find(class_='css-1y59cbu e1j8zk4s0').contents
		num = random.randint(1, len(lis))
		inp = lis[num].contents[0].contents[0]

	else:
		inp = input('Word? ')
	
	page = requests.get(f'{URL}browse/{inp}')
	soup = bs4.BeautifulSoup(page.text, 'html.parser')
	body = soup.find('body')

	word = str(body.find(class_='css-13gkw1x e1rg2mtf5').contents[0])

	pron = ''
	for i in body.find(class_='pron-spell-content css-cqidvf evh0tcl2').contents:
		if type(i) == bs4.element.NavigableString:
			pron += i
		else:
			pron += i.contents[0]
	pron = pron.replace('\u2009', ' _')

	wordClass = []
	for i in body.find_all(class_='css-chpztc e1hk9ate2'):
		try:
			wordClass.append(str(i.contents[0].contents[0]))
		except:
			continue


	meaning = []
	for i in body.find_all(class_='css-1o58fj8 e1hk9ate4'):
		for j in i.find_all(class_='one-click-content css-17f75g0 e1q3nk1v4'):
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
	for i in body.find_all(class_='css-cilpq1 e15p0a5t1')[:5]:
		syn.append(str(i.contents[0]))

	ex = []
	for i in body.find_all(class_='one-click-content css-1pfxpp4 e15kc6du6')[:3]:
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
	if ch == 'y' or ch == 'Y':
		words.append(temp)


def search():
	inp = input('Word? ')
	for w in words:
		if w.word == inp:
			print(w)
			break
	else:
		print('Word not found')


def test():
	qCnt = int(input('How many questions? '))
	temp = words[:]
	x = len(temp)
	for i in range(min(qCnt, x)):
		w = random.randrange(0, x)
		print(temp[w].word)
		input('Check (Press Enter) ')
		print(temp[w])
		temp.pop(w)
		x -= 1


def dispVocab():
	print(f'\nThere are {len(words)} words in your vocabulary')
	for w in words:
		print(w.word)


def main():
	loadData()

	try:
		while True:
			ch = input('''
1. Take a test
2. Search for a word in your vocab
3. Look up a new word online
4. Look up a new random word online
5. Explore your vocab
6. Exit
''')

			if ch == '1':
				test()
			elif ch == '2':
				search()
			elif ch == '3':
				fetch(False)
			elif ch == '4':
				fetch()
			elif ch == '5':
				dispVocab()
			else:
				break
	except Exception as e:
		print(e)
		input('Press enter to exit')

	storeData()


if __name__ == '__main__':
	main()
