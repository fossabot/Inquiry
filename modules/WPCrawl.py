# Inquiry v1.0 WPCrawl v1.1
# Signature: Yasin Yaşar

import os
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import threading
from modules.color import found, not_found, reset_color, yellow_wpcrawl


def run_wordpress_crawl(targets):
    stop_event = threading.Event()
    animation_thread = threading.Thread(args=(stop_event,))
    animation_thread.start()
    
    threads = [threading.Thread(target=crawl_worker, args=(target,)) for target in targets]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    stop_event.set()  # Animasyonu durdur
    animation_thread.join()
    print(f"{yellow_wpcrawl} Tarama tamamlandı! {reset_color}")

def crawl_worker(target_name):
    try:
        site_url = format_site_url(target_name)
        response = requests.get(site_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        if not is_wordpress_site(soup):
            print(f"{not_found}Site {target_name} bir WordPress sitesi değil.{reset_color}")
            return

        optimized_links = optimize_plugin_links(soup, site_url)
        folder_path = prepare_folder(target_name)

        cleaned_paths = save_cleaned_paths(optimized_links, target_name)

        status_codes_data = check_and_save_status_codes(cleaned_paths, '/readme.txt', '/changelog.md')

        for file_info in status_codes_data:
            if file_info["status_code"] == 200:
                file_type = "readme.txt" if "readme.txt" in file_info["url"] else "changelog.md"
                extract_and_save_info(file_info["url"], folder_path)

        sonuc(folder_path, status_codes_data)
    except Exception as e:
        print_error_message(f"{not_found} Crawl hatası: {e} {reset_color}")

def extract_and_save_info(file_url, folder_path):
    try:
        response = requests.get(file_url)
        if response.status_code == 200:
            plugin_name = re.search(r'===(.+?)===', response.text, re.DOTALL)
            stable_tag = re.search(r'Stable\s*tag:\s*(.+)', response.text, re.IGNORECASE)
            
            if plugin_name and stable_tag:
                plugin_info = {
                    'plugin_name': plugin_name.group(1).strip(), 
                    'version': stable_tag.group(1).strip()
                }
                
                json_filename = os.path.join(folder_path, "plugins.json")
                existing_data = json.load(open(json_filename, 'r')) if os.path.exists(json_filename) else []
                
                existing_entry = next((entry for entry in existing_data if entry['plugin_name'] == plugin_info['plugin_name']), None)
                
                if not existing_entry or existing_entry['version'] != plugin_info['version']:
                    if existing_entry:
                        existing_data.remove(existing_entry)
                    existing_data.append(plugin_info)
                    
                    with open(json_filename, 'w') as json_file:
                        json.dump(existing_data, json_file, indent=4)
    except Exception as e:
        print_error_message(f"{not_found} Bilgi çıkarma hatası: {e} {reset_color}")

def format_site_url(target_name):
    return target_name if target_name.startswith("https://") else "https://" + target_name

def is_wordpress_site(soup):
    return any('/wp-content/plugins/' in link_tag.get('href', '') for link_tag in soup.find_all('link', rel='stylesheet', href=True))

def optimize_plugin_links(soup, site_url):
    return [
        href if href.startswith("http") else urljoin(site_url, href)
        for link_tag in soup.find_all('link', rel='stylesheet', href=True)
        for href in [link_tag.get('href')]
        if href and '/wp-content/plugins/' in href
    ]

def prepare_folder(target_name):
    folder_path = os.path.join("data/domain", target_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def save_cleaned_paths(optimized_links, target_name):
    cleaned_paths = {
        f"{target_name}/wp-content/plugins/{match.group(1)}"
        for url in optimized_links
        for match in [re.search(r'/wp-content/plugins/([^/]+)', url)]
        if match
    }
    return list(cleaned_paths)

def check_and_save_status_codes(cleaned_paths, *file_extensions):
    try:
        status_codes_data = []

        for url in cleaned_paths:
            for file_extension in file_extensions:
                new_url = 'http://' + url + file_extension
                response = requests.get(new_url)

                url_status_dict = {'url': new_url, 'status_code': response.status_code}
                status_codes_data.append(url_status_dict)

        return status_codes_data
    except Exception as e:
        print_error_message(f"{not_found} Status kodu hatası: {e} {reset_color}")

def sonuc(folder_path, status_codes_data):
    try:
        plugins_json_filename = os.path.join(folder_path, "plugins.json")
        
        if os.path.exists(plugins_json_filename):
            with open(plugins_json_filename, 'r') as plugins_file:
                plugins_data = json.load(plugins_file)
                
                print(f"{yellow_wpcrawl}Plugins.json içeriği:{reset_color}")
                for plugin in plugins_data:
                    print(f"{yellow_wpcrawl}Eklenti Adı: {plugin.get('plugin_name', 'Bilinmeyen')}\n"
                          f"Versiyon: {plugin.get('version', 'Bilinmeyen')}\n{reset_color}")
        else:
            print(f"{not_found}plugins.json dosyası bulunamadı.{reset_color}")

        for file_dict in status_codes_data:
            if file_dict['status_code'] == 200:
                print(f"{found}{file_dict['url']} - Status kodu: {file_dict['status_code']}{reset_color}")

    except Exception as e:
        print_error_message(f"{not_found} Sonuç işleme hatası: {e} {reset_color}")

def print_error_message(message):
    print(f"{not_found}Hata: {message}{reset_color}")
