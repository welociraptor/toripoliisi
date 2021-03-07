from bs4 import BeautifulSoup
from google.cloud import storage
import json
import os
import re
import requests
from telebot import TeleBot


def scrape_current_items(keyword: str, category: str):
    """Scrape a list of current classified ads off muusikoiden.net tori, with a keyword search from ad titles.

    :param keyword: Keyword to search for.
    :return: List of dictionary objects containing the ads.
    """
    page = requests.get(
        f'https://muusikoiden.net/tori/haku.php?keyword={keyword}&title_only=1&category={category}&type=sell&sort=new')
    soup = BeautifulSoup(page.content, 'html.parser')

    items = []
    for separator in soup.find_all('hr', {'class': 'hort_sep'}):  # Locate the items by horizontal separators.
        if separator.next_sibling.name != 'a':  # Classified ads have a HTML anchor directly below the separator.
            continue
        tds = separator.next_sibling.next_sibling.find_all('td')
        item = {
            'title': tds[0].text[9:],
            'url': "https://muusikoiden.net/tori/ilmoitus/" + separator.next_sibling['name'],
            'created': tds[2].span['title'][9:25],
            'updated': tds[2].span['title'][36:] if len(tds[2].span['title']) > 25 else None,
            'description': tds[7].font.text,
            'price': int(re.search('(\d+).*', tds[7].p.text[7:]).group(1))
        }
        items.append(item)
    return items


def download_from_cloud_storage(filename: str):
    """Download a JSON file from Cloud storage."""
    client = storage.Client()
    bucket = client.get_bucket(os.environ['BUCKET'])
    blob = bucket.blob(filename)
    return json.loads(blob.download_as_text())


def upload_to_cloud_storage(filename: str, jsondata: str):
    """Upload a JSON file to Cloud storage."""
    client = storage.Client()
    bucket = client.get_bucket(os.environ['BUCKET'])
    blob = bucket.blob(filename)
    blob.upload_from_string(jsondata)


def send_telegram_notify(item: dict):
    """Send a Telegram notification about a new item."""
    bot = TeleBot(os.environ['TG_BOT_TOKEN'], parse_mode='HTML')
    bot.send_message(int(os.environ['USER_ID']),
                     (f'Uusi ilmoitus torilla!\n\n'
                      f'<b>{item["title"]}</b>\n'
                      f'{item["description"]}\n'
                      f'Hinta: {item["price"]} €'))


def toripoliisi(_event, _context):
    """Business logic:

    - Load a list of previously scraped items from Cloud Storage
    - Scrape current items from muusikoiden.net
    - Filter previously scraped items from the list of current items
    - Send notifications for new items via Telegram
    - Upload a current list of items to Cloud Storage
    """

    saved_items = download_from_cloud_storage('toripoliisi.json')

    current_items = scrape_current_items(os.environ['KEYWORD'], os.environ['CATEGORY'])

    # Filter those scraped items that have already been saved.
    items = list(filter(lambda ci: not any(si['url'] == ci['url'] for si in saved_items), current_items))

    if not items:  # No new items found.
        print('No new items found.')
        return

    print(f'{len(items)} new items found.')

    for item in items:
        send_telegram_notify(item)

    jsondata = json.dumps(current_items, sort_keys=True)
    upload_to_cloud_storage('toripoliisi.json', jsondata)


if __name__ == '__main__':
    toripoliisi('', '')
