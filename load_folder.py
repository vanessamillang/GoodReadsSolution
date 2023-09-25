import redis
import os
import re
from bs4 import BeautifulSoup
import itertools

r = redis.Redis(host='localhost', port=6379, db=0)

def load_folder(path):
    files = os.listdir(path)
    print(files)
    for file in files:
        match = re.match(r'^book(\d+).html$', file)
        if match:
            with open(path + file) as f:
                html = f.read()
                book_id = match.group(1)

                r.set(match.group(1), html)
                create_index(book_id, html)
            print(match.group(0), match.group(1))

def create_index(book_id, html):
    soup = BeautifulSoup(html, 'html.parser')
    texto = soup.get_text()
    
    palabras = re.findall(r'\w+', texto, re.IGNORECASE)
    
    for palabra in palabras:
        palabra_lower = palabra.lower()
        r.sadd(palabra, book_id)  # Original 
        r.sadd(palabra_lower, book_id)  # Minúsculas
        r.sadd(palabra.upper(), book_id)  # Mayúsculas
        
        combinaciones = [''.join(p) for p in itertools.product(*zip(palabra_lower, palabra_lower.upper()))]
        for combinacion in combinaciones:
            r.sadd(combinacion, book_id)

load_folder('html/books/')
