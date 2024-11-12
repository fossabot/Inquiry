# Inquiry v1.1
# Signature: Yasin Yaşar

import argparse
import os
import random
from modules.dnsCrawl import DNSChecker
import modules.WPCrawl as WPCrawl
import modules.nmapDracula as nmapDracula
import modules.MoodleCrawl as MoodleCrawl
import modules.subfinder as subfinder
from lib.color import ascii_art, reset_color, yellow_wpcrawl
from colorama import init

def process_domain_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def display_ascii_art():
    art_directory = os.path.join(os.path.dirname(__file__), "lib", "ascii-art")
    
    try:
        # Get a list of all ASCII art files in the directory
        art_files = [f for f in os.listdir(art_directory) if f.endswith('.txt')]
        
        if not art_files:
            print("ASCII art dosyası bulunamadı.")
            return
        
        # Select a random ASCII art file
        selected_art_file = random.choice(art_files)
        art_file_path = os.path.join(art_directory, selected_art_file)
        
        with open(art_file_path, 'r', encoding='utf-8') as file:
            art = file.read()
            print(f"{ascii_art}{art}{reset_color}")

    except Exception as e:
        print(f"ASCII art yüklenemedi: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Dracula TOOL")
    parser.add_argument("-u", "--url", help="Hedef alan adı.")
    parser.add_argument("-f", "--file", help="Hedef alan adları içeren dosya yolu.")
    parser.add_argument("--dns-records", dest="dns_records", action='store_true', help="Hedef hakkında DNS kayıtlarını alır.")
    parser.add_argument("--subfinder", dest="subfinder_domain", action='store_true', help="Hedef Subdomain tespiti yapar.")
    parser.add_argument("--wordpress-crawl", dest="wordpress_crawl", action='store_true', help="Hedef WordPress Pluginglerini bulur ve kayıt altına alır.")
    parser.add_argument("--moodle-crawl", dest="moodle_crawl", action="store_true", help="Hedefin Moodle Version bilgilerini getirir.")
    parser.add_argument("--nmap-vulners", dest="nmap_vulners", action='store_true', help="Hedefe Nmap Vulners scripti kullanarak zafiyet testi yapar.")
    args = parser.parse_args()

    try:
        # Hedef alan adı kontrolü
        urls = []
        
        if args.url:
            urls.append(args.url)

        if args.file:
            if not os.path.isfile(args.file):
                print(ascii_art + "Belirtilen dosya bulunamadı veya geçersiz bir dosya yolu." + reset_color)
                return
            urls.extend(process_domain_from_file(args.file))

        if not urls:
            print(ascii_art + "Lütfen bir hedef alan adı veya dosya belirtin." + reset_color)
            return

        for url in urls:
            print(f"{yellow_wpcrawl} \nİşlem yapılıyor: {url} {reset_color}")

            ### SUBFINDER ###
            if args.subfinder_domain:
                subfinder.find_subdomains(url)

            ### DNSCRAWL ###
            if args.dns_records:
                checker = DNSChecker()
                results = checker.check_all(url)
                print(checker.format_results(results))

            ### WPCRAWL ###
            if args.wordpress_crawl:
                WPCrawl.run_wordpress_crawl([url])
            
            ### Moodle Crawl ###
            if args.moodle_crawl:
                MoodleCrawl.crawl(url)
                
            ### NMAP VULNERS SCRIPT ###
            if args.nmap_vulners:
                nmapDracula.run_nmap_vulners([url])

    except KeyboardInterrupt:
        print("\nProgram durduruldu. Çıkılıyor...")
    except Exception as e:
        print(f"{ascii_art} Hata oluştu: {e} {reset_color}")

if __name__ == "__main__":
    # Colorama'yı başlat
    init(autoreset=True)
    display_ascii_art()
    main()
