from bs4 import BeautifulSoup
import requests
from abc import ABC
from datetime import datetime
import uuid


class SiteParser(ABC):
    def __init__(self, base_url: str, articles_path: str = ''):
        self.base_url = base_url
        self.articles_path = articles_path
        self.keywords = set()

    def parse(self):
        raise NotImplementedError

    def _normalize_url(self, url: str):
        if url.startswith('http'):
            return url
        return self.base_url + url if url.startswith('/') else self.base_url + self.articles_path + '/' + url

    def set_keywords(self, keywords: list):
        """Setting keywords to filter news"""
        self.keywords = set(word.lower() for word in keywords)

    def _matches_keywords(self, title: str, summary: str) -> bool:
        """Checking if a news item matches any of the keywords"""
        if not self.keywords:
            return True
        content = (title + " " + summary).lower()
        return any(keyword in content for keyword in self.keywords)


class HabrParser(SiteParser):
    def __init__(self):
        super().__init__('https://habr.com/', 'ru/articles')
        self.source = 'habr'

    def parse(self):
        news_items = []
        try:
            response = requests.get(f"{self.base_url}/{self.articles_path}/", headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0'
            })
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find('div', class_='tm-articles-list').find_all('article')

            for article in articles:
                try:
                    title_element = article.find('h2').find('a')
                    title = title_element.get_text(strip=True) if title_element else "No title"

                    url_element = article.find('h2').find('a')
                    url = url_element.get('href') if url_element else ""
                    if url:
                        url = self._normalize_url(url)

                    time_element = article.find('time')
                    dt = None
                    if time_element and time_element.get('datetime'):
                        dt = datetime.fromisoformat(time_element.get('datetime'))
                    else:
                        dt = datetime.utcnow()

                    summary_element = article.find('div', class_='article-formatted-body')
                    summary = summary_element.get_text(strip=True) if summary_element else ""

                    if not self._matches_keywords(title, summary):
                        continue

                    news_item = {
                        'id': str(uuid.uuid4()),
                        'title': title,
                        'url': url,
                        'summary': summary,
                        'source': self.source,
                        'published_at': dt,
                        'raw_text': str(summary_element) if summary_element else ""
                    }

                    news_items.append(news_item)

                except Exception as e:
                    print(f"Error parsing article: {e}")
                    continue

            return news_items

        except requests.RequestException as e:
            print(f"Error when requesting {self.base_url}: {e}")
            return []


if __name__ == "__main__":
    parser = HabrParser()
    parser.set_keywords(['python', 'django', 'ai', 'artificial intelligence'])
    news_items = parser.parse()
    for item in news_items[:3]:
        print(f"Title: {item['title']}")
        print(f"URL: {item['url']}")
        print(f"Published: {item['published_at']}")
        print(f"Summary: {item['summary'][:100]}...")
        print('-' * 50)
