import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import re
import os
from ebooklib import epub
from datetime import datetime

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

def write_posts_to_epub(posts):
    book = epub.EpubBook()

    # Basic metadata
    book.set_identifier('avc-posts')
    book.set_title('AVC Posts')
    book.set_language('en')
    book.add_author('AVC')

    # Create a table of contents
    book.toc = [epub.Link(f"post-{index}.xhtml", post['title'], f"post-{index}") for index, post in enumerate(posts)]

    # Add content
    for index, post in enumerate(posts):
        content = f"""
        <h2>{post['title']}</h2>
        <p>URL: <a href="{post['url']}">{post['url']}</a></p>
        <p>Date: {post['date'].isoformat() if post['date'] else 'N/A'}</p>
        <p>Content:</p>
        <p>{post['content']}</p>
        """

        chapter = epub.EpubHtml(title=post['title'], file_name=f"post-{index}.xhtml", lang='en')
        chapter.content = content
        book.add_item(chapter)

    # Add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Save the EPUB file
    epub.write_epub('output/posts.epub', book)

def convert_epub_to_mobi():
    subprocess.run(['kindlegen', 'posts.epub'])

base_url = 'https://avc.com'
current_page = 1
max_workers = 10
end_page = 100

# Fetch and save all the posts
all_posts = []
current_page = 1
last_page = 100

with ThreadPoolExecutor(max_workers=10) as executor:
    while current_page <= last_page:
        print(f"Fetching page {current_page}")

        futures = [executor.submit(get_posts, f'https://avc.com/page/{page}/') for page in range(current_page, current_page + 10)]

        current_page += 10

        for future in futures:
            result = future.result()
            if result:
                all_posts.extend(result)
            else:
                break

        if not result:
            break

# Save posts to an EPUB file
write_posts_to_epub(all_posts)

print("All posts have been saved as an EPUB file.")
