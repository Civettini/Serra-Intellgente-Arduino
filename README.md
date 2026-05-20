# Greenhouse Manager

Sistema automatico per il monitoraggio e controllo di una serra, con allarmi locali, notifiche remote via Telegram e integrazione meteo.

---

## File disponibili

| File | Scopo | Uso |
|------|-------|-----|
| serra_demo_generale.py | Template con API e bot da configurare | Uso personale, produzione, deploy reale |
| Arduino.py | Script Python per connessione diretta ad Arduino fisico | Lettura dati reali da sensori, controllo LED, invio Telegram |

---

## Avvio rapido

### 1. Uso personale (serra_demo_generale.py)

```bash
pip install requests
```

Modifica le righe 15-17 con i tuoi dati:
```python
OPENWEATHER_API_KEY = "LA_TUA_API_KEY_QUI"
TELEGRAM_BOT_TOKEN    = "IL_TUO_TOKEN_BOT_QUI"
TELEGRAM_CHAT_ID      = "IL_TUO_CHAT_ID_QUI"
```

Poi avvia:
```bash
python serra_demo_generale.py
```

### 2. Arduino fisico (Arduino.py)

Collega Arduino al PC via USB, carica lo sketch greenhouse_manager.ino, poi:

```bash
pip install pyserial requests
python Arduino.py
```

Funzionalita:
- Lettura dati reali da Arduino (temperatura, umidita, luce)
- Scelta interattiva della pianta e della citta
- Analisi allarmi con soglie personalizzate per pianta
- Invio notifiche Telegram in tempo reale
- Integrazione meteo OpenWeatherMap

---

## Ottenere le credenziali

### OpenWeatherMap API
1. Registrati su openweathermap.org
2. Vai su My API Keys
3. Copia la key gratuita

### Telegram Bot
1. Cerca @BotFather su Telegram
2. Invia /newbot e segui le istruzioni
3. Copia il token fornito

### Telegram Chat ID
1. Cerca @userinfobot su Telegram
2. Invia /start
3. Copia il tuo ID numerico

---

## Comandi durante l'esecuzione

```
[N] Normale         Torna a fluttuazione naturale (solo demo)
[T] Allarme Temp    Simula temperatura troppo alta (solo demo)
[U] Allarme Umid    Simula umidita fuori range (solo demo)
[L] Allarme Luce    Simula luce insufficiente (solo demo)
[M] Meteo           Aggiorna dati meteo e controlla previsioni
[S] Stato           Richiede stato completo Arduino
[Q] Esci            Arresta il sistema
```

---

## Requisiti

- Python 3.8+
- Librerie: requests, pyserial (solo per Arduino.py)
- Connessione internet (per API meteo e Telegram)

```bash
pip install requests pyserial
```

---

## Autori

- Civettini Damiano
- Salagor Adrian

Anno Accademico 2025/2026
