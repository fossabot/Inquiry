# Inquiry v1.0 dnsCrawl
# Signature: Yasin Yaşar

import socket
import concurrent.futures
from typing import Dict, Any, List
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
            print(f"Hata ({record_type}): {str(e)}")
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
        output = [f"\n[+] DNS Kayıtları: {results['domain']}\n"]
        
        if results['A']:
            output.append("[+] A Kayıtları:")
            output.extend(f"  └─ {ip}" for ip in results['A'])
            
        if results['CNAME']:
            output.append("\n[+] CNAME Kayıtları:")
            output.extend(f"  └─ {cname}" for cname in results['CNAME'])
            
        if results['MX']:
            output.append("\n[+] MX Kayıtları:")
            output.extend(f"  └─ {host} (öncelik: {pref})" 
                         for pref, host in sorted(results['MX']))
            
        if results['TXT']:
            output.append("\n[+] TXT Kayıtları:")
            output.extend(f"  └─ {txt}" for txt in results['TXT'])
            
        if results['NS']:
            output.append("\n[+] NS Kayıtları:")
            output.extend(f"  └─ {ns}" for ns in results['NS'])
            
        return '\n'.join(output)

def handle_dns_records(args):
    if args.dns_records:
        print("\n=== DNS Kayıt Kontrolü Başlatılıyor ===")
        checker = DNSChecker()
        results = checker.check_all(args.url)
        print(checker.format_results(results))
