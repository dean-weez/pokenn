import requests
from pathlib import Path
import sys
import os
from bs4 import BeautifulSoup
import re
import csv

class Scraper:
    DOMAIN_URL = 'https://pokemondb.net'

    def __init__(self, fpath):
        self.fpath = Path(fpath)
        if not self.fpath.exists():
            self.fpath.mkdir()

        self.imgpath = self.fpath / 'images'
        if not self.imgpath.exists():
            self.imgpath.mkdir()


    def hello(self):
        print('Gotta catch em all!!')


    def getPokemonInfo(self, pokemon_url):
        """Get name, types, and image of pokemon"""
        # TODO: Get additional pokemon information and images
        response = requests.get(pokemon_url)
        soup = BeautifulSoup(response.text, "html.parser")

        name = soup.find('h1').string
        types = [t.string for t in soup.find_all(class_='type-icon')]
        type1 = types[0]
        if len(types) > 1:
            type2 = types[1]
        else:
            type2 = None
        img_pat = 'https://img.pokemondb.net/artwork/large/'
        img_url = img_pat + name.lower() + '.jpg'
        #img_url = soup.find('a', href=re.compile(img_pat)).get('href')
        img_data = requests.get(img_url).content
        
        return {'name': name, 'type1': type1, 'type2': type2, 'img': img_data}
        

    def getPokemonURLList(self):
        """Gets list of pokemon URLs from pokedex page"""
        pokedex_url = self.DOMAIN_URL + '/pokedex/national'
        response = requests.get(pokedex_url)
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.find_all('div', class_='infocard')
        suffixes = [c.find('a', href=re.compile('^/pokedex/')).get('href')
                    for c in cards]
        urls = [self.DOMAIN_URL + s for s in suffixes]
        return urls
    

    def getPokemonData(self):
        """Download images and metadata for all pokemon"""
        pokemon = self.getPokemonURLList()
        f = open(self.fpath / 'data.csv', 'w')
        writer = csv.writer(f, delimiter=',')
        for p in pokemon:
            data = self.getPokemonInfo(p)
            img_name = data['name'] + '.jpg'
            with open(self.imgpath / img_name, 'wb') as handler:
                handler.write(data['img'])
            writer.writerow([data['name'], data['type1'], data['type2']])
        f.close()
    

if __name__ == "__main__":
    if len(sys.argv) == 2:
        fpath = sys.argv[1]
    else:
        fpath = os.getcwd()
    scraper = Scraper(fpath)
    scraper.hello()
    scraper.getPokemonData()
