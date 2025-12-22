import streamlit as st
import psutil
import requests
import time
import pandas as pd
import os
from datetime import datetime  

# ==============================================================================
# 1. CONFIGURATION & SECRETS
# ==============================================================================
# Pourquoi ? On sécurise les accès et on définit les règles du jeu.

st.set_page_config(page_title="Sentinel", page_icon="🛡️", layout="wide")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Seuils d'alerte (Tu peux les baisser à 10% pour tester l'envoi)
CPU_LIMIT = 80
RAM_LIMIT = 85

# On utilise le "State" de Streamlit pour se souvenir des choses entre deux rafraîchissements
if 'last_alert_time' not in st.session_state:
    st.session_state['last_alert_time'] = 0

# ==============================================================================
# 2. FONCTIONS (La Logique)
# ==============================================================================

def get_timestamp():
    """Retourne l'heure actuelle formatée (ex: 18/12/2025 20:30:05)"""
    # VOICI L'USAGE DE DATETIME : Avoir des logs humains
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def send_telegram_alert(message):
    """Envoie le message à ton téléphone via l'API Telegram."""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        st.warning("⚠️ Configuration Telegram manquante dans le .env")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    # On ajoute l'heure précise dans le message
    timestamp = get_timestamp()
    clean_message = f"🚨 **ALERTE SENTINEL** [{timestamp}] 🚨\n\n{message}"
    
    payload = {"chat_id": CHAT_ID, "text": clean_message}
    
    try:
        # Streamlit utilise le proxy du système automatiquement s'il est défini
        requests.post(url, json=payload, timeout=5)
        # On affiche une notification visuelle sur le dashboard aussi
        st.toast(f"Alerte envoyée à {timestamp} !", icon="📨")
    except Exception as e:
        st.error(f"Erreur envoi Telegram: {e}")

def monitor_system(cpu, ram):
    """Le cerveau : décide si on doit crier ou pas."""
    current_time = time.time()
    
    # Anti-spam : On attend au moins 300 secondes (5 min) entre deux alertes
    if current_time - st.session_state['last_alert_time'] > 300:
        alert_msg = ""
        if cpu > CPU_LIMIT:
            alert_msg += f"🔥 CPU en surchauffe : {cpu}%\n"
        if ram > RAM_LIMIT:
            alert_msg += f"🧠 RAM saturée : {ram}%\n"
        
        if alert_msg:
            send_telegram_alert(alert_msg)
            st.session_state['last_alert_time'] = current_time

# ==============================================================================
# 3. INTERFACE VISUELLE (Le Frontend)
# ==============================================================================

st.title("🛡️ Sentinel - Server Monitor")
st.markdown(f"*Dernière mise à jour : {get_timestamp()}*")

# --- A. Collecte des données ---
# psutil lit les infos du noyau Linux du conteneur (qui sont celles de l'hôte LXC)
cpu_usage = psutil.cpu_percent(interval=1) # Bloque 1 seconde pour mesurer
ram_info = psutil.virtual_memory()
disk_info = psutil.disk_usage('/')

# --- B. Vérification Alertes ---
monitor_system(cpu_usage, ram_info.percent)

# --- C. Affichage des KPIs (Gros chiffres) ---
col1, col2, col3 = st.columns(3)
col1.metric("CPU", f"{cpu_usage}%", delta_color="inverse")
col2.metric("RAM", f"{ram_info.percent}%", f"Libre: {ram_info.available // (1024**3)} GB")
col3.metric("Disque", f"{disk_info.percent}%", f"Libre: {disk_info.free // (1024**3)} GB")

# --- D. Graphique Temps Réel ---
st.subheader("Historique CPU (Session)")

if 'cpu_history' not in st.session_state:
    st.session_state.cpu_history = []

st.session_state.cpu_history.append(cpu_usage)
# On garde les 60 derniers points (environ 2 minutes d'historique)
if len(st.session_state.cpu_history) > 60:
    st.session_state.cpu_history.pop(0)

# Création du graphique simple
st.line_chart(st.session_state.cpu_history)

# --- E. Table des Processus ---
st.subheader("Top 5 Processus Gourmands")
processes = []
# On parcourt les processus actifs
for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
    try:
        processes.append(proc.info)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

# Pandas permet de trier ça en une ligne
df_proc = pd.DataFrame(processes)
if not df_proc.empty:
    df_proc = df_proc.sort_values(by='cpu_percent', ascending=False).head(5)
    st.dataframe(df_proc, use_container_width=True)

# ==============================================================================
# 4. BOUCLE INFINIE (Refresh)
# ==============================================================================
# C'est l'astuce Streamlit : on attend 2s et on recharge toute la page.
time.sleep(2)
st.rerun()