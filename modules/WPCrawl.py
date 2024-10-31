# Inquiry v1.0 WPCrawl
# Signature: Yasin Yaşar

import os
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import threading
from modules.color import found, not_found, reset_color, yellow_wpcrawl, cobalt_blue
from colorama import init

def run_wordpress_crawl(targets):
    threads = []
    for target_name in targets:
        t = threading.Thread(target=crawl_worker, args=(target_name,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


def crawl_worker(target_name):
    try:
        site_url = format_site_url(target_name)

        response = requests.get(site_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        if not is_wordpress_site(soup):
            print({not_found} + f"Site {target_name} bir WordPress sitesi değil." + {reset_color})
            return

        optimized_links = optimize_plugin_links(soup, site_url)
        folder_path, existing_json_path = prepare_folders_and_paths(target_name)
        update_existing_data(existing_json_path, optimized_links)
        cleaned_json_filename = save_cleaned_paths(folder_path, optimized_links, target_name)
        status_codes_data = check_and_save_status_codes(cleaned_json_filename, '/readme.txt', '/changelog.md')

        for file_info in status_codes_data:
            file_url = file_info["url"]
            status_code = file_info["status_code"]
            if status_code == 200:
                file_type = "readme.txt" if "readme.txt" in file_url else "changelog.md"
                extract_and_save_info(file_url, file_type, folder_path)  # target_name kaldırıldı

        sonuc(cleaned_json_filename, status_codes_data)
    except Exception as e:
        print_error_message(f"(2) Hata meydana geldi: {e}")


def extract_and_save_info(file_url, file_type, folder_path):
    try:
        response = requests.get(file_url)
        status_code = response.status_code
        if status_code == 200:
            file_content = response.text

            # Eklenti Adı ve Stable Tag'ı çıkart
            plugin_name_pattern = re.compile(r'===(.+?)===', re.DOTALL)
            plugin_name_match = plugin_name_pattern.search(file_content)
            plugin_name = plugin_name_match.group(1).strip() if plugin_name_match else None

            stable_tag_pattern = re.compile(r'Stable\s*tag:\s*(.+)', re.IGNORECASE)
            stable_tag_match = stable_tag_pattern.search(file_content)
            stable_tag = stable_tag_match.group(1).strip() if stable_tag_match else None

            if plugin_name and stable_tag:
                plugin_info = {'plugin_name': plugin_name, 'version': stable_tag}
                json_filename = os.path.join(folder_path, "plugins.json")
                existing_data = []
                if os.path.exists(json_filename):
                    with open(json_filename, 'r') as json_file:
                        existing_data = json.load(json_file)

                existing_entry = next((entry for entry in existing_data if entry['plugin_name'] == plugin_name), None)
                if existing_entry:
                    if existing_entry['version'] != stable_tag:
                        existing_data.remove(existing_entry)
                        existing_data.append(plugin_info)
                        with open(json_filename, 'w') as json_file:
                            json.dump(existing_data, json_file, indent=4)
                        print(f"{found} {file_type.capitalize()} veri güncellendi {json_filename}.{reset_color}")
                    else:
                        print(f"{yellow_wpcrawl} {file_type.capitalize()} veri zaten mevcut {json_filename}.{reset_color}")
                else:
                    existing_data.append(plugin_info)
                    with open(json_filename, 'w') as json_file:
                        json.dump(existing_data, json_file, indent=4)
                    print(f"{yellow_wpcrawl} {file_type.capitalize()} şuradan alınan bilgi {file_url} şuraya kayıt edildi {json_filename}.{reset_color}")
            else:
                print(f"{not_found} Eklenti Adı veya Stable Tag bilgisi bulunamadı {file_url}.{reset_color}")
        else:
            print(f"{not_found} Görüntülenemedi {file_url}. Status kodu: {status_code}.{reset_color}")
    except Exception as e:
        print_error_message(f"(1) Hata meydana geldi: {e}")

def format_site_url(target_name):
    if not target_name.startswith("https://"):
        return "https://" + target_name
    return target_name

def is_wordpress_site(soup):
    wp_plugin_link_found = any(link_tag.get('href') and '/wp-content/plugins/' in link_tag.get('href') for link_tag in soup.find_all('link', rel='stylesheet', href=True))
    return wp_plugin_link_found

def optimize_plugin_links(soup, site_url):
    optimized_links = []
    for link_tag in soup.find_all('link', rel='stylesheet', href=True):
        href = link_tag.get('href')
        if href and '/wp-content/plugins/' in href:
            optimized_url = href if href.startswith("http") else urljoin(site_url, href)
            optimized_links.append(optimized_url)
            link_tag['href'] = optimized_url
    return optimized_links

def prepare_folders_and_paths(target_name):
    output_folder = "data/domain"
    folder_path = os.path.join(output_folder, target_name)
    existing_json_path = os.path.join(folder_path, "optimized_links.json")
    os.makedirs(folder_path, exist_ok=True)
    return folder_path, existing_json_path

def update_existing_data(existing_json_path, optimized_links):
    if os.path.exists(existing_json_path):
        with open(existing_json_path, 'r') as existing_json_file:
            existing_data = json.load(existing_json_file)
        new_links = [link for link in optimized_links if link not in existing_data]
        if new_links:
            updated_data = existing_data + new_links
            with open(existing_json_path, 'w') as json_file:
                json.dump(updated_data, json_file, indent=4)
            print(f"{found} Yeni veri başarıyla kayıt edildi.{reset_color}")
        else:
            print(f"{cobalt_blue} Yeni veri bulunmadı, güncelleme yapılmadı.{reset_color}")
    else:
        with open(existing_json_path, 'w') as json_file:
            json.dump(optimized_links, json_file, indent=4)
        print(f"{found} Veri başarıyla kayıt edildi.{reset_color}")

def save_cleaned_paths(folder_path, optimized_links, target_name):
    cleaned_paths = set()
    for url in optimized_links:
        match = re.search(r'/wp-content/plugins/([^/]+)', url)
        if match:
            plugin_name = match.group(1)
            cleaned_path = f"{target_name}/wp-content/plugins/{plugin_name}"
            cleaned_paths.add(cleaned_path)
    cleaned_json_filename = get_cleaned_json_filename(folder_path)
    with open(cleaned_json_filename, 'w') as cleaned_json_file:
        json.dump(list(cleaned_paths), cleaned_json_file, indent=4)
    return cleaned_json_filename

def get_cleaned_json_filename(folder_path):
    site_name = os.path.basename(folder_path)
    cleaned_json_filename = f"{site_name}_temiz.json"
    return os.path.join(folder_path, cleaned_json_filename)

def check_and_save_status_codes(cleaned_json_filename, *file_extensions):
    try:
        with open(cleaned_json_filename, 'r') as cleaned_json_file:
            data = json.load(cleaned_json_file)
            status_codes_data = []
            for url in data:
                for file_extension in file_extensions:
                    new_url = url + file_extension
                    if not new_url.startswith('http://') and not new_url.startswith('https://'):
                        new_url = 'http://' + new_url
                    response = requests.get(new_url)
                    status_code = response.status_code
                    url_status_dict = {'url': new_url, 'status_code': status_code}
                    status_codes_data.append(url_status_dict)
                    print(f"{found} {new_url} - Status kodu: {status_code} {reset_color}")
            status_codes_json_filename = cleaned_json_filename.replace('_temiz.json', '_status_codes.json')
            with open(status_codes_json_filename, 'w') as status_codes_json_file:
                json.dump(status_codes_data, status_codes_json_file, indent=4)
            print(f"{found} Status kodları şuraya kayıt edildi {status_codes_json_filename}.{reset_color}")
            return status_codes_data
    except Exception as e:
        print_error_message(f"(3) Hata meydana geldi: {e}")

def sonuc(cleaned_json_filename, status_codes_data):
    try:
        # Read and print the contents of plugins.json
        plugins_json_filename = os.path.join(os.path.dirname(cleaned_json_filename), "plugins.json")
        if os.path.exists(plugins_json_filename):
            with open(plugins_json_filename, 'r') as plugins_file:
                plugins_data = json.load(plugins_file)

                print(f"{yellow_wpcrawl} Plugins.json içeriği: {reset_color}")
                for plugin in plugins_data:
                    plugin_name = plugin.get('plugin_name', 'Bilinmeyen Eklenti')
                    version = plugin.get('version', 'Bilinmeyen Versiyon')
                    print(f"{yellow_wpcrawl} Eklenti Adı: {plugin_name}\nVersiyon: {version}\n {reset_color}")  # Alt alta yazdır

        else:
            print(f"{not_found} plugins.json dosyası bulunamadı: {plugins_json_filename}.{reset_color}")

        # Only show status codes
        for file_dict in status_codes_data:
            if file_dict['status_code'] == 200:
                print(f"{found} {file_dict['url']} - Status kodu: {file_dict['status_code']} {reset_color}")

    except Exception as e:
        print_error_message(f"(4) Hata meydana geldi: {e}")

def print_error_message(message):
    print(f"{not_found} Error: {message} {reset_color}")