
import urllib.request
import os

url = "https://unpkg.com/nepali-date-converter/dist/nepali-date-converter.umd.js"
dest = "d:\\CrimeData\\static\\js\\nepali_date.js"

try:
    print(f"Downloading {url} to {dest}...")
    urllib.request.urlretrieve(url, dest)
    print("Download complete.")
    print(f"File size: {os.path.getsize(dest)} bytes")
except Exception as e:
    print(f"Error: {e}")
