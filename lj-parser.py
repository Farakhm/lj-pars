import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
import datetime

# Программа для парсинга ЖЖ и снятия информации из него. 
# На данный момент работает с ограничениями:
# 1. Собирает данные по тэгам, а не "сплошняком". 
# Плюсы - когда смотришь так, нормально работает кнопка 
# Previous, в других случаях она быстро "ломается" и дальше приходится 
# шлёпать по дням. 
# Минусы - неразмеченные данные в выборку не попадают. 
# 2. Зависит от наличия заголовка (это я поправлю в ближайшее время) 
# 3. Не выдирает содержимое поста (сделать это относительно просто, 
# но вот куда потом кидать - тут вопрос, там может быть достаточно 
# большой текст). Так что пока только прямая ссылка. 
# 4. Тег вводится ручками 
# 5. Нет автоопределения количества постов на страницу (вшито 10)
# Большинство ограничений сниму в близкое время. 

def getdate(line):
    m1 = ['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December']
    year = int(line[4])
    month = m1.index(line[2]) + 1
    day = int(re.findall(r'\d+',line[3])[0])
    minut = int(re.findall(r'\d+', line[0])[1])
    hour = int(re.findall(r'\d+', line[0])[0])
    if line[1] == 'pm' or line[1] == 'PM':
        if hour != 12:
            hour = hour + 12
    res = datetime.datetime(year,month,day,hour,minut)
    return res


url = 'https://wim-winter.livejournal.com'

# Результат для простоты заталкиваем в DataFrame
result = pd.DataFrame()

r = requests.get(url)
filename = 'test.html'
with open(filename, 'w', encoding='utf8') as output_file:
  output_file.write(r.text)

soup = BeautifulSoup(r.text, features='lxml')
items = soup.find('ul',{'class':'ljtaglist'})
gost = items.find_all('a')

refs = []
numr = 0
num_r = []
r_dict = {}
i = 0

for line in gost:
    dean = line.get('href')
    num_p = int(re.findall(r'\d+', line.get('title'))[0])
    num_r.append(num_p)
    print(i, ': По тэгу', line.text, 'найдено', num_p, 'сообщений')
    refs.append(dean)
    numr = numr + num_p
    r_dict[dean] = num_p
    i += 1

print('Всего', len(refs), 'тэгов и', numr, 'сообщений')

# Интересующий нас тэг
num_tag = 34
link = refs[num_tag]
num_posts = r_dict.get(link)
print('*******************************')
num_dates = 0
print(link)
dattes = []
titles = []
links = []
comments = []

while True:
    r = requests.get(link)
    soup = BeautifulSoup(r.text, features='lxml')
    # Если количество постов по тэгу больше 10, тогда получаем ссылку на предыдущую страницу
    if num_posts > 10:
        prev = soup.find('div',{'class':'compList page-nav-link'})
        link = prev.find('a',{'class':'headerLinks'}).get('href')
    # Считаем количество комментариев
    comment = soup.find_all('div',{'class': 'entryComments entry-comments-control'})
    for line in comment:
        m1 = re.findall(r'\d+', line.text)
        if m1:
            num_com = int(m1[0])
        else:
            num_com = 0
        comments.append(num_com)
    # Определяем заголовки
    items = soup.find_all('div',{'class':'entryHeader'})
    for line in items:
        titles.append(line.find('a').text)
        links.append(line.find('a').get('href'))
    # Определяем дату
    dates = soup.find_all('div',{'class': 'entryDate thread-started-header'})
    num_d = len(dates)
    for line in dates:
        date_l = line.text
        dattes.append(getdate(date_l.split()))
    
    num_dates = num_dates + num_d
    if num_dates >= num_posts:
        print(num_dates, num_posts)
        break

result['Datetime'] = dattes
result['Link'] = links
result['Title'] = titles
result['Comments'] = comments

resfile = 'result.xlsx'
result.to_excel(resfile)

print('That\'s all!')