import requests
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

def write_posts_to_epub(posts):
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier('sample-blog-posts')
    book.set_title('Sample Blog Posts')
    book.set_language('en')
    book.add_author('Your Name')

    # Define styles
    style = '''
    @namespace epub "http://www.idpf.org/2007/ops";
    body {
        font-family: Georgia, Times, serif;
    }
    h2 {
        text-align: left;
        text-transform: uppercase;
        font-weight: 200;
    }
    '''

    # Add style to the book
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # Add content to the book
    spine = ['nav']
    for post in posts:
        title = post['title']
        url = post['url']
        content = post['content']
        date = post['date'].isoformat() if post['date'] else 'N/A'

        c1 = epub.EpubHtml(title=title, file_name=f'post_{len(spine)}.xhtml', lang='en')
        c1.content = f'<h2>{title}</h2><p><a href="{url}">{url}</a></p><p>{content}</p><p>Date: {date}</p>'
        c1.add_item(nav_css)
        book.add_item(c1)
        spine.append(c1)

    # Define Table of Contents
    book.toc = [(epub.Link(f'post_{i}.xhtml', post['title'], f'post_{i}') for i, post in enumerate(posts, 1))]

    # Add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Set spine
    book.spine = spine

    # Create EPUB file
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