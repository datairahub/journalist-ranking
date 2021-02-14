import re
import os
import csv
import time
import zlib
import datetime
from urllib import request
from bs4 import BeautifulSoup

OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'elpaiscom')
PORTADA = "https://elpais.com/"
ARCHIVO_INDICE = 'index.csv'
ARCHIVO_AUTORES = 'authors.csv'
BASE_DOMAIN = 'https://elpais.com'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Content-Type': 'application/json; charset=UTF-8',
}


def parse_elpaiscom_date(datestr):
    months_dict = {
        'ene': '01',
        'feb': '02',
        'mar': '03',
        'abr': '04',
        'may': '05',
        'jun': '06',
        'jul': '07',
        'ago': '08',
        'sep': '09',
        'pct': '10',
        'nov': '11',
        'dic': '12',
    }
    matchs = re.search('\d+ \w{3} \d{4}', datestr)
    day_matchs = re.search('\d+', datestr)
    month_matchs = re.search('\w{3}', datestr)
    year_matchs = re.search('\d{4}', datestr)
    fecha = matchs[0]
    year = year_matchs[0]
    day = day_matchs[0]
    month = months_dict.get(month_matchs[0])

    return f"{year}-{month}-{day}"

def scraper_portada():
    response = request.Request(PORTADA)
    pagedata = request.urlopen(response)
    lectura_html = pagedata.read()
    soup = BeautifulSoup(lectura_html, "html.parser")

    notis = soup.select('.headline')
    output_path = os.path.join(OUTPUT_FOLDER, ARCHIVO_INDICE)

    with open(output_path, mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"',)
        for noti in notis:
            titulo = noti.get_text().strip().encode('utf-8')
            if len(noti.select('a')):
                enlace = noti.select('a')[0]['href'].strip()
                if enlace.startswith('/'):
                    enlace = BASE_DOMAIN + enlace
                writer.writerow([titulo, enlace])


def scraper_articulos():
    source_path = os.path.join(OUTPUT_FOLDER, ARCHIVO_INDICE)
    output_path = os.path.join(OUTPUT_FOLDER, ARCHIVO_AUTORES)
    articles_dir = os.path.join(OUTPUT_FOLDER, 'articles')

    with open(output_path, mode='a+', newline='') as autores_file:
        writer = csv.writer(autores_file, delimiter=',', quotechar='"',)

        with open(source_path, mode='r') as indice_file:
            rows = csv.reader(indice_file, delimiter=',')
            for row in rows:
                if len(row) and row[1].startswith(BASE_DOMAIN):
                    enlace = row[1]
                    time.sleep(1)
                    print('Enlace:', enlace)

                    # Get article name
                    nombre = enlace.replace('https://elpais.com/', '').replace('/', '').replace('-', '').replace('_', '').replace('.', '').replace('&', '').replace('?', '')
                    nombre += '.txt'

                    response = request.Request(enlace, headers=HEADERS)
                    pagedata = request.urlopen(response)
                    if pagedata.info().get('Content-Encoding') == 'gzip':
                        lectura_html = zlib.decompress(pagedata.read(), 16+zlib.MAX_WBITS)
                    else:
                        lectura_html = pagedata.read()

                    soup = BeautifulSoup(lectura_html, "html.parser")

                    sections = soup.select('.article_body p')
                    if not len(sections):
                        sections = soup.select('.articulo-cuerpo p')

                    if not len(soup.select('.a_h .a_pt .a_ti')):
                        if len(soup.select('[name="date"]')):
                            fechas = soup.select('[name="date"]')
                        else:
                            fechas = soup.select('[name="DC.date"]')
                        fecha = fechas[0]['content'][:10]
                    else:
                        fechas = soup.select('.a_h .a_pt .a_ti')
                        fecha = fechas[0].get_text()

                    autores = soup.select('.a_auts .a_aut')
                    autor_class = '.a_aut_n'
                    autor_twitter_class = '.twitter'
                    if not len(autores):
                        autor_class = '.autor-texto a'
                        autor_twitter_class = '.boton_twitter'
                        autores = soup.select('.firma .autor')

                    for autor in autores:

                        # Get author profile
                        if len(autor.select(autor_class)):
                            autor_nombre = autor.select(autor_class)[0].get_text().encode('utf-8')
                            autor_enlace = autor.select(autor_class)[0]['href']
                        else:
                            autor_nombre = '?'
                            autor_enlace = ''

                        # Get author twitter profile
                        if len(autor.select(autor_twitter_class)):
                            autor_twitter = autor.select(autor_twitter_class)[0]['href']
                        else:
                            autor_twitter = ''

                        writer.writerow([
                            autor_nombre, autor_enlace, autor_twitter, len(autores), enlace, nombre, fecha
                        ])

                    # Save articles on .txt files
                    article_path = os.path.join(articles_dir, nombre)
                    with open(article_path, mode='w', newline='') as article_file:
                        for section in sections:
                            article_file.write(str(section.get_text().encode('utf-8')))


if __name__ == "__main__":
    # scraper_portada()
    scraper_articulos()
