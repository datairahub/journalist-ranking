# -*- coding: UTF-8 -*-
import os
import csv
import re

INPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'elpaiscom')
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
ARCHIVO_AUTORES = 'authors.csv'
ARCHIVO_FINAL = 'uniquewords.csv'


def clean_unwanted_chars(article):
    article_cleaned = re.sub(r'#(\w+)', '', article)
    article_cleaned = re.sub(r'\d', '', article_cleaned)
    article_cleaned = re.sub(r'\.|,|:|;|º|ª|\||/|\\|\?|\¿|\!|\¡|\(|\)|\[|\]|\{|\}|\%', '', article_cleaned)
    article_cleaned = re.sub(r'“|”|"|\'|-|–|—|―|_|`|‘|’', '', article_cleaned)

    article_cleaned = article_cleaned.replace('  ', ' ').replace('  ', ' ')
    return article_cleaned.lower()


def export_authors(authors):
    output_file = os.path.join(OUTPUT_FOLDER, ARCHIVO_FINAL)

    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"',)
        writer.writerow(['autor_nombre', 'total_articulos', 'total_palabras', 'palabras_unicas'])

        for author in authors:
            unique_words = len(authors[author]['words'].items())
            total_words = authors[author]['total_words']
            percent = unique_words * 100 / total_words
            # words = sorted(authors[author]['words'].items(), key=lambda x: x[1], reverse=True)
            writer.writerow([
                author, authors[author]['articles'], total_words, unique_words
            ])


def contar_palabras():
    authors = {}
    index_file = os.path.join(INPUT_FOLDER, ARCHIVO_AUTORES)

    with open(index_file, mode='r', newline='') as indice_file:
        rows = csv.reader(indice_file, delimiter=',')

        for row in rows:

            author = row[0]
            article_file = os.path.join(INPUT_FOLDER, 'articles', row[5])

            if not author in authors:
                authors[author] = {
                    "articles": 1,
                    "total_words": 0,
                    "words": {},
                }
            else:
                authors[author]['articles'] += 1

            with open(article_file, mode='r') as article:
                contents = article.read()
                contents_cleaned = clean_unwanted_chars(contents)
                for word in contents_cleaned.split(' '):
                    if len(word) < 2:
                        continue

                    authors[author]['total_words'] += 1

                    if not word in authors[author]['words']:
                        authors[author]['words'][word] = 1
                    else:
                        authors[author]['words'][word] += 1

    export_authors(authors)



if __name__ == "__main__":

    contar_palabras()