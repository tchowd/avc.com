# app.py

from flask import Flask, render_template, request, send_file
import scraper

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        base_url = 'https://avc.com'
        max_workers = 10
        csv_file = scraper.run_scraper(base_url, max_workers)
        return send_file(csv_file, mimetype='text/csv', attachment_filename='all_posts.csv', as_attachment=True)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
