from flask import Flask, render_template, send_file, redirect, url_for
from scraper import scrape_profiles
from database import export_csv, get_last_run, get_total_records
import os

app = Flask(__name__)

@app.route('/')
def dashboard():
    last_run = get_last_run()
    total = get_total_records()
    return render_template('dashboard.html', last_run=last_run, total=total)

@app.route('/scrape')
def scrape():
    scrape_profiles()
    return redirect(url_for('dashboard'))

@app.route('/download')
def download():
    filename = export_csv()
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
