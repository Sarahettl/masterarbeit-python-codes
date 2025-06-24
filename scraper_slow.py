import requests
import zipfile
import time
import random
import json
import re
import csv
import pandas as pd
import undetected_chromedriver as uc

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_proxy_auth_extension(proxy_host, proxy_port, proxy_user, proxy_pass, plugin_path="proxy_auth_plugin.zip"):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Proxy Auth Extension",
        "permissions": [
            "proxy", "tabs", "unlimitedStorage", "storage",
            "<all_urls>", "webRequest", "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        }
    }
    """
    background_js = f"""
    var config = {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                scheme: "http",
                host: "{proxy_host}",
                port: parseInt({proxy_port})
            }},
            bypassList: ["localhost"]
        }}
    }};
    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function(){{}});
    chrome.webRequest.onAuthRequired.addListener(
        function(details) {{
            return {{
                authCredentials: {{
                    username: "{proxy_user}",
                    password: "{proxy_pass}"
                }}
            }};
        }},
        {{urls: ["<all_urls>"]}},
        ["blocking"]
    );
    """
    with zipfile.ZipFile(plugin_path, "w") as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return plugin_path

#DeepL API-Key
DEEPL_API_KEY = "9e105097-a8b8-47de-bef8-bb1caf824a01:fx"

#Translation via DeepL
def translate_to_english(text):
    if not text or not isinstance(text, str):
        return "N/A"
    try:
        url = "https://api-free.deepl.com/v2/translate"
        data = {
            "auth_key": DEEPL_API_KEY,
            "text": text,
            "target_lang": "EN"
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            return response.json()["translations"][0]["text"]
        else:
            return text
    except:
        return text

# map month
MONTHS_MAP = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04", "mayo": "05", "junio": "06",
    "julio": "07", "agosto": "08", "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12",
    "january": "01", "february": "02", "march": "03", "april": "04", "may": "05", "june": "06",
    "july": "07", "august": "08", "september": "09", "october": "10", "november": "11", "december": "12",
}

def normalize_visit_date(raw_date: str) -> str:
    if not raw_date or not isinstance(raw_date, str):
        return "N/A"
    raw_date = raw_date.lower().replace(".", "").strip()
    match = re.search(r"([a-záéíóú]+)\s*(de)?\s*(\d{4})", raw_date)
    if match:
        month_word = match.group(1).strip()
        year = match.group(3)
        month = MONTHS_MAP.get(month_word, "??")
        return f"{month}/{year}" if month != "??" else f"??/{year}"
    return "N/A"

def init_driver():
    proxy_ip = "p.webshare.io"
    proxy_port = "80"
    proxy_user = "ylgpuahq-rotate"
    proxy_pass = "d126kw0eqowa"
    plugin_file = create_proxy_auth_extension(proxy_ip, proxy_port, proxy_user, proxy_pass)

    options = uc.ChromeOptions()
    options.add_extension(plugin_file)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1280,800")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...")

    driver = uc.Chrome(options=options)
    driver.get("https://api.ipify.org/?format=text")
    print("🌍 Aktuelle Proxy-IP:", driver.page_source.strip())
    return driver

def is_captcha_page(driver):
    return "captcha" in driver.page_source.lower()

def extract_reviews(driver, profile_url):
    driver.get("https://api.ipify.org/?format=text")
    print("current IP:", driver.page_source)
    driver.get(profile_url)
    wait = WebDriverWait(driver, 15)
    username = profile_url.split("/")[-1]
    print(f"\n--- Reviews von: {username} ---")

    if is_captcha_page(driver):
        print("CAPTCHA - solve manually, press enter.")
        input()
        time.sleep(random.uniform(8, 10))

    time.sleep(random.uniform(4, 6))

    try:
        review_blocks = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.muQub.VrCoN")))
    except:
        print("No Reviews found")
        return []

    try:
        location_blocks = driver.find_elements(By.XPATH, "//div[contains(@class, 'SdiTl')]")
    except:
        location_blocks = []

    results = []

    for i, review in enumerate(review_blocks):
        geo_location = avg_rating = place_type = place_name = translated_text = translated_title = "N/A"

        try:
            rating = review.find_element(By.CSS_SELECTOR, "svg title").get_attribute("textContent").split(" ")[0]
        except:
            rating = "N/A"
        try:
            title = review.find_element(By.CSS_SELECTOR, "div.AzIrY").text.strip()
            translated_title = translate_to_english(title)
        except:
            title = "N/A"
        try:
            text = review.find_element(By.CSS_SELECTOR, "q.BTPVX").text.strip()
            translated_text = translate_to_english(text)
        except:
            text = "N/A"
        try:
            raw_date = review.find_element(By.CSS_SELECTOR, "div.LmTJN span").text
            visit_date = normalize_visit_date(raw_date.replace("Fecha de la visita:", "").replace("Date of visit:", "").strip())
        except:
            visit_date = "N/A"
        try:
            link = review.find_element(By.XPATH, ".//following::a[contains(@href, '/ShowUserReviews-')]")
            match = re.search(r"/ShowUserReviews-[^/]*-([^/]+)-", link.get_attribute("href"))
            if match:
                place_name = match.group(1).replace("_", " ").strip()
        except:
            place_name = "N/A"
        if i < len(location_blocks):
            try:
                location_block = location_blocks[i]
                geo_location = location_block.text.strip()
                try:
                    avg_rating = location_block.find_element(
                        By.XPATH, "./preceding-sibling::div//a | ./preceding-sibling::div//div"
                    ).text.strip()
                except:
                    avg_rating = "N/A"
                try:
                    href = location_block.find_element(By.XPATH, ".//ancestor::a[1]").get_attribute("href").lower()
                    if "restaurant_review" in href:
                        place_type = "restaurant"
                    elif "hotel_review" in href:
                        place_type = "hotel"
                    elif "attraction_review" in href:
                        place_type = "attraction"
                    elif "tour" in href:
                        place_type = "tour"
                except:
                    place_type = "unknown"
            except:
                pass

        results.append({
            "Original Title": title,
            "Translated Title": translated_title,
            "Original Text": text,
            "Translated Text": translated_text,
            "Rating": rating,
            "Reviewed Location Name": place_name,
            "Average Rating (N Reviews)": avg_rating,
            "Date of Visit": visit_date,
            "City, Country": geo_location,
            "Category": place_type,
            "User": username
        })

        time.sleep(random.uniform(4.5, 6.5))

    return results

#MAIN
if __name__ == "__main__":
    batch_number = 2
    batch_size = 10

    excel_path = "profiles_to_scrape.xlsx"
    df_profiles = pd.read_excel(excel_path, header=None)
    profile_urls = df_profiles.iloc[:, 0].dropna().tolist()
    batch_profiles = profile_urls[batch_number * batch_size : (batch_number + 1) * batch_size]

    if not batch_profiles:
        print("No URLS in the batch")
        exit()

    driver = init_driver()
    all_results = []

    for i, url in enumerate(batch_profiles):
        print(f"\nScrape Profile {i + 1}/{len(batch_profiles)}")
        try:
            driver.get("https://api.ipify.org/?format=text")
            print("current IP-address:", driver.page_source.strip())
        except:
            print("ip not found")

        all_results.extend(extract_reviews(driver, url))
        time.sleep(random.uniform(15, 30))

        if (i + 1) % 3 == 0 and (i + 1) < len(batch_profiles):
            print("3 profiles loaded - start new for new IP-address")
            driver.quit()
            time.sleep(random.uniform(10, 20))
            driver = init_driver()

    driver.quit()

    for i in range(len(all_results) - 1, 0, -1):
        all_results[i]["Reviewed Location Name"] = all_results[i - 1]["Reviewed Location Name"]
    if all_results:
        all_results[0]["Reviewed Location Name"] = "N/A"

    filename = f"tripadvisor_reviews_batch_{batch_number + 1}.csv"
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
        writer.writeheader()
        writer.writerows(all_results)

    print(f"\nBatch {batch_number + 1} saved as {filename}")
