import serial
import time
import requests
import json
from datetime import datetime




# Porta seriale Arduino
SERIAL_PORT = "COM3"
SERIAL_BAUD = 9600

# Telegram Bot
TELEGRAM_TOKEN = "INSERISCI_QUI_IL_TUO_TOKEN"
TELEGRAM_CHAT_ID = "INSERISCI_QUI_IL_TUO_CHAT_ID"
OWM_API_KEY = "INSERISCI_QUI_LA_TUA_API_KEY"


# DATABASE PIANTE


PIANTE = {
    1: {
        "nome": "🍅 Pomodoro",
        "temp_min": 18, "temp_max": 27,
        "hum_min": 60, "hum_max": 80,
        "light_min": 500,
        "desc": "Amante del sole, molta luce e umidità moderata-alta"
    },
    2: {
        "nome": "🥬 Lattuga",
        "temp_min": 15, "temp_max": 22,
        "hum_min": 50, "hum_max": 70,
        "light_min": 300,
        "desc": "Temperature fresche, ombra parziale"
    },
    3: {
        "nome": "🌿 Basilico",
        "temp_min": 20, "temp_max": 30,
        "hum_min": 50, "hum_max": 70,
        "light_min": 600,
        "desc": "Aroma mediterraneo, caldo e luce diretta"
    },
    4: {
        "nome": "🌶️ Peperoncino",
        "temp_min": 22, "temp_max": 30,
        "hum_min": 60, "hum_max": 75,
        "light_min": 700,
        "desc": "Caldo intenso e molta luce"
    },
    5: {
        "nome": "🍓 Fragola",
        "temp_min": 18, "temp_max": 25,
        "hum_min": 65, "hum_max": 80,
        "light_min": 400,
        "desc": "Umidità costante e luce diffusa"
    },
}


# SCELTA UTENTE


def scegli_pianta():
    print("\n🌱 Scegli la pianta:")
    for k, v in PIANTE.items():
        print(f"  [{k}] {v['nome']}")
        print(f"      T:{v['temp_min']}-{v['temp_max']}°C | 💧{v['hum_min']}-{v['hum_max']}% | ☀️>{v['light_min']}")
        print(f"      {v['desc']}")
        print()
    
    while True:
            scelta = int(input("👉 Inserisci numero (1-5): "))
            

def scegli_citta():
    citta = input("\n🌍 Inserisci città per il meteo (es. Milano, Roma, Brescia): ").strip()
    return citta


# FUNZIONI SERIALE


def leggi_dati_arduino(ser):
    try:
        linea = ser.readline().decode('utf-8').strip()
        if not linea or not linea.startswith("DATA,"):
            return None
        
        parti = linea.split(',')
        if len(parti) != 8:
            return None
        
        return {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "temperatura": float(parti[1]),
            "umidita": float(parti[2]),
            "luce": int(parti[3]),
            "allarme_temp": parti[4] == "1",
            "allarme_hum": parti[5] == "1",
            "allarme_light": parti[6] == "1",
        }
    except Exception as e:
        print(f"Errore lettura: {e}")
        return None


# FUNZIONI ANALISI


def analizza_dati(dati, pianta):
    alert = []
    
    # Temperatura
    if dati["temperatura"] < pianta["temp_min"]:
        alert.append(f"🌡️ Temperatura troppo BASSA: {dati['temperatura']}°C (min: {pianta['temp_min']}°C)")
    elif dati["temperatura"] > pianta["temp_max"]:
        alert.append(f"🌡️ Temperatura troppo ALTA: {dati['temperatura']}°C (max: {pianta['temp_max']}°C)")
    
    # Umidità
    if dati["umidita"] < pianta["hum_min"]:
        alert.append(f"💧 Umidità troppo BASSA: {dati['umidita']}% (min: {pianta['hum_min']}%)")
    elif dati["umidita"] > pianta["hum_max"]:
        alert.append(f"💧 Umidità troppo ALTA: {dati['umidita']}% (max: {pianta['hum_max']}%)")
    
    # Luce
    if dati["luce"] < pianta["light_min"]:
        alert.append(f"☀️ Luce INSUFFICIENTE: {dati['luce']} (min: {pianta['light_min']})")
    
    return alert

# FUNZIONI METEO


def prendi_meteo(citta):
    """Ottiene previsioni meteo da OpenWeatherMap"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={citta}&appid={OWM_API_KEY}&units=metric&lang=it"
        r = requests.get(url, timeout=5)
        dati = r.json()
        
        return {
            "temp_esterna": dati["main"]["temp"],
            "umidita_esterna": dati["main"]["humidity"],
            "descrizione": dati["weather"][0]["description"],
            "vento": dati["wind"]["speed"],
        }
    except Exception as e:
        print(f"Errore meteo: {e}")
        return None

# FUNZIONI TELEGRAM


def invia_telegram(messaggio):

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": messaggio,
            "parse_mode": "HTML"
        }
        r = requests.post(url, json=payload, timeout=5)
        return r.status_code == 200
    except Exception as e:
        print(f"Errore Telegram: {e}")
        return False


# MAIN

def main():
    print("=" * 50)
    print("🌿 GREENHOUSE MANAGER - Python")
    print("=" * 50)
    
    # SCELTA PIANTA
    pianta = scegli_pianta()
    print(f"\n✅ Pianta selezionata: {pianta['nome']}")
    
    # SCELTA CITTÀ
    citta = scegli_citta()
    print(f"✅ Città meteo: {citta}")
    
    # Connessione Arduino
    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
    time.sleep(2)
    print("✅ Arduino connesso")

    
    # Storico allarmi
    ultimo_allarme = None
    
    while True:
        dati = leggi_dati_arduino(ser)
        if not dati:
            time.sleep(0.1)
            continue
        
        # Stampa dati
        print(f"\n[{dati['timestamp']}] "
              f"T:{dati['temperatura']:.1f}°C "
              f"H:{dati['umidita']:.1f}% "
              f"L:{dati['luce']} "
              f"| LED:{int(dati['allarme_temp'])}{int(dati['allarme_hum'])}{int(dati['allarme_light'])}")
        
        # Analizza
        alert = analizza_dati(dati, pianta)
        
        if alert:
            msg = f"⚠️ <b>ALLARME SERRA</b>\n"
            msg += f"🌱 Pianta: <b>{pianta['nome']}</b>\n"
            msg += f"📍 {citta} | {dati['timestamp']}\n\n"
            msg += "\n".join(alert)
            msg += f"\n\n📊 Dati attuali:\n"
            msg += f"• Temperatura: {dati['temperatura']:.1f}°C\n"
            msg += f"• Umidità: {dati['umidita']:.1f}%\n"
            msg += f"• Luce: {dati['luce']}"
            
            # Meteo
            meteo = prendi_meteo(citta)
            if meteo:
                msg += f"\n\n🌤️ Meteo esterno:\n"
                msg += f"• {meteo['descrizione']}\n"
                msg += f"• {meteo['temp_esterna']:.1f}°C | 💧{meteo['umidita_esterna']}%"
            
            # Invia Telegram
            allarme_key = "|".join(alert)
            if allarme_key != ultimo_allarme:
                print(f"🔔 Invio Telegram...")
                if invia_telegram(msg):
                    print("✅ Notifica inviata!")
                    ultimo_allarme = allarme_key
                else:
                    print("❌ Errore invio")
            else:
                print("⏳ Allarme già notificato")
        else:
            print("✅ Tutto nella norma")
            ultimo_allarme = None
        
        time.sleep(1)

if __name__ == "__main__":
    main()