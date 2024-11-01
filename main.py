# Inquiry v1.0
# Signature: Yasin Yaşar

import argparse
import os
import random
from modules.dnsCrawl import DNSChecker
import modules.WPCrawl as WPCrawl
import modules.nmapDracula as nmapDracula
import modules.subfinder as subfinder
from modules.color import ascii_art, reset_color
from colorama import init

def process_domain_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def display_ascii_art():
    art_directory = os.path.join(os.path.dirname(__file__), "modules", "ascii-art")
    
    try:
        art_files = [f for f in os.listdir(art_directory) if f.endswith('.txt')]
        
        if not art_files:
            print("ASCII art dosyası bulunamadı.")
            return
        
        selected_art_file = random.choice(art_files)
        art_file_path = os.path.join(art_directory, selected_art_file)
        
        with open(art_file_path, 'r', encoding='utf-8') as file:
            art = file.read()
            print(f"{ascii_art}{art}{reset_color}")

    except Exception as e:
        print(f"ASCII art yüklenemedi: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Dracula TOOL")
    parser.add_argument("--nmap-vulners", dest="nmap_vulners", action='store_true', help="Hedef hakkında vuln ile ilgili bilgi almak için.")
    parser.add_argument("--dns-records", dest="dns_records", action='store_true', help="Hedef hakkında DNS kayıtlarını alır.")
    parser.add_argument("--wordpress-crawl", dest="wordpress_crawl", action='store_true', help="Hedef WordPress Pluginglerini bulur ve kayıt altına alır.")
    parser.add_argument("--subfinder", dest="subfinder_domain", action='store_true', help="Subdomain tespiti yapar.")
    parser.add_argument("-u", "--url", help="Hedef alan adı.", required=True)

    args = parser.parse_args()

    try:
        # Hedef alan adı kontrolü
        if args.url:
            ### SUBFINDER ###
            if args.subfinder_domain:
                subfinder.find_subdomains(args.url)
                print("--- Subfinder İşlemi Bitti ---")

            ### DNSCRAWL ###
            if args.dns_records:
                print("\n=== DNS Kayıt Kontrolü Başlatılıyor ===")
                checker = DNSChecker()
                results = checker.check_all(args.url)
                print(checker.format_results(results))
                print("--- DNSCRAWL İşlemi Bitti ---")

            ### WPCRAWL ###
            if args.wordpress_crawl:
                WPCrawl.run_wordpress_crawl([args.url])
                print("--- WordPress Crawl İşlemi Bitti ---")

            ### NMAP VULNERS SCRIPT ###
            if args.nmap_vulners:
                nmapDracula.run_nmap_vulners([args.url])
                print("--- Nmap Vulners İşlemi Bitti ---")

    except KeyboardInterrupt:
        print("\nProgram durduruldu. Çıkılıyor...")
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    # Colorama'yı başlat
    init(autoreset=True)
    display_ascii_art()
    main()
