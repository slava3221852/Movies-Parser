from bs4 import BeautifulSoup
from urllib.request import urlopen
from multiprocessing import Pool
import sqlite3

conn = sqlite3.connect(r"C:\Users\user\Desktop\Django-Parser\db.db3")
Base_Url = 'http://www.torrentino.online'

def reloadDictionary():
    return {'Название': None,
            'Год': None,
            'Длительность': None, 
            'Страна': None, 
            'Жанр': None, 
            'Бюджет': None, 
            'Magnet-link': None, 
            'Image': None, 
            'Video': None, 
            'Рейтинг': None
            }

def writeInformations(dictionary):
    key = list(map(str, dictionary.keys()))
    value = list(map(str, dictionary.values()))
    conn.execute("INSERT INTO Movies ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}') VALUES ('{10}', '{11}', '{12}', '{13}', '{14}', '{15}', '{16}', '{17}', '{18}', '{19}')".format(
        *key, *value
        ))
    conn.commit()

def getMaxPage():
    Page_count = BeautifulSoup(urlopen('http://www.torrentino.online/movies?quality=hq&years=2017').read(), 'html.parser').find('div', class_='plate showcase')
    return max([int(i.text) for i in Page_count.find('ul', class_='pagination').find_all('li') if i.text.strip().rstrip().isdigit()])

def getLinks():
    links = []
    for page in range(1, getMaxPage()+1):
        link = 'http://www.torrentino.online/movies?page={0}&quality=hq&years=2017'.format(page)
        Soup = BeautifulSoup(urlopen(link).read(), 'html.parser').find('div', class_='plate showcase')
        for i in Soup.find('div', class_='tiles').find_all('div', class_='tile'):
            try:
                links.append(i.a['href'])
            except TypeError:
                pass
    return links

def getInformations(link):
    Flag = str()
    Name = BeautifulSoup(urlopen(Base_Url + link).read(), 'html.parser').find('div', class_='header-group').h1.text
    Soup = BeautifulSoup(urlopen(Base_Url + link), 'html.parser').find('div', class_='section numbers')
    Flag = str()
    dictionary = reloadDictionary()
    dictionary['Название'] = Name.strip().rstrip()
    for i in Soup.table.find_all('td'):
        if Flag:
            dictionary[Flag] = i.text.strip().rstrip()
            Flag = str()
            continue
        if i.text.strip().rstrip() in dictionary:
            Flag = i.text.strip().rstrip()
    writeInformations(dictionary)

def main():
    links = getLinks()
    with Pool(12) as stack:
        stack.map(getInformations, links)

if __name__ == '__main__':
    main()
