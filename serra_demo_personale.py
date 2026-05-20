import time
import random
import threading
import requests
from queue import Queue
from datetime import datetime


# CONFIGURAZIONE


OPENWEATHER_API_KEY = "LA TUA OPENWEATHER API KEY"      # openweathermap.org
TELEGRAM_BOT_TOKEN = "TELEGRAM BOT TOKEN"      # @BotFather
TELEGRAM_CHAT_ID = "TELEGRAM CHAT ID"

# DATABASE PIANTE


PIANTE = {
    1: {
        "nome": "🍅 Pomodoro",
        "temp_max": 28.0,
        "umid_min": 60.0,
        "umid_max": 80.0,
        "luce_min": 400,
        "desc": "Amante del sole, molta luce e umidità moderata-alta"
    },
    2: {
        "nome": "🥬 Lattuga",
        "temp_max": 22.0,
        "umid_min": 50.0,
        "umid_max": 70.0,
        "luce_min": 200,
        "desc": "Temperature fresche, ombra parziale"
    },
    3: {
        "nome": "🌿 Basilico",
        "temp_max": 25.0,
        "umid_min": 40.0,
        "umid_max": 60.0,
        "luce_min": 350,
        "desc": "Aroma mediterraneo, caldo e luce diretta"
    },
    4: {
        "nome": "🌶️ Peperoncino",
        "temp_max": 30.0,
        "umid_min": 50.0,
        "umid_max": 70.0,
        "luce_min": 450,
        "desc": "Caldo intenso e molta luce"
    },
    5: {
        "nome": "🍓 Fragola",
        "temp_max": 24.0,
        "umid_min": 60.0,
        "umid_max": 75.0,
        "luce_min": 300,
        "desc": "Umidità costante e luce diffusa"
    },
}


# FAKE ARDUINO - Simulazione pura Python


class FakeArduino:

    
    def __init__(self, baudrate=9600, timeout=5):
        self.baudrate = baudrate
        self.timeout = timeout
        self.is_open = True
        self.out_buffer = Queue()   # Dati verso PC
        self.in_buffer = Queue()    # Comandi dal PC
        
        # Soglie (ricevute da PC)
        self.temp_max = 30.0
        self.umid_min = 40.0
        self.umid_max = 70.0
        self.luce_min = 300
        
        # Sensori
        self.temp = 24.0
        self.umid = 65.0
        self.luce = 500
        
        # LED
        self.LED_temp = False
        self.LED_luce = False
        self.LED_umid = False
        
        # Forzatura allarme (per demo)
        self.forza = None
        
        self.running = True
        self.thread = threading.Thread(target=self._loop)
        self.thread.daemon = True
        self.thread.start()
        
        # Messaggio iniziale
        self.out_buffer.put(b"ARDUINO_READY\n")
    
    def _loop(self):

        while self.running:
            # Applica forzatura se richiesta
            if self.forza == "temp":
                self.temp = self.temp_max + random.uniform(3, 6)
            elif self.forza == "umid":
                self.umid = self.umid_max + random.uniform(5, 10)
            elif self.forza == "luce":
                self.luce = random.randint(50, 150)
            elif self.forza == "normale":
                self.forza = None
            else:
                # Fluttuazione naturale
                self.temp += random.gauss(0, 0.3)
                self.umid += random.gauss(0, 1.5)
                self.luce = max(0, min(1023, self.luce + random.randint(-40, 40)))
            
            # Limita valori realistici
            self.temp = max(10, min(45, self.temp))
            self.umid = max(10, min(95, self.umid))
            
            # Controlla allarmi (logica Arduino)
            self._check_alarms()
            
            # Invia dati
            dati = f"{self.temp:.1f}|{self.umid:.1f}|{self.luce}\n"
            self.out_buffer.put(dati.encode('utf-8'))
            
            time.sleep(5)
    
    def _check_alarms(self):
        """Simula la logica LED di Arduino"""
        # LED 1 - Temperatura
        if self.temp > self.temp_max:
            if not self.LED_temp:
                self.LED_temp = True
                print("     [LED 1] ATTIVO - Temperatura alta!")
        else:
            if self.LED_temp:
                self.LED_temp = False
                print("     [LED 1] Spento")
        
        # LED 2 - Luce
        if self.luce < self.luce_min:
            if not self.LED_luce:
                self.LED_luce = True
                print("     [LED 2] ATTIVO - Luce bassa!")
        else:
            if self.LED_luce:
                self.LED_luce = False
                print("     [LED 2] Spento")
        
        # LED 3 - Umidità
        if self.umid < self.umid_min or self.umid > self.umid_max:
            if not self.LED_umid:
                self.LED_umid = True
                print("     [LED 3] ATTIVO - Umidità fuori range!")
        else:
            if self.LED_umid:
                self.LED_umid = False
                print("     [LED 3] Spento")
    
    def forza_allarme(self, tipo):
        """Forza un allarme per la demo"""
        self.forza = tipo
        print(f"   ⚡ Forzatura: {tipo}")
    
    # Metodi compatibili pyserial
    def readline(self):
        try:
            return self.out_buffer.get(timeout=self.timeout)
        except:
            return b''
    
    def write(self, data):
        self.in_buffer.put(data)
        self._process_cmd(data.decode('utf-8', errors='ignore').strip())
        return len(data)
    
    def _process_cmd(self, cmd):
        if cmd.startswith("CONFIG|"):
            p = cmd.split("|")
            self.temp_max, self.umid_min = float(p[1]), float(p[2])
            self.umid_max, self.luce_min = float(p[3]), int(p[4])
            self.out_buffer.put(f"CONFIG_OK|{p[1]}|{p[2]}|{p[3]}|{p[4]}\n".encode())
            
        elif cmd == "ALARM_OFF":
            print("     [PC] Allarmi esterni spenti")
        elif cmd == "FORECAST_RAIN":
            print("   🌧️  [LED 3] Pattern: pioggia prevista")
        elif cmd == "FORECAST_BAD":
            print("   ⛈️  [LED 3] Pattern: meteo avverso")
        elif cmd == "STATUS":
            st = f"STATUS|{self.temp:.1f}|{self.umid:.1f}|{self.luce}|{int(self.LED_temp)}|{int(self.LED_luce)}|{int(self.LED_umid)}\n"
            self.out_buffer.put(st.encode())
    
    @property
    def in_waiting(self):
        return self.out_buffer.qsize()
    
    def close(self):
        self.running = False
        self.thread.join(timeout=1)


# TELEGRAM


def telegram_invia(testo):
    if TELEGRAM_BOT_TOKEN == "IL_TUO_TOKEN_BOT_QUI":
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": testo, "parse_mode": "HTML"}, timeout=10)
        return r.status_code == 200
    except:
        return False


# METEO


def meteo_coords(citta):
    try:
        r = requests.get("http://api.openweathermap.org/geo/1.0/direct",
            params={"q": citta, "limit": 1, "appid": OPENWEATHER_API_KEY}, timeout=10)
        d = r.json()[0]
        return {"nome": d["name"], "lat": d["lat"], "lon": d["lon"]}
    except:
        return None

def meteo_attuale(lat, lon):
    try:
        r = requests.get("https://api.openweathermap.org/data/2.5/weather",
            params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric", "lang": "it"}, timeout=10)
        d = r.json()
        return {"temp": d["main"]["temp"], "umid": d["main"]["humidity"], "desc": d["weather"][0]["description"]}
    except:
        return None

def meteo_previsioni(lat, lon):
    try:
        r = requests.get("https://api.openweathermap.org/data/2.5/forecast",
            params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric", "lang": "it"}, timeout=10)
        d = r.json()
        prossime = d["list"][:8]
        pioggia = any(200 <= f["weather"][0]["id"] < 600 for f in prossime)
        brutto = any(f["weather"][0]["id"] < 800 for f in prossime)
        return {"pioggia": pioggia, "brutto": brutto}
    except:
        return None


# UI


def clear():
    print("\n" * 3)

def banner(titolo):
    print("╔" + "═" * 58 + "╗")
    print("║" + titolo.center(58) + "║")
    print("╚" + "═" * 58 + "╝")

def dashboard(serra, pianta, citta, meteo, allarmi):
    clear()
    banner(" 🌿 SERRA SMART - DASHBOARD ")
    print(f"\n  🌱 Pianta: {pianta['nome']}")
    print(f"  🌍 Città:  {citta['nome'] if citta else 'N/D'}")
    if meteo:
        print(f"  🌤️  Esterno: {meteo['temp']:.1f}°C, {meteo['umid']}%, {meteo['desc']}")
    print("─" * 60)
    print(f"  🌡️  Temperatura:  {serra.temp:.1f}°C    (max: {serra.temp_max}°C)")
    print(f"  💧 Umidità:       {serra.umid:.1f}%     (range: {serra.umid_min}-{serra.umid_max}%)")
    print(f"  ☀️  Luce:          {serra.luce}      (min: {serra.luce_min})")
    print("─" * 60)
    print(f"    LED:  [1:{'ON ' if serra.LED_temp else 'off'}]  [2:{'ON ' if serra.LED_luce else 'off'}]  [3:{'ON ' if serra.LED_umid else 'off'}]")
    print("─" * 60)
    if allarmi:
        print("  🚨 ALLARMI:")
        for a in allarmi:
            print(f"     • {a}")
    else:
        print("  ✅ Nessun allarme attivo")
    print("═" * 60)

def menu_demo():
    print("\n  [N] Normale  [T] Allarme Temp  [U] Allarme Umid  [L] Allarme Luce")
    print("  [M] Meteo    [S] Stato         [Q] Esci")

# MAIN


def main():
    banner(" 🌿 GREENHOUSE MANAGER v3 - DEMO ")
    
    # Verifica config
    if OPENWEATHER_API_KEY == "LA_TUA_API_KEY_QUI":
        print("\n⚠️  Inserisci OPENWEATHER_API_KEY nel codice!")
    if TELEGRAM_BOT_TOKEN == "IL_TUO_TOKEN_BOT_QUI":
        print("\n⚠️  Telegram non configurato (opzionale)")
    else:
        telegram_invia("🌿 <b>Serra Manager</b> avviato!")
        print("\n📱 Notifica Telegram inviata!")
    
    # Selezione pianta
    print("\nScegli la pianta:")
    for k, v in PIANTE.items():
        print(f"  [{k}] {v['nome']}")
    pianta = PIANTE[int(input("\n👉 "))]
    
    # Città
    citta_nome = input("\nCittà meteo: ").strip() or "Brescia"
    citta = meteo_coords(citta_nome)
    if citta:
        print(f"✅ Trovata: {citta['nome']}")
    else:
        print("⚠️  Città non trovata, uso Brescia default")
        citta = {"nome": "Brescia", "lat": 45.54, "lon": 10.21}
    
    # Avvia Fake Arduino
    print("\n🔧 Avvio Fake Arduino...")
    arduino = FakeArduino()
    time.sleep(1)
    
    # Invia config pianta
    config = f"CONFIG|{pianta['temp_max']}|{pianta['umid_min']}|{pianta['umid_max']}|{pianta['luce_min']}"
    arduino.write(config.encode())
    time.sleep(0.5)
    
    # Leggi conferma
    while arduino.in_waiting:
        print(f"   {arduino.readline().decode().strip()}")
    
    # Meteo iniziale
    meteo = meteo_attuale(citta['lat'], citta['lon'])
    
    # Notifica avvio
    msg = f"✅ <b>Serra avviata</b>\n🌱 {pianta['nome']}\n🌍 {citta['nome']}"
    telegram_invia(msg)
    
    print(f"\n{'═'*60}")
    print("   🚀 SISTEMA PRONTO!")
    print("   Controlla il tuo telefono per le notifiche")
    print(f"{'═'*60}")
    
    ciclo = 0
    modo = "N"
    allarmi = []
    
    try:
        while True:
            # Leggi dati da Arduino
            dati = None
            while arduino.in_waiting:
                line = arduino.readline().decode().strip()
                if line.startswith("CONFIG_OK") or line.startswith("STATUS"):
                    continue
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) == 3:
                        dati = {"temp": float(parts[0]), "umid": float(parts[1]), "luce": int(parts[2])}
            
            # Analisi allarmi
            allarmi = []
            if dati:
                if dati["temp"] > pianta["temp_max"]:
                    allarmi.append(f"🔥 Temperatura {dati['temp']}°C > {pianta['temp_max']}°C")
                if dati["umid"] < pianta["umid_min"] or dati["umid"] > pianta["umid_max"]:
                    allarmi.append(f"💧 Umidità {dati['umid']}% fuori range")
                if dati["luce"] < pianta["luce_min"]:
                    allarmi.append(f"🌑 Luce {dati['luce']} < {pianta['luce_min']}")
            
            # Mostra dashboard
            dashboard(arduino, pianta, citta, meteo, allarmi)
            
            # Menu ogni 2 cicli
            if ciclo % 2 == 0:
                menu_demo()
                modo = input("👉 ").strip().upper() or "N"
                
                if modo == "Q":
                    break
                elif modo == "T":
                    arduino.forza_allarme("temp")
                elif modo == "U":
                    arduino.forza_allarme("umid")
                elif modo == "L":
                    arduino.forza_allarme("luce")
                elif modo == "N":
                    arduino.forza_allarme("normale")
                elif modo == "M":
                    meteo = meteo_attuale(citta['lat'], citta['lon'])
                    prev = meteo_previsioni(citta['lat'], citta['lon'])
                    if prev:
                        if prev["pioggia"]:
                            arduino.write(b"FORECAST_RAIN\n")
                            telegram_invia(f"🌧️ <b>Previsione pioggia</b> a {citta['nome']}!")
                        elif prev["brutto"]:
                            arduino.write(b"FORECAST_BAD\n")
                        else:
                            arduino.write(b"ALARM_OFF\n")
                    print(f"   🔄 Meteo aggiornato!")
                elif modo == "S":
                    arduino.write(b"STATUS\n")
            
            # Invia allarmi Telegram (solo se nuovi)
            if allarmi and modo in "TUL":
                testo = "🚨 <b>ALLARME SERRA</b>\n\n"
                for a in allarmi:
                    testo += f"• {a}\n"
                testo += f"\n🌱 {pianta['nome']}\n⏰ {datetime.now().strftime('%H:%M:%S')}"
                telegram_invia(testo)
                print("   📱 Notifica inviata!")
            
            ciclo += 1
            time.sleep(2)
    
    except KeyboardInterrupt:
        pass
    
    print("\n🛑 Arresto...")
    arduino.write(b"ALARM_OFF\n")
    arduino.close()
    telegram_invia("🛑 <b>Serra</b> arrestata")
    print("✅ Demo terminata!")

if __name__ == "__main__":
    main()