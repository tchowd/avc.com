import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

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

def generate_toc(posts, styles):
    data = [["#", "Title", "Page"]]
    for index, post in enumerate(posts):
        data.append([index + 1, post['title'], index + 2])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    return table


def write_posts_to_pdf(posts):
    doc = SimpleDocTemplate("output/all_posts.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    content_style = styles["BodyText"].clone('content_style')
    content_style.fontSize = 12
    content_style.spaceBefore = 25

    toc = generate_toc(posts, styles)
    story.append(toc)
    story.append(PageBreak())

    for post in posts:
        title = Paragraph(f"{post['title']}", styles["Heading2"])
        url = Paragraph(f"<a href='{post['url']}'>{post['url']}</a>", styles["BodyText"])
        content = Paragraph(post['content'], content_style)
        date = Paragraph(f"Date: {post['date'].isoformat() if post['date'] else 'N/A'}", styles["BodyText"])

        story.extend([title, url, content, date, PageBreak()])

    doc.build(story)

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
write_posts_to_pdf(sorted_posts)