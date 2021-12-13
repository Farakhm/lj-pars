import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
import datetime

def getdate(line, flag):
    m1 = ['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December']
    if flag == 0:
        year = int(re.findall(r'\d+',line[2])[0])
        month = m1.index(line[0]) + 1
        day = int(re.findall(r'\d+',line[1])[0])
        m2 = line[3].split(':')
        minut = int(m2[1])
        hour = int(m2[0])
        sec = 0
        if line[4] == 'pm' or line[1] == 'PM':
            if hour != 12:
                hour = hour + 12
    else:
        m1 = line[0].split('-')
        m2 = line[1].split(':')
        year = int(m1[0])
        month = int(m1[1])
        day = int(m1[2])
        hour = int(m2[0])
        minut = int(m2[1])
        sec = int(m2[2])
    res = datetime.datetime(year,month,day,hour,minut,sec)
    return res

# It is last LJ record
prev = 'https://***.livejournal.com/***.html'
content = []
links = []
dates = []
title = []
cycle = True
i = 1

while cycle:
    r = requests.get(prev)
    soup = BeautifulSoup(r.text, features='lxml')
    items = soup.find_all('meta',{'property':'og:url'})
    if len(items) > 0:
        links.append(items[0].get('content'))
    else:
        links.append('no answer')
    items = soup.find_all('article', {'class': 'b-singlepost-body entry-content e-content'})
    if len(items) > 0:
        content.append(items[0].text)
    else:
        content.append('no answer')
    items = soup.find_all('time')
    if len(items) > 0:
        dates.append(getdate(items[0].text.split(), 1))
    else:
        dates.append(' ')
    items = soup.find_all('meta',{'property':'og:title'})
    if len(items) > 0:
        title.append(items[0].get('content'))
    else:
        title.append('no title')
    finish = 0
    prext = soup.find_all('div',{'class':'b-singlepost-standout'})
    if len(prext) > 0:
        preext = prext[0].text
        if preext.find('Previous') != -1:
            prev = prext[0].find('a').get('href')
            finish = 1
    else:
        preext = ''
    print(i, finish, dates[i - 1])
    if finish == 0:
      cycle = False
    i += 1

result = pd.DataFrame()

result['Datetime'] = dates
result['Link'] = links
result['Title'] = title
result['Text'] = content

resfile = 'Res\\result_all.xlsx'
result.to_excel(resfile)

print('That\'s all!')