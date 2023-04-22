import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import ebooklib
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

def create_epub_chapter(post):
    title = post['title']
    url = post['url']
    content = post['content']
    date = post['date'].isoformat() if post['date'] else 'N/A'

    html_content = f'''
    <h2>{title}</h2>
    <p><a href="{url}">{url}</a></p>
    <p>{content}</p>
    <p>Date: {date}</p>
    '''
    chapter = epub.EpubHtml(title=title, file_name=f"{title.replace(' ', '_')}.xhtml", content=html_content)
    return chapter

def write_posts_to_epub(posts):
    book = epub.EpubBook()

    # Set book metadata
    book.set_identifier('sample123456')
    book.set_title('Sample Blog Posts')
    book.set_language('en')
    book.add_author('Blog Author')

    # Create a table of contents
    toc = epub.EpubHtml(title='Table of Contents', file_name='toc.xhtml')
    toc.set_content('<h1>Table of Contents</h1>')
    book.add_item(toc)

    # Create chapters
    chapters = [create_epub_chapter(post) for post in posts]
    for chapter in chapters:
        book.add_item(chapter)

    # Create a spine
    book.spine = ['nav', toc] + chapters

    # Create a table of contents in the book
    book.toc = [('Table of Contents', toc)] + [(chapter.title, chapter) for chapter in chapters]

    # Write the EPUB file
    epub.write_epub('output/final_output.epub', book)

base_url = 'https://avc.com'
current_page = 1
max_workers = 10
end_page = 100

all_posts = []

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    while current_page <= end_page:
        futures = [executor.submit(process_page, current_page + i) for i in range(max_workers)]
        results = [future.result() for future in futures]

        if all(result is None for result in results):
            break

        for result in results:
            if result is not None:
                all_posts.extend(result)

        current_page += max_workers

sorted_posts = sorted(all_posts, key=lambda post: post['date'], reverse=True)
write_posts_to_epub(sorted_posts)