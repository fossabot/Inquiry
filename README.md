<h1 align="center">
  <a href="https://github.com/sahici/Inquiry"><img src="https://raw.githubusercontent.com/sahici/sahici/refs/heads/main/inquiry.jpg" alt="Inquiry" width="400" height="400"></a>
  <br>
  Inquiry
  <br>
</h1>

<h4 align="center">Red Team Tools</h4>

Inquiry, belirtilen alan adları üzerinde çeşitli keşif görevleri gerçekleştirmek için tasarlanmış çok amaçlı bir siber güvenlik aracıdır. Subdomain keşfi, zafiyet taraması, WordPress eklenti/version belirleme gibi çeşitli sıfırdan yazılmış modüller kullanıyor.

## Özellikler

- **Subdomain Keşfi**: Hedef alan adıyla ilişkili alt alan adlarını tespit eder.
- **DNS Taraması**: Hedef alan adı hakkında DNS kayıtlarını tespit eder.
- **WordPress Tarama**: Hedef site üzerindeki yüklü WordPress eklentilerini tanımlar ve kaydeder.
- **Nmap Zafiyet Taraması**: Hedef alan adı ile ilgili zafiyetleri kontrol etmek için Nmap çalıştırır.

## Yükleme Ve Kurulum

- **Programı kurmak için aşağıdaki komutları çalıştırın:**

```bash
git clone https://github.com/sahici/Inquiry.git
cd Inquiry
sudo snap install nmap
pip3 install -r requirements.txt
```

## Kullanım Örnekleri
```bash
python3 main.py -u example.com --subfinder
```
```bash
python3 main.py -u example.com --subfinder --dns-records
```
## Süreklilik:

- Inquiry yazılımı sürekli olarak aktif bir şekilde geliştirilmeye devam ediyor. Mevcut modüller üzerinde düzenli güncellemeler yapılıyor ve yeni modüller için geliştirme çalışmaları çoktan başlamış durumda.

## Özel Teşekkürler:
- **Bel ağrılarına katlanabildiği için kendime teşekkür ederim :D.**

- ## İletişim:
- Linkedin: https://www.linkedin.com/in/yasinyasarai/
- İnstagram: https://www.instagram.com/yyasar.yasin/
