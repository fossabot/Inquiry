# Inquiry v1.1
# Signature: Yasin Yaşar

import os
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import threading
from lib.color import not_found, reset_color, yellow_wpcrawl

def run_wordpress_crawl(targets):
    threads = [threading.Thread(target=crawl_worker, args=(target,)) for target in targets]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    print(f"{yellow_wpcrawl} Tarama tamamlandı! {reset_color}")
    
def get_wordpress_users(site_url):
    try:
        api_url = f"{site_url}/wp-json/wp/v2/users"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            users_data = response.json()
            # Sadece name bilgilerini al
            user_names = [user.get('name') for user in users_data if user.get('name')]
            return user_names
        return []
    except Exception as e:
        print_error_message(f"{not_found} Kullanıcı bilgileri alınamadı: {e} {reset_color}")
        return []

def crawl_worker(target_name):
    try:
        site_url = format_site_url(target_name)
        response = requests.get(site_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        if not is_wordpress_site(soup):
            print(f"{not_found}Site {target_name} bir WordPress sitesi değil.{reset_color}")
            return

        # Kullanıcı bilgilerini al
        user_names = get_wordpress_users(site_url)
        
        optimized_links = optimize_plugin_links(soup, site_url)
        folder_path = prepare_folder(target_name)

        # Verileri tek bir JSON dosyasına kaydet
        wordpress_data = {
            "site_url": site_url,
            "users": user_names,
            "plugins": [],
            "status_codes": []
        }

        # Kullanıcı bilgilerini JSON'a ekle
        if user_names:
            wordpress_data["users"] = user_names

        cleaned_paths = save_cleaned_paths(optimized_links, target_name)
        status_codes_data = check_and_save_status_codes(cleaned_paths, '/readme.txt', '/changelog.md')

        for file_info in status_codes_data:
            if file_info["status_code"] == 200:
                file_type = "readme.txt" if "readme.txt" in file_info["url"] else "changelog.md"
                extract_and_save_info(file_info["url"], folder_path, wordpress_data)

        # Veriyi dosyaya kaydet
        save_results_to_file(wordpress_data, folder_path)

        sonuc(folder_path, wordpress_data)
        
    except requests.exceptions.SSLError:
        print_error_message(f"{not_found} Site Taraflı SSL Bağlantı Hatası: {target_name} {reset_color}")
    except Exception as e:
        print_error_message(f"{not_found} Crawl hatası: {e} {reset_color}")

def extract_and_save_info(file_url, folder_path, wordpress_data):
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
                
                # Plugins JSON listesine ekle
                wordpress_data['plugins'].append(plugin_info)
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

def save_results_to_file(wordpress_data, folder_path):
    results_filename = os.path.join(folder_path, "wordpress_results.json")
    try:
        with open(results_filename, 'w') as f:
            json.dump(wordpress_data, f, indent=4)
    except Exception as e:
        print_error_message(f"{not_found} JSON dosyasına yazma hatası: {e} {reset_color}")

def sonuc(folder_path, wordpress_data):
    try:
        output = []
        
        # Kullanıcı bilgilerini göster
        if wordpress_data.get('users'):
            output.append(f"{yellow_wpcrawl}\n[+] WordPress Kullanıcıları:{reset_color}")
            for user_name in wordpress_data.get('users', []):
                output.append(f"{yellow_wpcrawl} └─ {user_name}{reset_color}")
            output.append("")  # Boş satır ekle

        if wordpress_data.get('plugins'):
            output.append(f"{yellow_wpcrawl}[+] Plugins.json içeriği:{reset_color}")
            for i, plugin in enumerate(wordpress_data['plugins']):
                output.append(f"{yellow_wpcrawl} └─ Eklenti Adı: {plugin.get('plugin_name', 'Bilinmeyen')}{reset_color}")
                if i == len(wordpress_data['plugins']) - 1:
                    output.append(f"{yellow_wpcrawl}    Versiyon: {plugin.get('version', 'Bilinmeyen')}{reset_color}")
                else:
                    output.append(f"{yellow_wpcrawl} |   Versiyon: {plugin.get('version', 'Bilinmeyen')}{reset_color}")
                    output.append(f"{yellow_wpcrawl} |{reset_color}")

        if wordpress_data.get('status_codes'):
            output.append(f"{yellow_wpcrawl}\n[+] Eklenti Status Kodları:{reset_color}")
            for file_dict in wordpress_data['status_codes']:
                if file_dict['status_code'] == 200:
                    output.append(f"{yellow_wpcrawl} └─ {file_dict['url']} - Status kodu: {file_dict['status_code']}{reset_color}")

        print("\n".join(output))

    except Exception as e:
        print_error_message(f"{not_found} Sonuç işleme hatası: {e} {reset_color}")

def print_error_message(message):
    print(f"{not_found}Hata: {message}{reset_color}")
