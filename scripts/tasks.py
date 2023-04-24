import os
from invoke import task

def remove_existing_output_files():
    output_files = ["all_posts.csv", "all_posts.epub", "all_posts.pdf", "all_posts.mobi"]
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
    c.run('/usr/local/bin/python3 mobi.py')

@task
def clean(c):
    remove_existing_output_files()

@task(pre=[clean, fetch_posts, create_pdf, create_epub, create_mobi])
def all(c):
    pass
