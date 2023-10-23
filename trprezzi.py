import requests
from bs4 import BeautifulSoup
import sqlite3
import smtplib
from email.mime.text import MIMEText
import schedule
import time

# URL del prodotto su Trovaprezzi
url = "URL_DEL_PRODOTTO"

# Funzione per estrarre il prezzo dalla pagina
def estrai_prezzo(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    prezzo = soup.find("span", class_="price").text
    return prezzo

# Funzione per controllare il prezzo e inviare notifiche
def controllo_prezzo():
    # Connessione al database per memorizzare i dati
    conn = sqlite3.connect("prezzi.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS prezzi (
                  data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  prezzo REAL)''')

    # Estrarre il prezzo e memorizzarlo nel database
    prezzo_corrente = estrai_prezzo(url)
    cursor.execute("INSERT INTO prezzi (prezzo) VALUES (?)", (prezzo_corrente,))
    conn.commit()

    # Controlla se il prezzo attuale è diverso dall'ultimo prezzo registrato
    cursor.execute("SELECT prezzo FROM prezzi ORDER BY data DESC LIMIT 2")
    ultimi_prezzi = cursor.fetchall()
    if len(ultimi_prezzi) == 2 and ultimi_prezzi[0][0] != ultimi_prezzi[1][0]:
        # Invia una notifica via email
        messaggio = "Il prezzo del prodotto è cambiato da {} a {}".format(ultimi_prezzi[1][0], ultimi_prezzi[0][0])
        destinatario = "TUA_EMAIL"
        mittente = "TUA_EMAIL"
        password = "TUA_PASSWORD"

        msg = MIMEText(messaggio)
        msg["Subject"] = "Variazione di prezzo"
        msg["From"] = mittente
        msg["To"] = destinatario

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(mittente, password)
        server.sendmail(mittente, destinatario, msg.as_string())
        server.quit()

    # Chiudi la connessione al database
    conn.close()

# Pianifica il controllo del prezzo ogni 10 minuti
schedule.every(10).minutes.do(controllo_prezzo)

# Ciclo principale per eseguire il controllo in background
while True:
    schedule.run_pending()
    time.sleep(1)
