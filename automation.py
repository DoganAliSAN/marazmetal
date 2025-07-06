from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from seleniumbase import SB
import time
import os,requests,re
from woocommerce import API
import csv

username = "ali"
password = "MarazAliDogan14#"
login_url = "https://marazmetal.com/wp-login.php?jetpack-sso-show-default-form=1"

def upload_file(file_path):
    print(f"[DEBUG] Starting file upload for: {file_path}")
    site_url = "https://marazmetal.com"
    selenium_cookies = sb.get_cookies()
    print(f"[DEBUG] Retrieved {len(selenium_cookies)} cookies from Selenium")
    
    session = requests.Session()
    for cookie in selenium_cookies:
        session.cookies.set(cookie["name"], cookie["value"], domain=cookie.get("domain"))
        print(f"[DEBUG] Set cookie: {cookie['name']} for domain: {cookie.get('domain')}")

    # Step 3: Get _wpnonce from media-new.php
    headers = {
        "User-Agent": sb.execute_script("return navigator.userAgent;"),
        "Referer": f"{site_url}/wp-admin/media-new.php"
    }
    print(f"[DEBUG] Making request to get wpnonce from: {site_url}/wp-admin/media-new.php")
    media_page = session.get(f"{site_url}/wp-admin/media-new.php", headers=headers)
    print(f"[DEBUG] Media page request status: {media_page.status_code}")
    
    wpnonce_match = re.search(r'name="_wpnonce" value="([^"]+)"', media_page.text)
    if not wpnonce_match:
        print("[ERROR] Couldn't find _wpnonce in media page")
        raise Exception("Couldn't find _wpnonce.")
    wpnonce = wpnonce_match.group(1)
    print(f"[DEBUG] Found wpnonce: {wpnonce}")

    # Step 4: Upload file using requests
    print(f"[DEBUG] Opening file for upload: {file_path}")
    files = {
        "async-upload": (file_path, open(file_path, "rb"), "image/jpeg")
    }
    data = {
        "name": file_path,
        "post_id": "0",
        "_wpnonce": wpnonce,
        "type": "",
        "tab": "",
        "short": "1"
    }
    upload_url = f"{site_url}/wp-admin/async-upload.php"
    print(f"[DEBUG] Uploading to: {upload_url}")
    print(f"[DEBUG] Upload data: {data}")
    
    response = session.post(upload_url, headers=headers, files=files, data=data)
    print(f"[DEBUG] Upload response status: {response.status_code}")
    print(f"[DEBUG] Upload response text: {response.text[:200]}...")

    if response.status_code != 200:
        print(f"[ERROR] Upload failed with status: {response.status_code}")
        raise Exception("Upload failed")

    attachment_id = response.text.strip()
    print(f"[SUCCESS] Upload successful. Attachment ID: {attachment_id}")

    # Try REST API to get the media URL
    rest_url = f"{site_url}/wp-json/wp/v2/media/{attachment_id}"
    print(f"[DEBUG] Getting media info from REST API: {rest_url}")
    rest_response = session.get(rest_url, headers=headers)
    print(f"[DEBUG] REST API response status: {rest_response.status_code}")

    if rest_response.status_code == 200:
        json_data = rest_response.json()
        image_url = json_data.get("source_url")
        if image_url:
            print(f"[SUCCESS] Uploaded image URL: {image_url}")
            return image_url
        else:
            print("[WARNING] No source_url found in REST response")
    else:
        print(f"[ERROR] REST API failed with status: {rest_response.status_code}")
        print(f"[DEBUG] REST API response: {rest_response.text[:200]}...")

def upload_product(name,regular_price,description,image_urls):
    print(f"[DEBUG] Starting WooCommerce API product upload for: {name}")
    # WooCommerce API credentials
    url = "https://marazmetal.com"
    wcapi = API(
        url= url,
        consumer_key="ck_3f2dca3330c166b8dc830566f306fae867f8c10b",
        consumer_secret="cs_27fee5723b19d503cdc2c8d0a556216e5cf2da56",
        version="wc/v3",
        timeout=100
    )
    print("[DEBUG] WooCommerce API initialized")
    
    # Product data
    product_data = {
        "name": name,
        "type": "simple",
        "regular_price": regular_price,
        "description": description,
        "featured": True,
        "images": [{"src": x} for x in image_urls]
    }
    print(f"[DEBUG] Product data prepared: {product_data}")

    # Create product
    print("[DEBUG] Sending product creation request to WooCommerce API")
    response = wcapi.post("products", product_data)
    print(f"[DEBUG] WooCommerce API response status: {response.status_code}")

    # Print response
    if response.status_code == 201:
        print("[SUCCESS] Product created successfully via WooCommerce API!")
        print(f"[DEBUG] API Response: {response.json()}")
        return True
    else:
        print(f"[ERROR] Failed to create product via API. Status: {response.status_code}")
        print(f"[DEBUG] API Error Response: {response.json()}")
        return False

def upload_product_new():
    print("[DEBUG] Starting manual product upload via WordPress admin")
    site_url = "https://marazmetal.com"
    url = "https://marazmetal.com/wp-admin/post.php"

    selenium_cookies = sb.get_cookies()
    print(f"[DEBUG] Retrieved {len(selenium_cookies)} cookies for manual upload")
    
    session = requests.Session()
    for cookie in selenium_cookies:
        session.cookies.set(cookie["name"], cookie["value"], domain=cookie.get("domain"))
        print(f"[DEBUG] Set cookie for manual upload: {cookie['name']}")

    # Step 3: Get _wpnonce from media-new.php
    headers = {
        "User-Agent": sb.execute_script("return navigator.userAgent;"),
        "Referer": f"{site_url}/wp-admin/media-new.php"
    }

    data = {
        "_wpnonce": "625e700458",
        "_wp_http_referer": "/wp-admin/post-new.php?post_type=product",
        "user_ID": "1",
        "action": "editpost",
        "post_author": "1",
        "post_type": "product",
        "post_ID": "7267",
        "post_title": "Test ürün",
        "content": "test açıklama",
        "excerpt": "test kısa açıklama",
        "_thumbnail_id": "7260",
        "product_image_gallery": "7263,7262,7261,7260",
        "_regular_price": "500",
        "_stock": "10",
        "_manage_stock": "yes",
        "_stock_status": "instock",
        "post_status": "draft",
        "publish": "Yayınla",
        "product-type": "simple",
    }
    
    print(f"[DEBUG] Manual upload data prepared: {data}")
    print(f"[DEBUG] Sending manual upload request to: {url}")
    
    response = session.post(url, headers=headers, data=data)
    print(f"[DEBUG] Manual upload response status: {response.status_code}")
    print(f"[DEBUG] Manual upload response preview: {response.text[:500]}...")

print("[INIT] Starting main script execution")

with SB(uc=True,headless=False) as sb:
    print("[DEBUG] SeleniumBase browser initialized")
    time.sleep(1)
    
    print(f"[DEBUG] Opening login URL: {login_url}")
    sb.open(login_url)
    url_count = 0 
    
    print("[DEBUG] Checking if login page loaded correctly")
    while "marazmetal" not in sb.get_current_url():
        print(f"[DEBUG] Login page not loaded correctly. Current URL: {sb.get_current_url()}")
        print(f"[DEBUG] Retry attempt #{url_count + 1}")
        sb.open(login_url)
        url_count += 1
        if url_count > 5:
            print("[ERROR] Unable to open login page - seleniumbase issue")
            sb.quit()
            exit()

    print(f"[SUCCESS] Login page loaded. Current URL: {sb.get_current_url()}")
    
    print(f"[DEBUG] Entering username: {username}")
    sb.type("#user_login", username)
    
    print("[DEBUG] Entering password")
    sb.type("#user_pass", password)
    
    print("[DEBUG] Clicking login submit button")
    sb.click("#wp-submit")
    
    print(f"[DEBUG] After login attempt, current URL: {sb.get_current_url()}")

    # Get product info from csv file
    print("[DEBUG] Reading last processed products from last_product.txt")
    try:
        with open("last_product.txt","r") as f:
            data = f.readlines()
            data = [x.strip().replace(" ","").lower() for x in data]
        print(f"[DEBUG] Found {len(data)} previously processed products")
    except FileNotFoundError:
        print("[DEBUG] last_product.txt not found, creating new tracking file")
        data = []

    print("[DEBUG] Opening product.csv file")
    try:
        with open("product.csv", "r") as file:
            reader = csv.reader(file)
            row_count = 0

            for row in reader:
                row_count += 1
                print(f"\n[DEBUG] ===== Processing CSV row #{row_count} =====")
                
                # Skip first row
                if reader.line_num == 1:
                    print("[DEBUG] Skipping header row")
                    continue
                
                print(f"[DEBUG] Raw row data: {row[:3]}...") # Show first 3 elements
                images_first_part = [x for x in row[1:]]
                print(f"[DEBUG] Images first part count: {len(images_first_part)}")

                row = row[0].split(";")
                print(f"[DEBUG] Split row data: {row[:3]}...")
                
                name = row[2]
                print(f"[DEBUG] Product name: {name}")

                if name.strip().replace(" ","").lower() in data:
                    print(f"[SKIP] Product '{name}' is already uploaded")
                    continue
                else:
                    print(f"[NEW] Processing new product: {name}")
                    with open("last_product.txt","a+") as f:
                        f.write(name + "\n")
                    print(f"[DEBUG] Added '{name}' to tracking file")
                
                regular_price = row[11]
                description = row[7]
                short_description = row[6]
                print(f"[DEBUG] Product details - Price: {regular_price}, Description length: {len(description)}")
                
                base_url = "/Users/doganalisan/Projects/Python/marazmetal/maraz-new/"
                images_second_part = [row[13]] + images_first_part
                image_urls = [base_url + x for x in images_second_part]
                print(f"[DEBUG] Total images to upload: {len(image_urls)}")
                
                for i, img_path in enumerate(image_urls):
                    print(f"[DEBUG] Image {i+1}: {img_path}")

                print("[DEBUG] Navigating to media upload page")
                sb.open("https://marazmetal.com/wp-admin/media-new.php")
                print(f"[DEBUG] Current URL after navigation: {sb.get_current_url()}")
                
                print("[DEBUG] Starting image uploads")
                for i, img_path in enumerate(image_urls):
                    print(f"[DEBUG] Uploading image {i+1}/{len(image_urls)}: {os.path.basename(img_path)}")
                    try:
                        sb.choose_file('input[type="file"]', img_path)
                        print(f"[SUCCESS] Image {i+1} selected for upload")
                    except Exception as e:
                        print(f"[ERROR] Failed to select image {i+1}: {e}")

                wait_time = 60 * 7
                print(f"[DEBUG] Waiting {wait_time} seconds for all images to upload")
                time.sleep(wait_time)
                print("[DEBUG] Upload wait time completed")

                # Write down product information
                print("[DEBUG] Navigating to new product page")
                sb.open("https://marazmetal.com/wp-admin/post-new.php?post_type=product")
                print(f"[DEBUG] Current URL: {sb.get_current_url()}")

                print(f"[DEBUG] Entering product title: {name}")
                sb.type("#title", name)
                
                print(f"[DEBUG] Entering regular price: {regular_price}")
                sb.type("#_regular_price", regular_price)
                
                # Wait for iframe to load
                print("[DEBUG] Waiting for excerpt iframe to load")
                sb.wait_for_element("#excerpt_ifr")
                print("[DEBUG] Excerpt iframe found")

                # Switch to the iframe
                print("[DEBUG] Switching to excerpt iframe")
                sb.switch_to_frame("excerpt_ifr")

                # Type into the TinyMCE body inside the iframe
                print(f"[DEBUG] Setting short description (length: {len(short_description)})")
                sb.set_content(short_description)

                # Switch back to main content
                print("[DEBUG] Switching back to main content from excerpt iframe")
                sb.switch_to_default_content()

                print("[DEBUG] Waiting for content iframe to load")
                sb.wait_for_element("#content_ifr")
                print("[DEBUG] Content iframe found")
                
                print("[DEBUG] Switching to content iframe")
                sb.switch_to_frame("content_ifr")

                print(f"[DEBUG] Setting main description (length: {len(description)})")
                sb.set_content(description)

                # Switch back to main content
                print("[DEBUG] Switching back to main content from description iframe")
                sb.switch_to_default_content()

                print("[DEBUG] Clicking set featured image button")
                sb.click("#set-post-thumbnail")
                
                print("[DEBUG] Waiting for media library attachments to load")
                sb.wait_for_element(".attachments > li")
                photos = sb.find_elements(".attachments > li")
                print(f"[DEBUG] Found {len(photos)} photos in media library")
                
                featured_image_index = len(image_urls) - 1
                print(f"[DEBUG] Selecting featured image at index {featured_image_index}")
                photos[featured_image_index].click()
                
                # Wait for clickable
                print("[DEBUG] Waiting for media button to become clickable")
                while sb.is_element_clickable('.media-button') == False:
                    print("[DEBUG] Media button not yet clickable, waiting...")
                    time.sleep(1)
                
                print("[DEBUG] Clicking media button for featured image")
                sb.click('.media-button')
                
                print("[DEBUG] Removing media button element")
                sb.execute_script("document.querySelector('.media-button').remove();")

                # Clear attachments 
                print("[DEBUG] Clearing attachments display")
                sb.execute_script("document.querySelector('.attachments').remove();")

                print("[DEBUG] Opening product gallery selector")
                sb.click('#woocommerce-product-images > div.inside > p > a')
                
                print("[DEBUG] Waiting for gallery attachments to load")
                sb.wait_for_element(".attachments > li")

                print("[DEBUG] Setting up multi-select for gallery images")
                act = ActionChains(sb.driver)
                act.key_down(Keys.COMMAND)
                
                gallery_count = len(image_urls) - 1  # Exclude featured image
                print(f"[DEBUG] Selecting {gallery_count} images for gallery")
                
                for i in range(gallery_count):
                    print(f"[DEBUG] Selecting gallery image {i+1}/{gallery_count}")
                    act.click(sb.find_elements(".attachments > li")[i])
                
                act.key_up(Keys.COMMAND)
                act.perform()
                print("[DEBUG] Gallery image selection completed")

                print("[DEBUG] Waiting for gallery media button to become clickable")
                while sb.is_element_clickable('.media-button') == False:
                    print("[DEBUG] Gallery media button not yet clickable...")
                    time.sleep(1)
                
                print("[DEBUG] Clicking gallery media button")
                sb.click('.media-button')

                print("[DEBUG] Waiting for publish button to become clickable")
                while sb.is_element_clickable('#publish') == False:
                    print("[DEBUG] Publish button not yet clickable...")
                    time.sleep(1)
                
                print(f"[DEBUG] Publishing product: {name}")
                sb.click('#publish')
                
                print(f"[SUCCESS] ===== Product '{name}' processing completed =====\n")
                
    except FileNotFoundError:
        print("[ERROR] product.csv file not found!")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

print("[COMPLETE] Script execution finished")
