# Inquiry v1.1
# Signature: Yasin Yaşar

import requests
import json
import threading
from lib.color import not_found, yellow_wpcrawl, reset_color

def fetch_subdomain_status(common_name, results):
    try:
        response = requests.get(f"http://{common_name}", timeout=5)
        status_code = response.status_code
        if status_code == 200:
            results.append({"subdomain": common_name, "status_code": status_code})
    except requests.exceptions.RequestException:
        pass

def find_subdomains(domain):
    print(f"{yellow_wpcrawl}[+] Subdomain tespiti başlatılıyor: {domain}{reset_color}")
    url = f"https://crt.sh/?q={domain}&output=json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"{yellow_wpcrawl}[+] CRT.sh'den yanıt alındı: {domain}{reset_color}")

        subdomains = []
        seen_subdomains = set()
        json_data = json.loads(response.text)

        results = []
        threads = []

        for item in json_data:
            common_name = item.get("common_name")
            if common_name and not common_name.startswith("www.") and common_name not in seen_subdomains and common_name != domain:
                seen_subdomains.add(common_name)
                thread = threading.Thread(target=fetch_subdomain_status, args=(common_name, results))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()
            
        if results:
            print_subdomains(results)
        else:
            print(f"{not_found}Alt etki alanı bulunamadı.{reset_color}")

    except requests.exceptions.HTTPError as e:
        if 500 <= response.status_code < 600:
            print(f"{not_found}CRT.sh şuanda kullanılabilir değil, lütfen daha sonra tekrar deneyiniz. (Önerilen 5 dakika){reset_color}")
        else:
            print(f"{not_found}Hata: {e}{reset_color}")
    except requests.exceptions.RequestException as e:
        print(f"{not_found}Bağlantı hatası: {e}{reset_color}")

def print_subdomains(subdomains):
    print(f"{yellow_wpcrawl}\n[+] Bulunan Alt Etki Alanları:{reset_color}")
    
    for i, entry in enumerate(subdomains):
        if i == len(subdomains) - 1:
            # Son alt alan adı için
            print(f"{yellow_wpcrawl} └─ Alt Alan Adı: {entry['subdomain']}{reset_color}")
            print(f"{yellow_wpcrawl}    Durum Kodu: {entry['status_code']}{reset_color}")
        else:
            # Diğer alt alan adları için
            print(f"{yellow_wpcrawl} └─ Alt Alan Adı: {entry['subdomain']}{reset_color}")
            print(f"{yellow_wpcrawl} |   Durum Kodu: {entry['status_code']}{reset_color}")
            print(f"{yellow_wpcrawl} |{reset_color}")
