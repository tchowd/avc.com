import os
from invoke import task

def remove_existing_output_files():
    output_files = ["posts.txt", "posts.pdf", "posts.epub", "posts.mobi"]
    for file in output_files:
        if os.path.exists(file):
            os.remove(file)

@task
def fetch_posts(c):
    remove_existing_output_files()
    c.run('/usr/local/bin/python3 txt.py')

@task
def create_pdf(c):
    remove_existing_output_files()
    c.run('/usr/local/bin/python3 pdf.py')

@task
def create_epub(c):
    remove_existing_output_files()
    c.run('/usr/local/bin/python3 epub.py')

@task
def create_mobi(c):
    remove_existing_output_files()
    c.run('/usr/local/bin/python3 posts.mobi')

@task
def clean(c):
    remove_existing_output_files()

@task(pre=[fetch_posts, create_pdf, create_epub, create_mobi])
def all(c):
    pass
