import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
from PIL import Image, ImageTk
import hashlib

def hash_dogrula(dosya_yolu, beklenen_hash):
    with open(dosya_yolu, 'rb') as f:
        dosya_verisi = f.read()
        dosya_hash = hashlib.sha512(dosya_verisi).hexdigest()
        return dosya_hash == beklenen_hash

def dms_donustur(coord):
    lat, lon = map(float, coord.split(","))
    lat_deg = int(lat)
    lat_min = int((lat - lat_deg) * 60)
    lat_sec = (lat - lat_deg - lat_min / 60) * 3600

    lon_deg = int(lon)
    lon_min = int((lon - lon_deg) * 60)
    lon_sec = (lon - lon_deg - lon_min / 60) * 3600

    lat_dms = f"{abs(lat_deg)}°{abs(lat_min)}'{abs(lat_sec):.1f}\"{'N' if lat_deg >= 0 else 'S'}"
    lon_dms = f"{abs(lon_deg)}°{abs(lon_min)}'{abs(lon_sec):.1f}\"{'E' if lon_deg >= 0 else 'W'}"

    return lat_dms, lon_dms

def adres_bilgisi_al(coord):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={coord.split(',')[0]}&lon={coord.split(',')[1]}"
        yanit = requests.get(url)
        yanit.raise_for_status()  # HTTP hata durumlarını kontrol et
        veriler = yanit.json()

        if 'error' not in veriler:
            adres = veriler.get('display_name', 'Adres bulunamadı.')
            return adres
        else:
            return "Adres bulunamadı."
    except requests.exceptions.RequestException as e:
        return f"Adres alınamadı: {e}"
    except Exception as e:
        return f"Bir hata oluştu: {e}"

def ip_sorgula():
    ip = girdi_ip.get()
    if not ip:
        messagebox.showerror("Hata", "Lütfen bir IP adresi girin.")
        return

    try:
        yanit = requests.get(f'https://ipinfo.io/{ip}/json')
        yanit.raise_for_status()  # HTTP hata durumlarını kontrol et
        veriler = yanit.json()

        if yanit.status_code != 200:
            messagebox.showerror("Hata", "IP adresi bilgileri alınamadı.")
            return
        
        lat_lon = veriler.get('loc', 'N/A')
        if lat_lon != 'N/A':
            lat_dms, lon_dms = dms_donustur(lat_lon)
            adres = adres_bilgisi_al(lat_lon)
        else:
            lat_dms, lon_dms = "N/A", "N/A"
            adres = "Adres bulunamadı."

        bilgiler = (
            f"IP: {veriler.get('ip', 'N/A')}\n"
            f"Hostname: {veriler.get('hostname', 'N/A')}\n"
            f"Şehir: {veriler.get('city', 'N/A')}\n"
            f"Bölge: {veriler.get('region', 'N/A')}\n"
            f"Ülke: {veriler.get('country', 'N/A')}\n"
            f"Konum: {lat_dms}, {lon_dms}\n"
            f"Adres: {adres}\n"
            f"Org: {veriler.get('org', 'N/A')}\n"
            f"Posta Kodu: {veriler.get('postal', 'N/A')}\n"
            f"Zaman Dilimi: {veriler.get('timezone', 'N/A')}\n"
        )
        text_bilgiler.delete("1.0", tk.END)
        text_bilgiler.insert(tk.END, bilgiler)
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Hata", f"API isteği başarısız oldu: {e}")
    except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu: {e}")

pencere = tk.Tk()
pencere.title("NMSIPScanner")

logo_yolu = 'logo.png'
logo_hash = "f5d8ab7499d2762c2ef8b8d3de87fc980b32d504eb5e8d810279ea80f697857eb3c18ccda4e87d448a9a3daba6770ac32c84d281d16eb574a8fb42fd433d5832"

if not hash_dogrula(logo_yolu, logo_hash):
    messagebox.showerror("Hata", "logo.png dosyasının hash değeri doğru değil.")
    pencere.destroy()
    exit()

logo_resim = Image.open(logo_yolu)
logo_resim = logo_resim.resize((281, 281), Image.LANCZOS)
logo_resim = ImageTk.PhotoImage(logo_resim)
logo_etiketi = tk.Label(pencere, image=logo_resim)
logo_etiketi.pack(padx=10, pady=10)

cerceve = tk.Frame(pencere)
cerceve.pack(pady=10)

etiket_ip = tk.Label(cerceve, text="IP Adresi:")
etiket_ip.pack(side=tk.LEFT)

girdi_ip = ttk.Entry(cerceve)
girdi_ip.pack(side=tk.LEFT, padx=5)

buton_sorgula = ttk.Button(cerceve, text="Sorgula", command=ip_sorgula)
buton_sorgula.pack(side=tk.LEFT)

text_bilgiler = tk.Text(pencere, height=20, width=60)
text_bilgiler.pack(pady=10)

pencere.mainloop()

