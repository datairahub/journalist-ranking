from urllib import request
import csv
from bs4 import BeautifulSoup

url = "https://elpais.com/"

response = request.Request(url)
pagedata = request.urlopen(response)
lectura_html = pagedata.read()

soup = BeautifulSoup(lectura_html, "html.parser")

notis = soup.select('.headline')

elpais_domain = 'https://elpais.com'

with open('elpaiscom.csv', mode='w') as output_file:
    writer = csv.writer(output_file, delimiter=',', quotechar='"',)
    for noti in notis:
        titulo = noti.get_text().strip().encode('utf-8')
        enlace = noti.select('a')[0]['href'].strip()
        if enlace.startswith('/'):
            enlace = elpais_domain + enlace
        writer.writerow([titulo, enlace])
