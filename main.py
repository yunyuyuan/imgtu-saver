import shutil

from requests import Session
from bs4 import BeautifulSoup
from re import match, search
from os import listdir
from config import imgtu_user, imgtu_pwd
import concurrent.futures

session = Session()


def login():
    result = session.get('https://imgtu.com/login').content.decode()
    matcher = search('auth_token\s?=\s?"([0-9a-z]{40})"', result)
    if matcher:
        session.post('https://imgtu.com/login', data={
            'login-subject': imgtu_user,
            'password': imgtu_pwd,
            'auth_token': matcher.groups()[0],
        })
        print('logined!')


need_download = []


def get_img_from_url(url):
    result = session.get(url).content.decode()

    soup = BeautifulSoup(result, 'html.parser')

    img_list = soup.select('.pad-content-listing .list-item a.image-container img')

    for img in img_list:
        img_name = img.get('alt')
        matcher = match('^((.*?)/(\d{4})/(\d\d)/(\d\d)/)[^/]*$', img.get('src'))
        groups = matcher.groups()
        need_download.append({
            'name': '.'.join(groups[2:]) + '.' + img_name,
            'url': groups[0] + img_name
        })

    # 下一页
    next_page = soup.select('.content-listing-pagination .pagination-next a[href]')
    if next_page:
        get_img_from_url(next_page[0].get('href'))


def download():
    exist_imgs = listdir('imgs')
    lis = [x for x in need_download if x['name'] not in exist_imgs]
    print(f'{len(need_download)} images found, {len(lis)} images need download.')
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for item in lis:
            futures.append(executor.submit(download_thread, item=item))
        for future in concurrent.futures.as_completed(futures):
            print(future.result())


def download_thread(item):
    r = session.get(item['url'], stream=True)
    if r.status_code == 200:
        filename = 'imgs/' + item['name']
        with open(filename, 'wb') as fp:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, fp)
        return f'{filename} downloaded!'


login()
get_img_from_url('https://imgtu.com/album/wybNR')
download()
