# Inquiry v1.1
# Signature: Yasin Yaşar
import requests
import re
from lib.color import yellow_wpcrawl, not_found, reset_color

def crawl(url):
    try:
        istek = requests.get(f"https://{url}/lib/upgrade.txt")
        
        if istek.status_code == 200:
            response_text = istek.text
           
            match = re.search(r"===\s*(.*?)\s*===", response_text)
            
            if match:
                version_code = match.group(1)
                print(f"{yellow_wpcrawl}[+] Version Kodu: {version_code}{reset_color}")
            
            else:
                print(f"{not_found}[!] Version Kodu Tespit Edilemedi{reset_color}")
        
        else:
            print(f"{not_found}[!] İstek başarısız oldu, HTTP Durum Kodu: {istek.status_code}{reset_color}")
    
    except requests.exceptions.RequestException as e:
        print(f"{not_found}[!] Bir Hata oluştu: {e}{reset_color}")
