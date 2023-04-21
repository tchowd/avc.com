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

def write_posts_to_epub(posts):
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier("avc_posts")
    book.set_title("AVC Posts")
    book.set_language("en")
    book.add_author("AVC")

    # Create TOC
    toc = []

    for post in posts:
        chapter = epub.EpubHtml(title=post['title'], file_name=f"{post['url'].replace('/', '_')}.xhtml", lang="en")
        chapter.content = f"<h2>{post['title']}</h2><p>Date: {post['date'].isoformat() if post['date'] else 'N/A'}</p><p>{post['content']}</p>"
        book.add_item(chapter)
        toc.append(chapter)

    book.toc = toc

    # Add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define CSS style
    style = """
    @namespace epub "http://www.idpf.org/2007/ops";
    body {
        font-family: Verdana, Arial, sans-serif;
        font-size: 14px;
    }
    h2 {
        margin-top: 1em;
        margin-bottom: 0.5em;
    }
    """
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # Set spine
    book.spine = ["nav"] + toc

    # Write the EPUB file
    epub.write_epub("output/posts.epub", book)

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
                all_posts.extend
                all_posts.extend(result)

        current_page += max_workers

# Reverse the order of posts so the newest posts come first
all_posts.sort(key=lambda post: post['date'], reverse=True)

# Write the posts to an EPUB file
write_posts_to_epub(all_posts)

print("The EPUB file has been generated.")
