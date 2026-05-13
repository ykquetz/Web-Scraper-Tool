import customtkinter as ctk
import requests
from bs4 import BeautifulSoup
import time
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")  

pencere = ctk.CTk()  
pencere.title("Web scraping device")
pencere.geometry("1600x900") 

arama_ekrani = ctk.CTkFrame(pencere, fg_color="transparent")
sonuc_ekrani = ctk.CTkFrame(pencere, fg_color="transparent")


baslik_etiketi = ctk.CTkLabel(arama_ekrani, text="Web Scraper", font=("Cambria", 80, "bold"))
baslik_etiketi.pack(pady=(100, 20)) 

url_kutusu = ctk.CTkEntry(arama_ekrani, placeholder_text="Site adresini girin (örn: haberturk.com)", width=500, height=45)
url_kutusu.pack(pady=10)

log_ekrani = ctk.CTkTextbox(arama_ekrani, width=500, height=150, font=("Consolas", 13), text_color="#00FF00", fg_color="#1E1E1E")
log_ekrani.pack(pady=20)
log_ekrani.insert("0.0", "Sistem hazır. Taranacak URL bekleniyor. Lütfen URL'yi girip taramayı başlatın.\n")
log_ekrani.configure(state="disabled") 

def taramayi_baslat():
    girilen_url = url_kutusu.get().strip()
    if not girilen_url:
        return
    
    log_ekrani.configure(state="normal")
    log_ekrani.delete("0.0", "end")
    
   
    log_ekrani.insert("end", f"[*] {girilen_url} adresine bağlantı isteği gönderiliyor...\n")
    pencere.update()
    
    url_listesi = []
    if girilen_url.startswith("http://") or girilen_url.startswith("https://"):
        url_listesi.append(girilen_url)
    else:
        url_listesi.append("https://" + girilen_url)
        url_listesi.append("http://" + girilen_url)
        
    test = None
    basarili_url = ""
    
    for u in url_listesi:
        try:
            log_ekrani.insert("end", f"[*] {u} deneniyor...\n")
            pencere.update()
            test = requests.get(u, timeout=5)
            basarili_url = u
            break
        except requests.exceptions.RequestException:
            continue
            
    #
    if not test or test.status_code != 200:
        log_ekrani.insert("end", "[!] Hata: Siteye ulaşılamadı. Adresi kontrol edin.\n")
        log_ekrani.configure(state="disabled")
        return

    log_ekrani.insert("end", f"[+] HTTP 200 OK: Siteye başarıyla ulaşıldı!\n")
    pencere.update()
    
    
    ping = int(test.elapsed.total_seconds() * 1000)
    log_ekrani.insert("end", f"[*] Gerçek Ping ölçüldü: {ping} ms\n")
    log_ekrani.insert("end", "[*] Veriler BeautifulSoup ile ayrıştırılıyor...\n")
    pencere.update()
    
    site = BeautifulSoup(test.text, "html.parser")
    
  
    h1_metin = "--- ANA BAŞLIKLAR (H1) \n\n"
    for baslik in site.find_all("h1"):
        h1_metin += f"- {baslik.get_text().strip()}\n"

    
    h2_metin = "--- ALT BAŞLIKLAR (H2) \n\n"
    for baslik in site.find_all("h2")[:20]:
        h2_metin += f"• {baslik.get_text().strip()}\n"

    
    li_metin = "--- LİSTELER (LI)\n\n"
    for i, ogre in enumerate(site.find_all("li")[:100]):
        li_metin += f"{i+1}. {ogre.get_text().strip()}\n"

   
    link_metin = "--- BAĞLANTILAR \n\n"
    sayac = 0
    for link in site.find_all("a"):
        url2 = link.get("href")           
        metin = link.get_text().strip() 
        if metin and url2:
            sayac += 1
            link_metin += f"{sayac}. {metin}\n   Adres: {url2}\n\n"
        if sayac == 100:
            break
    if sayac == 0:
        link_metin += "Başka bir sayfaya geçiş bulunmuyor.\n"

 
    resim_metin = "--- RESİMLER \n\n"
    sayac_resim = 0
    for resim in site.find_all("img"):
        resimurl = resim.get("src")
        resimaciklama = resim.get("alt")
        if resimurl:
            sayac_resim += 1
            aciklama = resimaciklama.strip() if resimaciklama else "(Açıklama yok)"
            resim_metin += f"{sayac_resim}. {aciklama}\n   Adres: {resimurl}\n\n"
        if sayac_resim == 20:
            break
    if sayac_resim == 0:
        resim_metin += "Sitede herhangi bir resim bulunamadı.\n"

   
    log_ekrani.insert("end", "[+] Tarama tamamlandı! Sonuç ekranına geçiliyor...\n")
    pencere.update()
    time.sleep(2)
    log_ekrani.configure(state="disabled") 
    
    arama_ekrani.pack_forget()
    sonuc_ekrani.pack(fill="both", expand=True)
    
    
    sekme_basligi = site.find("title").text if site.find("title") else basarili_url
    sonuc_baslik.configure(text=f"Taranan Hedef: {sekme_basligi}")
    ping_etiketi.configure(text=f"Ping: {ping} ms")
    
    
    kutuya_yaz(kutu_h1, h1_metin)
    kutuya_yaz(kutu_h2, h2_metin)
    kutuya_yaz(kutu_liste, li_metin)
    kutuya_yaz(kutu_link, link_metin)
    kutuya_yaz(kutu_resim, resim_metin)

tara_butonu = ctk.CTkButton(arama_ekrani, text="Siteyi tara", command=taramayi_baslat, font=("Segoe UI", 15, "bold"), height=40)
tara_butonu.pack(pady=10)

arama_ekrani.pack(fill="both", expand=True)


ust_bilgi_frame = ctk.CTkFrame(sonuc_ekrani, fg_color="transparent")
ust_bilgi_frame.pack(fill="x", padx=25, pady=(15, 0))

sonuc_baslik = ctk.CTkLabel(ust_bilgi_frame, text="Taranan Hedef: -", font=("Segoe UI", 18, "bold"), text_color="#3498DB")
sonuc_baslik.pack(side="left")

ping_etiketi = ctk.CTkLabel(ust_bilgi_frame, text="Ping: -- ms", font=("Consolas", 16, "bold"), text_color="#2ECC71")
ping_etiketi.pack(side="right")

grid_frame = ctk.CTkFrame(sonuc_ekrani, fg_color="transparent")
grid_frame.pack(fill="both", expand=True, padx=15, pady=10)

grid_frame.columnconfigure((0, 1, 2), weight=1) 
grid_frame.rowconfigure((0, 1), weight=1)       

def kutuya_yaz(kutu, metin):
    kutu.configure(state="normal") 
    kutu.delete("0.0", "end")      
    kutu.insert("0.0", metin)      
    kutu.configure(state="disabled") 

kutu_h1 = ctk.CTkTextbox(grid_frame, font=("Consolas", 13), state="disabled")
kutu_h1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

kutu_h2 = ctk.CTkTextbox(grid_frame, font=("Consolas", 13), state="disabled")
kutu_h2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

kutu_liste = ctk.CTkTextbox(grid_frame, font=("Consolas", 13), state="disabled")
kutu_liste.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

kutu_link = ctk.CTkTextbox(grid_frame, font=("Consolas", 13), state="disabled")
kutu_link.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

kutu_resim = ctk.CTkTextbox(grid_frame, font=("Consolas", 13), state="disabled")
kutu_resim.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

hizli_arama_frame = ctk.CTkFrame(grid_frame, fg_color="#1E1E1E") 
hizli_arama_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

icerik_frame = ctk.CTkFrame(hizli_arama_frame, fg_color="transparent")
icerik_frame.pack(expand=True)

yeni_url_etiket = ctk.CTkLabel(icerik_frame, text="Yeni Hedef Tarama", font=("Segoe UI", 16, "bold"))
yeni_url_etiket.pack(pady=(0, 10))

yeni_url_kutusu = ctk.CTkEntry(icerik_frame, placeholder_text="Yeni link girin...", width=250, height=35)
yeni_url_kutusu.pack(pady=10)

def yeni_tarama():
    yeni_url = yeni_url_kutusu.get()
    
    sonuc_ekrani.pack_forget()
    arama_ekrani.pack(fill="both", expand=True)
    
    url_kutusu.delete(0, "end")
    url_kutusu.insert(0, yeni_url)
    yeni_url_kutusu.delete(0, "end") 
    
    taramayi_baslat()


def raporu_html_kaydet():
    dosya_yolu = filedialog.asksaveasfilename(
        defaultextension=".html",
        filetypes=[("HTML Dosyası", "*.html")],
        title="Raporu Kaydet"
    )
    
    if not dosya_yolu:
        return

    hedef = sonuc_baslik.cget("text")
    ping = ping_etiketi.cget("text")
    h1 = kutu_h1.get("0.0", "end")
    h2 = kutu_h2.get("0.0", "end")
    liste = kutu_liste.get("0.0", "end")
    linkler = kutu_link.get("0.0", "end")
    resimler = kutu_resim.get("0.0", "end")

    html_icerik = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background-color: #f0f2f5; padding: 30px; }}
            .card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 900px; margin: auto; }}
            h1 {{ color: #1e3a8a; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }}
            h2 {{ color: #1e40af; margin-top: 30px; background: #eff6ff; padding: 8px; border-radius: 5px; }}
            pre {{ background: #1e293b; color: #f8fafc; padding: 15px; border-radius: 8px; overflow-x: auto; white-space: pre-wrap; font-family: 'Consolas', monospace; }}
            .meta {{ color: #64748b; font-weight: bold; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Web Scraper Tarama Raporu</h1>
            <p class="meta">{hedef} | {ping}</p>
            <h2>H1 Başlıkları</h2> <pre>{h1}</pre>
            <h2>H2 Başlıkları</h2> <pre>{h2}</pre>
            <h2>Listeler</h2> <pre>{liste}</pre>
            <h2>Bağlantılar</h2> <pre>{linkler}</pre>
            <h2>Resimler</h2> <pre>{resimler}</pre>
        </div>
    </body>
    </html>
    """

    try:
        with open(dosya_yolu, "w", encoding="utf-8") as dosya:
            dosya.write(html_icerik)
        messagebox.showinfo("Başarılı", "Rapor başarıyla kaydedildi!")
    except Exception as e:
        messagebox.showerror("Hata", f"Kaydedilemedi: {e}")

yeni_tara_butonu = ctk.CTkButton(icerik_frame, text="Geçiş Yap", command=yeni_tarama, font=("Segoe UI", 13, "bold"), width=120, height=35)
yeni_tara_butonu.pack(pady=10)

kayit_butonu = ctk.CTkButton(
    icerik_frame, 
    text="Kayıt Dosyası Oluştur", 
    command=raporu_html_kaydet, 
    font=("Segoe UI", 13, "bold"), 
    width=180, 
    height=35, 
    fg_color="#1c00bb", 
    hover_color="#1c00bb"
)
kayit_butonu.pack(pady=30)


pencere.mainloop()