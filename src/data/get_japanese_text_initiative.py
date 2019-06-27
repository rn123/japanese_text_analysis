# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import lxml
import json
import unicodedata

# Japanese Text Initiative
# Texts of classical Japanese literature are available at the Japanese Text 
# Initiative sponsored by the University of Virginia: http://jti.lib.virginia.edu/japanese/ 

base_url = 'http://jti.lib.virginia.edu/japanese/genji/'

@click.command()
def main():
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('pulling data from the Japanese Text Initiative')

    toc_url = 'http://jti.lib.virginia.edu/japanese/genji/tocmodern.html'
    s = requests.Session()
    r = s.get(toc_url)
    GM_toc = r.text

    # Links chapters start at 1 (instead of python 0 based counting).
    no_chapters = 54
    chapters = [n for n in range(1, no_chapters+1)]
    top_level_links = ['Mur' + str(chapter).zfill(2) + 'GM.html' for chapter in chapters]

    genji_data = {}
    for chapter in chapters:
        chapter_url = base_url + top_level_links[chapter - 1] # Account for 1-based chapter numbering.
        r = s.get(chapter_url)
        
        # HTML(r.text)
        text = r.text
        text = unicodedata.normalize('NFKC', text) # Hex encoded whitespace \x3000
        
        soup = BeautifulSoup(text, 'html.parser')
        
        headings = soup.find_all('h2')
        tags = headings[0].find_all('a')
        chapter_name = tags[0]['name'].strip()
        print('\r {}'.format(chapter_name), end=' ')
        anchors = []
        for ol in soup.find_all('ol'):
            for anchor in ol.find_all('a'):
                if 'href' in anchor.attrs:
                    anchors.append(anchor['href'].replace('#', ''))
                    link_url = chapter_url + '#' + anchor['href']
    #                 print(anchor.text, link_url)
    #         print('='*40)
        paragraphs = soup.find_all('p')
        sections = {}
        for paragraph in paragraphs[1:]:
    #         print(len(paragraph.find_all('a')))
            for anchor in paragraph.find_all('a'):
    #             print(anchor.attrs)
                if anchor['name'] in anchors:
    #                 print(anchor['name'])
                    blocks = []
                    for tag in anchor:
                        if isinstance(tag, NavigableString):
                            block = str(tag)
                            if block != '\n':
                                blocks.append(block)
    #                         print(block)
    #                         print('='*40)
                    sections[anchor['name']] = blocks
        genji_data[chapter_name] = sections
    print('\n')

    with open('data/raw/genji_data.json', 'w') as fp:
        json.dump(genji_data, fp)

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
