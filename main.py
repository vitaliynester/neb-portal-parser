import grequests
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/v1/svet")
async def svet():
    result = []
    url = 'https://rusneb.ru/search/?f_field[publisher]=f%2Fpublisher%2FНЭБ+Свет&PAGEN_1=2'
    response = requests.get(url)
    if response.status_code != 200:
        return {"data": []}
    soup = BeautifulSoup(response.text, 'lxml')
    page_count = soup.find('title').string.split('|')[0].split()[-1]
    urls = [f'https://rusneb.ru/search/?f_field[publisher]=f%2Fpublisher%2FНЭБ+Свет&PAGEN_1={i}' for i in
            range(1, int(page_count) + 1)]
    response = (grequests.get(url) for url in urls)
    sites = grequests.map(response)
    for site in sites:
        if site is None or site.status_code != 200:
            continue
        soup = BeautifulSoup(site.text, 'lxml')
        all_books = soup.find_all('div', class_='search-list__item')
        for book in all_books:
            book_id = book.find('a', class_='search-list__item_link', href=True)['href'].split('/')[-2]
            book_name = book.find('a', class_='search-list__item_link').find('span').text.strip()
            result.append({'book_id': book_id, 'book_name': book_name})

    return {"data": result}


@app.get("/api/v1/portal")
async def portal():
    result = []
    url = 'https://rusneb.ru/search/?access=open&PAGEN_1=2'
    response = requests.get(url)
    if response.status_code != 200:
        return {"data": []}
    soup = BeautifulSoup(response.text, 'lxml')
    page_count = soup.find('title').string.split('|')[0].split()[-1]
    list_urls = list(chunk_based_on_size([f'https://rusneb.ru/search/?access=open&PAGEN_1={i}' for i in range(1, int(page_count) + 1)], 100))
    for urls in list_urls:
        response = (grequests.get(url) for url in urls)
        sites = grequests.map(response)
        for site in sites:
            if site is None or site.status_code != 200:
                continue
            soup = BeautifulSoup(site.text, 'lxml')
            all_books = soup.find_all('div', class_='search-list__item')
            for book in all_books:
                book_id = book.find('a', class_='search-list__item_link', href=True)['href'].split('/')[-2]
                book_name = book.find('a', class_='search-list__item_link').find('span').text.strip()
                result.append({'book_id': book_id, 'book_name': book_name})

    return {"data": result}


def chunk_based_on_size(lst, n):
    for x in range(0, len(lst), n):
        yield lst[x: n+x]
