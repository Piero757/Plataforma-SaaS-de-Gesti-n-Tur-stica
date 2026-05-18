import os
import urllib.request
import certifi
import ssl

context = ssl.create_default_context(cafile=certifi.where())

def download_file(url, path):
    print(f"Downloading {url} to {path}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=context) as response, open(path, 'wb') as out_file:
        out_file.write(response.read())

os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('static/webfonts', exist_ok=True)

# Bootstrap
download_file('https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css', 'static/css/bootstrap.min.css')
download_file('https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js', 'static/js/bootstrap.bundle.min.js')

# Lucide Icons
download_file('https://unpkg.com/lucide@latest', 'static/js/lucide.min.js')

# Chart.js (used in dashboard)
download_file('https://cdn.jsdelivr.net/npm/chart.js', 'static/js/chart.min.js')

# jQuery (if used)
# FullCalendar (if used)
print("Done!")
