# Inquiry v1.0 shodanCrawl
# Signature: Yasin Yaşar

import requests
from bs4 import BeautifulSoup
import json
import os
from typing import List, Dict, Union
from requests.exceptions import RequestException
from modules.color import found, not_found, reset_color, yellow_wpcrawl, cobalt_blue

class ShodanCrawler:
    def __init__(self):
        pass

    def shodanScrape(self, url: str, target_name: str) -> None:
        output_folder = os.path.join("data", "domain", target_name)
        os.makedirs(output_folder, exist_ok=True)

        try:
            print(f"{cobalt_blue} {target_name} için {url} adresinden veri alınıyor... {reset_color}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except RequestException as e:
            print(f"{not_found} {url} adresinden veri alınırken hata oluştu: {e} {reset_color}")
            return

        print(f"{found} Sayfa başarıyla yüklendi. {reset_color}\n")

        soup = BeautifulSoup(response.content, "html.parser")
        records = self.extractRecords(soup)

        if records:
            self.displayRecords(records)
            self.saveRecords(records, output_folder, target_name)
        else:
            print(f"{not_found} {target_name} için kayıt bulunamadı. {reset_color}")

    def extractRecords(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        records = []

        # Hata mesajı div'ini kontrol et
        error_div = soup.find("div", class_="alert alert-error")
        if error_div:
            error_message = error_div.find("p")
            if error_message and "No information available for that domain." in error_message.text:
                print(f"{not_found} Aranan alan ile ilgili kayıtlı veri yok. {reset_color}")
                return records

        # Normal kayıtları bulma
        domain_records_div = soup.find("div", class_="nine columns card card-padding card-yellow")
        if domain_records_div:
            table = domain_records_div.find("table", class_="u-full-width")
            if table:
                for row in table.find_all("tr"):
                    columns = row.find_all("td")
                    if len(columns) == 3:
                        record_type = columns[1].text.strip()
                        if record_type == "A":
                            link = columns[2].find("a", class_="text-dark")
                            if link:
                                record_value = link.text.strip()
                                records.append({"type": record_type, "ip_address": record_value})
                        else:
                            record_value = columns[2].text.strip()
                            records.append({"type": record_type, "value": record_value})
            else:
                print(f"{not_found} Kart sarı div içinde tablo bulunamadı. {reset_color}")
        else:
            print(f"{not_found} Alan kayıtları div'i (kart sarı) bulunamadı. {reset_color}")

        return records

    def saveRecords(self, records: List[Dict[str, str]], output_folder: str, target_name: str) -> None:
        output_file = os.path.join(output_folder, f"{target_name}_shodan_results.json")
        
        try:
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(records, json_file, ensure_ascii=False, indent=2)
            print(f"{cobalt_blue} Kayıtlar '{output_file}' dosyasına kaydedildi. {reset_color}\n")
        except IOError as e:
            print(f"{not_found} Kayıtları dosyaya kaydederken hata oluştu: {e} {reset_color}")

    def displayRecords(self, records: List[Dict[str, str]], limit: int = 50) -> None:
        print(f"{yellow_wpcrawl} \nÇıkarılan Kayıtlar: {reset_color}\n")
        
        for i, record in enumerate(records):
            if i < limit:
                if "ip_address" in record:
                    print(f"{yellow_wpcrawl} Tür: {record['type']}, IP Adresi: {record['ip_address']} {reset_color}")
                else:
                    print(f"{yellow_wpcrawl} Tür: {record['type']}, Değer: {record['value']} {reset_color}")
            else:
                print(f"{not_found} 50'den fazla kayıt bulundu. Tam sonuçlar için JSON dosyasına bakın. {reset_color}\n")
                break

    def handleShodanDomains(self, domains: Union[str, List[str]]) -> None:
        if isinstance(domains, str):
            domains = [domains]
            
        for domain in domains:
            if os.path.isfile(domain):
                try:
                    with open(domain, 'r') as file:
                        domain_list = [line.strip() for line in file if line.strip()]
                    self.processDomains(domain_list)
                except IOError as e:
                    print(f"{not_found} {domain} alan dosyası okunurken hata oluştu: {e} {reset_color}")
            else:
                self.processDomains([domain])

    def processDomains(self, domains: List[str]) -> None:
        for domain in domains:
            url = f"https://www.shodan.io/domain/{domain}"
            self.shodanScrape(url, domain)
