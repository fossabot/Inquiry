# Inquiry v1.1
# Signature: Yasin Yaşar
import os

def run_nmap_vulners(target):
    output_folder = "data/host"
    folder_path = os.path.join(output_folder, target)
    os.makedirs(folder_path, exist_ok=True)

    command = ["nmap", "-Pn", "-v", "-sV", target, "--script=vulners", "-oX", os.path.join(folder_path, f'nmap_vulners_{target}.xml')]
    os.system(" ".join(command))
