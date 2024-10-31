# Inquiry v1.0 subfinder
# Signature: Yasin Yaşar

import requests
import json
import threading
from modules.color import found, not_found, yellow_wpcrawl, reset_color

def fetch_subdomain_status(common_name, results):
    try:
        response = requests.get(f"http://{common_name}", timeout=5)
        status_code = response.status_code
        if status_code == 200:
            results.append({"subdomain": common_name, "status_code": status_code})
    except requests.exceptions.RequestException:
        pass

def find_subdomains(domain):
    print(f"{yellow_wpcrawl} Subdomain tespiti başlatılıyor: {domain} {reset_color}")
    url = f"https://crt.sh/?q={domain}&output=json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Bu, 4xx ve 5xx hatalarını tetikler
        print(f"{yellow_wpcrawl} CRT.sh'den yanıt alındı: {domain} {reset_color}")

        subdomains = []
        seen_subdomains = set()
        json_data = json.loads(response.text)

        results = []  # Alt alan adlarını saklamak için

        # Alt alan adlarını işlemek için thread'ler oluşturur
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
            print("Alt etki alanı bulunamadı.")

    except requests.exceptions.HTTPError as e:
        if 500 <= response.status_code < 600:
            print(f"{not_found} CRT.sh şuanda kullanılabilir değil, lütfen daha sonra tekrar deneyiniz. (Önerilen 5 dakika) {reset_color}")
        else:
            print(f"Hata: {e}")
    except requests.exceptions.RequestException as e:
        print(f"{not_found} Bağlantı hatası: {e} {reset_color}")

def print_subdomains(subdomains):
    print(f"{found} \nEkrana Yazdırılan Alt Etki Alanları: {reset_color}")
    for entry in subdomains:
        print(f"{found} {entry['subdomain']} ({entry['status_code']}) {reset_color}")
