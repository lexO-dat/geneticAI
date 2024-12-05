import requests
from bs4 import BeautifulSoup
import csv
import time
import os

offset = 0
limit = 109939 # Hasta el momento que hice el scrappeo habian 109939 archivos en el repo

data = []

def get_sbol(url):
    try:
        sbol = requests.get(url)
        sbol.raise_for_status()
        return sbol.text
    except requests.exceptions.RequestException as e:
        print(f'Error fetching SBOL from {url}: {e}')
        return ''

def add_sbol_links(data):
    for item in data:
        sbol = item['url'] + '/sbol'
        item['sbol_link'] = sbol
    return data

def download_sbol_files(data):
    for item in data:
        sbol_content = get_sbol(item['sbol_link'])
        item['sbol'] = sbol_content
        print('Downloaded SBOL for:', item['title'])
    return data

def obtain_first_info():
    with open('resultados.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'url', 'description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        global offset  # offset de 50 en 50 (synbiohub tiene paginaciones cada 50 )
        while offset < limit:
            if offset == 0:
                url = 'https://synbiohub.org/search?q='
            else:
                url = f'https://synbiohub.org/search/*/?offset={offset}'

            retries = 0
            success = False

            while not success and retries < 5:
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    success = True
                except requests.exceptions.RequestException as e:
                    retries += 1
                    print(f'Error making request: {e}')
                    print(f'Waiting 5 seconds before retrying... (Attempt {retries}/{5})')
                    time.sleep(5)

            if not success:
                print(f'Could not retrieve page after 5 attempts. Continuing to the next page.')
                offset += 50
                continue

            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')

            result_items = soup.find_all('div', class_='search-result-item')

            if not result_items:
                print('No items found with class "search-result-item".')
            else:
                for item in result_items:
                    title_tag = item.find('a')
                    title = title_tag.text.strip() if title_tag else 'No Title'

                    href = title_tag['href'] if title_tag else ''
                    link = 'https://synbiohub.org' + href

                    description_tag = item.find('strong')
                    description = ''

                    if description_tag:
                        sibling = description_tag.next_sibling
                        if sibling and isinstance(sibling, str):
                            description = sibling.strip()
                        else:
                            description = description_tag.get_text(strip=True)
                    else:
                        description = 'No Description'

                    print('Title:', title)
                    print('Link:', link)
                    print('Description:', description)
                    print('---')

                    writer.writerow({
                        'title': title,
                        'url': link,
                        'description': description
                    })

                    data.append({
                        'title': title,
                        'url': link,
                        'description': description
                    })

            offset += 50
            # time.sleep(1) 

    #print('Extraction completed. Data saved in "resultados.csv".')

def obtain_specific_info():
    input_file = 'resultados.csv'
    output_file = 'info.csv'

    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = list(reader)

    data = add_sbol_links(data)
    data = download_sbol_files(data)

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'url', 'description', 'sbol_link', 'sbol']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    #print(f'Updated file saved as "{output_file}".')

def main():
    obtain_first_info()
    obtain_specific_info()
