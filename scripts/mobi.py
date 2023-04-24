import requests
import os
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from ebooklib import epub

session = requests.Session()

def get_posts(url):
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    posts = soup.select('article.Post')

    if not posts:
        return None

    post_data = []

    for post in posts:
        date = post.select_one('time')['datetime']
        title = post.select_one('h2 a')
        content_area = post.select_one('.ContentArea')
        content = content_area.get_text(separator=" ", strip=True) if content_area else 'N/A'

        post_data.append({
            'title': title.text.strip(),
            'url': title['href'],
            'content': content,
            'date': datetime.fromisoformat(date.strip()) if date else None
        })

    return post_data

def process_page(current_page):
    url = f'{base_url}/page/{current_page}'
    print(f'Fetching posts from: {url}\n')
    posts = get_posts(url)
    return posts

def write_posts_to_mobi(posts):
    book = epub.EpubBook()

    book.set_identifier('avc-blog-collection')
    book.set_title('AVC Blog Collection')
    book.set_language('en')
    book.add_author('AVC Blog Author')

    toc = []  # Table of contents
    spine = ['nav']
    for index, post in enumerate(posts):
        title = post['title']
        content = f"<h2>{title}</h2>"
        content += f"<a href='{post['url']}'>{post['url']}</a><br><br>"
        content += post['content']
        content += f"<p>Date: {post['date'].isoformat() if post['date'] else 'N/A'}</p>"

        chapter = epub.EpubHtml(title=f"Chapter {index + 1}: {title}", file_name=f'chapter_{index + 1}.xhtml', lang='en')
        chapter.set_content(content)
        book.add_item(chapter)

        toc.append(chapter)  
        spine.append(chapter)

    book.toc = toc  
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    book.spine = spine

    epub.write_epub("output/all_posts.epub", book)

    os.system("ebook-convert output/all_posts.epub output/all_posts.mobi")

base_url = 'https://avc.com'
current_page = 1
max_workers = 10
end_page = 100

all_posts = []

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    while True:
        futures = [executor.submit(process_page, current_page + i) for i in range(max_workers)]
        results = [future.result() for future in futures]

        if all(result is None for result in results):
            break

        for result in results:
            if result is not None:
                all_posts.extend(result)

        current_page += max_workers

sorted_posts = sorted(all_posts, key=lambda post: post['date'], reverse=True)
write_posts_to_mobi(sorted_posts)