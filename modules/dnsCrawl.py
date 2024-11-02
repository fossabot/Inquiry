# Inquiry v1.0 dnsCrawl
# Signature: Yasin Yaşar

import socket
import concurrent.futures
from typing import Dict, Any, List
from modules.color import not_found, reset_color, yellow_wpcrawl
import dns.resolver

class DNSChecker:
    def __init__(self, timeout: int = 3):
        self.timeout = timeout
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = timeout
    
    def get_records(self, domain: str, record_type: str) -> List[str]:
        try:
            if record_type == 'A':
                return socket.gethostbyname_ex(domain)[2]
            
            answers = self.resolver.resolve(domain, record_type)
            
            if record_type == 'MX':
                return [(answer.preference, str(answer.exchange)) for answer in answers]
            elif record_type == 'TXT':
                return [str(answer).strip('"') for answer in answers]
            else:
                return [str(answer) for answer in answers]
                
        except Exception as e:
            print(f"{not_found} Hata ({record_type}): {str(e)} {reset_color}")
            return []

    def check_all(self, domain: str) -> Dict[str, Any]:
        record_types = ['A', 'CNAME', 'MX', 'TXT', 'NS']
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_type = {
                executor.submit(self.get_records, domain, record_type): record_type
                for record_type in record_types
            }
            
            results = {'domain': domain}
            for future in concurrent.futures.as_completed(future_to_type):
                record_type = future_to_type[future]
                results[record_type] = future.result()
                
        return results

    def format_results(self, results: Dict[str, Any]) -> str:
        output = [f"{yellow_wpcrawl} \n[+] DNS Kayıtları: {results['domain']}\n {reset_color}"]
        
        if results['A']:
            output.append(f"{yellow_wpcrawl} [+] A Kayıtları: {reset_color}")
            output.extend(f"{yellow_wpcrawl}  └─ {ip} {reset_color}" for ip in results['A'])
            
        if results['CNAME']:
            output.append(f"{yellow_wpcrawl} \n[+] CNAME Kayıtları: {reset_color}")
            output.extend(f"{yellow_wpcrawl}  └─ {cname} {reset_color}" for cname in results['CNAME'])
            
        if results['MX']:
            output.append(f"{yellow_wpcrawl} \n[+] MX Kayıtları: {reset_color}")
            output.extend(f"{yellow_wpcrawl}  └─ {host} (öncelik: {pref}) {reset_color}" 
                         for pref, host in sorted(results['MX']))
            
        if results['TXT']:
            output.append(f"{yellow_wpcrawl} \n[+] TXT Kayıtları: {reset_color}")
            output.extend(f"{yellow_wpcrawl}  └─ {txt} {reset_color}" for txt in results['TXT'])
            
        if results['NS']:
            output.append(f"{yellow_wpcrawl} \n[+] NS Kayıtları: {reset_color}")
            output.extend(f"{yellow_wpcrawl}  └─ {ns} {reset_color}" for ns in results['NS'])
            
        return '\n'.join(output)

def handle_dns_records(args):
    if args.dns_records:
        print(f"{not_found} \n=== DNS Kayıt Kontrolü Başlatılıyor === {reset_color}")
        checker = DNSChecker()
        results = checker.check_all(args.url)
        print(checker.format_results(results))
