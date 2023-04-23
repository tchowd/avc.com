from flask import Flask, render_template
from invoke import Collection, Context, Program
from tasks import fetch_posts, create_pdf, create_epub, create_mobi, clean, all

app = Flask(__name__)

# Create a new Collection object
ns = Collection()

# Add the task functions to the collection
ns.add_task(fetch_posts)
ns.add_task(create_pdf)
ns.add_task(create_epub)
ns.add_task(create_mobi)
ns.add_task(clean)
ns.add_task(all)

@app.route('/')
def index():
    return render_template('index.html')

# Define a route for each task
@app.route('/fetch_posts')
def fetch_posts_route():
    # Create a new Context object and run the task function
    c = Context(config={}, collection=ns)
    fetch_posts(c)
    return 'Posts fetched successfully'

@app.route('/create_pdf')
def create_pdf_route():
    # Create a new Context object and run the task function
    c = Context(config={}, collection=ns)
    create_pdf(c)
    return 'PDF created successfully'

@app.route('/create_epub')
def create_epub_route():
    # Create a new Context object and run the task function
    c = Context(config={}, collection=ns)
    create_epub(c)
    return 'EPUB created successfully'

@app.route('/create_mobi')
def create_mobi_route():
    # Create a new Context object and run the task function
    c = Context(config={}, collection=ns)
    create_mobi(c)
    return 'MOBI created successfully'

@app.route('/clean')
def clean_route():
    # Create a new Context object and run the task function
    c = Context(config={}, collection=ns)
    clean(c)
    return 'Cleaned successfully'

@app.route('/all')
def all_route():
    # Create a new Context object and run the task function
    c = Context(config={}, collection=ns)
    all(c)
    return 'All tasks executed successfully'

if __name__ == '__main__':
    app.run()
