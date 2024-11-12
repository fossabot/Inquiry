# Inquiry v1.1
# Signature: Yasin Yaşar
import requests
import re
from lib.color import yellow_wpcrawl, not_found, reset_color

def crawl(url):
    try:
        # Siteye istek gönderiyoruz
        istek = requests.get(f"https://{url}/lib/upgrade.txt")
        
        # Eğer başarılı bir cevap alırsak
        if istek.status_code == 200:
            response_text = istek.text
            
            # "===" arasında bir version kodu arıyoruz
            match = re.search(r"===\s*(.*?)\s*===", response_text)
            
            if match:
                version_code = match.group(1)
                print(f"{yellow_wpcrawl}[+] Version Kodu: {version_code}{reset_color}")
            
            else:
                # Version kodu bulunamazsa
                print(f"{not_found}[!] Version Kodu Tespit Edilemedi{reset_color}")
        
        else:
            # HTTP isteği başarısız olduysa
            print(f"{not_found}[!] İstek başarısız oldu, HTTP Durum Kodu: {istek.status_code}{reset_color}")
    
    except requests.exceptions.RequestException as e:
        # Hata oluşursa
        print(f"{not_found}[!] Bir Hata oluştu: {e}{reset_color}")
