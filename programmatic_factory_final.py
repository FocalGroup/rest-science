import os
import json
import requests
import re
import datetime
import time
import random

# --- CONFIGURATION ---
# Your Real API Credentials
ENCODED_CREDS = "aW5mb0Bmb2NhbG1hcmtldGluZ2dyb3VwLmNvbTplMTZhNmMzNGJlNmIzNDBl"

# SWITCHED TO REGULAR ENDPOINT (More reliable for basic scraping)
API_URL = "https://api.dataforseo.com/v3/serp/google/organic/live/regular"
OLLAMA_URL = "http://localhost:11434/api/generate"

# 💰 MONEY SETTINGS
AFFILIATE_TAG = "alexsleep-20"
SITE_ROOT = os.getcwd()
ASSETS_FILE = os.path.join(SITE_ROOT, "assets/products.json")
IMAGES_DIR = os.path.join(SITE_ROOT, "static/images")

def clean_content(text):
    """Fixes common AI formatting errors."""
    text = text.replace("“", '"').replace("”", '"')
    text = re.sub(r'(?<!\{)\{< product', '{{< product', text)
    text = re.sub(r'product >\}(?!\})', 'product >}}', text)
    if "{< product" in text:
        text = text.replace("{< product", "{{< product").replace(">}", ">}}")
    return text

def download_image(image_url, sku):
    """Downloads a product image and saves it locally."""
    if not image_url or "http" not in image_url: return ""
    try:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        ext = "jpg"
        if ".png" in image_url: ext = "png"
        filename = f"{sku}.{ext}"
        save_path = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(save_path): return f"/images/{filename}"

        headers = {'User-Agent': 'Mozilla/5.0'}
        img_data = requests.get(image_url, headers=headers, timeout=10).content
        with open(save_path, 'wb') as handler:
            handler.write(img_data)
        return f"/images/{filename}"
    except Exception as e:
        return ""

def update_product_database(product_data):
    """Saves the new product to assets/products.json."""
    db = []
    if os.path.exists(ASSETS_FILE):
        with open(ASSETS_FILE, 'r') as f:
            try: db = json.load(f)
            except: db = []

    for item in db:
        if item['sku'] == product_data['sku']: return 

    db.append(product_data)
    with open(ASSETS_FILE, 'w') as f:
        json.dump(db, f, indent=2)
    print(f"   💾 Saved product '{product_data['name']}' to database.")

def find_product_data(keyword):
    """
    REAL MODE: Scrapes Google for an Amazon link with DEBUG prints.
    """
    print(f"🔎 Hunting for REAL product: '{keyword}'...")
    
    headers = {
        'Authorization': f'Basic {ENCODED_CREDS}',
        'Content-Type': 'application/json'
    }
    
    # 1. SEARCH BROADLY
    payload = [{
        "language_code": "en",
        "location_code": 2840,
        "keyword": f"best {keyword} amazon", 
        "se": "google",
        "depth": 20
    }]

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        data = response.json()

        # Debug: Check if API actually worked
        if data.get('status_code') != 20000:
             print(f"   ⚠️ API Error: {data.get('status_message')}")
             # If error is 'Insufficient funds', tell the user clearly
             if "funds" in str(data.get('status_message')).lower():
                 print("   💰 ALERT: Account balance is empty. Cannot scrape real data.")
             return None
        
        if 'tasks' in data and data['tasks'][0]['result']:
            items = data['tasks'][0]['result'][0]['items']
            print(f"   (Scanning {len(items)} search results...)")
            
            for item in items:
                url = item.get('url', '')

                if 'amazon.com' in url:
                    # 2. IMPROVED REGEX: Catch /dp/ AND /gp/product/
                    asin_match = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', url)
                    
                    if asin_match:
                        asin = asin_match.group(1)
                        print(f"   🎯 Found Amazon ASIN: {asin}")
                        
                        sku = f"{keyword.replace(' ', '-').lower()}-{asin}"
                        clean_link = f"https://www.amazon.com/dp/{asin}?tag={AFFILIATE_TAG}"
                        
                        title = item.get('title', keyword.title())
                        desc = item.get('description', 'Top rated choice on Amazon.')

                        # Use a placeholder image since we can't scrape Amazon images directly easily
                        img_url = "https://placehold.co/400x400/orange/white?text=Top+Rated+On+Amazon"
                        local_img_path = download_image(img_url, sku)

                        product_obj = {
                            "sku": sku,
                            "name": title.split(":")[0].replace("Amazon.com", "").strip()[:50],
                            "brand": "Top Pick",
                            "price": "Check Price",
                            "aff_url": clean_link,
                            "image": local_img_path,
                            "category": "gear",
                            "features": [desc[:80]+"...", "Prime Eligible", "Highly Rated"]
                        }
                        
                        update_product_database(product_obj)
                        return sku
            
            print("   ⚠️ Found Amazon links, but none with a clear ASIN (product ID).")
                    
        else:
            # LOUD DEBUGGING: Print the raw reason why tasks failed
            print("   ⚠️ API returned 0 results. Raw status:")
            if 'tasks' in data:
                print(f"   Task Status: {data['tasks'][0].get('status_message')}")
            else:
                print(f"   Full Response: {data}")
            
        return None

    except Exception as e:
        print(f"   ❌ Error finding product: {e}")
        return None

def generate_article_with_ollama(brief, product_sku):
    """Writes the article around the product SKU."""
    keyword = brief['keyword']
    
    print(f"\n🤖 Writing content for: '{keyword}'...")

    prompt = f"""
    You are an expert Sleep Coach. Write a blog post about "{keyword}".
    
    CRITICAL INSTRUCTION:
    I have already selected the best product on Amazon. Its SKU is "{product_sku}".
    You MUST insert exactly this shortcode where you recommend the product:
    
    {{< product sku="{product_sku}" >}}
    
    Structure:
    1. **Title:** H1 Title.
    2. **Intro:** Hook the reader.
    3. **The Recommendation:** Introduce the product, then INSERT THE SHORTCODE on its own line.
    4. **Buying Guide:** What else to look for.
    
    Write in Markdown. Do not include Frontmatter.
    """

    payload = {
        "model": "llama3.1",
        "prompt": prompt,
        "stream": False,
        "options": {"num_ctx": 4096}
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        return response.json().get("response", "")
    except:
        return None

def save_to_hugo(content, brief):
    """Saves the file with Hugo Frontmatter."""
    content = clean_content(content)
    date_now = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = brief['keyword'].replace(" ", "-").lower() + ".md"
    
    frontmatter = f"""---
title: "{brief['keyword'].title()}"
date: {date_now}
draft: false
description: "A complete guide to {brief['keyword']}."
---
"""
    full_content = frontmatter + content
    save_path = os.path.join(SITE_ROOT, "content/posts", filename)
    
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    print(f"✅ Saved Post: {save_path}")

def main():
    # Define Keywords
    keywords = ["weighted blanket for anxiety", "best cooling pillow side sleeper", "white noise machine for baby"]
    
    print(f"--- 🏭 Starting Factory (REAL MODE) for {len(keywords)} articles ---")
    
    for kw in keywords:
        sku = find_product_data(kw)
        
        if sku:
            brief = {"keyword": kw}
            content = generate_article_with_ollama(brief, sku)
            
            if content:
                save_to_hugo(content, brief)
                print("   (Cooling down...)")
                time.sleep(2)
        else:
            print(f"   ⚠️ Could not find product for {kw}, skipping.")

if __name__ == "__main__":
    main()