import shutil

from requests import get
from bs4 import BeautifulSoup
from re import match
from os import listdir

exist_imgs = listdir('imgs')


def get_img_from_url(url):
    result = get(url).content.decode()

    soup = BeautifulSoup(result, 'html.parser')

    img_list = soup.select('.pad-content-listing .list-item a.image-container img')

    img_urls = []

    for img in img_list:
        img_name = img.get('alt')
        matcher = match('^((.*?)/(\d{4})/(\d\d)/(\d\d)/)[^/]*$', img.get('src'))
        groups = matcher.groups()
        img_urls.append({
            'name': '.'.join(groups[2:]) + '.' + img_name,
            'url': groups[0] + img_name
        })

    for img in [x for x in img_urls if x['name'] not in exist_imgs]:
        r = get(img['url'], stream=True)
        if r.status_code == 200:
            with open('imgs/' + img['name'], 'wb') as fp:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, fp)

    next_page = soup.select('.content-listing-pagination .pagination-next a')
    if next_page:
        get_img_from_url(next_page[0].get('href'))


get_img_from_url('https://imgtu.com/album/wybNR')
