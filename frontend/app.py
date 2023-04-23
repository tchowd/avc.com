# app.py

from flask import Flask, render_template, request, send_file, Response
import scraper 
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        base_url = 'https://avc.com'
        max_workers = 10
        csv_file_path = scraper.run_scraper(base_url, max_workers)
        with open(csv_file_path, "r") as f:
            csv_data = f.read()

        response = Response(csv_data, content_type='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=all_posts.csv'
        return response

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
