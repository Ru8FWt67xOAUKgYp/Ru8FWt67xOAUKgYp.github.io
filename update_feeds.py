 
import urllib.request
import json
import xml.etree.ElementTree as ET
from datetime import datetime

# --- ADD YOUR MIXED FEEDS HERE ---
FEED_URLS = [
    "https://news.google.com/rss?hl=en-CA&gl=CA&ceid=CA:en", # RSS
    "https://www.theverge.com/rss/index.xml",             # RSS
    "https://hackaday.com/blog/feed/",                    # RSS
    "https://github.com/blog.atom"                        # ATOM (Example)
]

def fetch_feed(url):
    items = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
        
        root = ET.fromstring(xml_data)
        
        # Determine if RSS or Atom
        # RSS uses <item>, Atom uses {http://www.w3.org/2005/Atom}entry
        is_atom = 'http://www.w3.org/2005/Atom' in root.tag
        namespace = {'ns': 'http://www.w3.org/2005/Atom'} if is_atom else {}

        source_title = "Unknown"
        if is_atom:
            source_title = root.find('ns:title', namespace).text
            entries = root.findall('ns:entry', namespace)
        else:
            source_title = root.find('.//channel/title').text
            entries = root.findall('.//item')

        for entry in entries[:5]:
            if is_atom:
                title = entry.find('ns:title', namespace).text
                # Atom links are usually in an attribute: <link href="...">
                link = entry.find('ns:link', namespace).attrib.get('href')
                date = entry.find('ns:updated', namespace).text[:10]
            else:
                title = entry.find('title').text
                link = entry.find('link').text
                date = entry.find('pubDate').text[:16] if entry.find('pubDate') is not None else ""

            items.append({
                "title": title,
                "link": link,
                "source": source_title,
                "date": date
            })
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return items

def main():
    all_feeds = []
    for url in FEED_URLS:
        all_feeds.extend(fetch_feed(url))
    
    # Sort all news by date (optional, but keeps things organized)
    all_feeds.sort(key=lambda x: x['date'], reverse=True)

    output = {
        "updated": datetime.now().strftime("%H:%M"),
        "feeds": all_feeds
    }
    
    with open('feeds.json', 'w') as f:
        json.dump(output, f)

if __name__ == "__main__":
    main()