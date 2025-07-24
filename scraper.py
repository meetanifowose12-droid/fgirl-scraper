import requests
import random
import time
import os
from bs4 import BeautifulSoup
from database import save_profile, profile_exists, update_last_run

BASE_URL = "https://www.fgirl.ch/filles/"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"
]

PROXY = os.environ.get("SCRAPER_PROXY")
PROXIES = {"http": PROXY, "https": PROXY} if PROXY else None

def safe_request(url, retries=3):
    for attempt in range(retries):
        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            resp = requests.get(url, headers=headers, proxies=PROXIES, timeout=15)
            if resp.status_code == 200:
                return resp.text
            time.sleep(2)
        except Exception:
            time.sleep(2)
    return None

def get_soup(url):
    html = safe_request(url)
    if not html:
        return None
    return BeautifulSoup(html, "html.parser")

def scrape_profiles():
    soup = get_soup(BASE_URL)
    if not soup:
        print("Failed to fetch main page. Check proxy or site status.")
        return 0

    links = [a["href"] for a in soup.select("a[href*='/filles/']") if a.get("href")]
    new_count = 0

    for link in links:
        try:
            if profile_exists(link):
                continue
            data = scrape_profile_details(link)
            if data:
                save_profile(data)
                new_count += 1
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            print(f"Error scraping {link}: {e}")

    update_last_run()
    return new_count

def scrape_profile_details(url):
    soup = get_soup(url)
    if not soup:
        return None
    name_tag = soup.find("h1")
    phone_tag = soup.select_one("a[href^='tel:']")
    about_section = soup.select_one(".about")
    return {
        "url": url,
        "name": name_tag.text.strip() if name_tag else "Unknown",
        "phone": phone_tag.text.strip() if phone_tag else "",
        "about": about_section.text.strip() if about_section else ""
  }
