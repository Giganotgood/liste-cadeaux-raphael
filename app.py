import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import base64

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Mon Catalogue", page_icon="📦", layout="wide")

# CSS global pour les images et pour nettoyer la sidebar
st.markdown("""
<style>
    img { object-fit: cover !important; border-radius: 8px; }
    
    /* Masquer la barre de défilement moche de la sidebar */
    [data-testid="stSidebarUserContent"] {
        scrollbar-width: none;
        -ms-overflow-style: none;
    }
    [data-testid="stSidebarUserContent"]::-webkit-scrollbar {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# --- FONCTIONS UTILITAIRES ---
def get_image_base64(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            mime = "image/png" if path.lower().endswith('.png') else "image/jpeg"
            return f"data:{mime};base64,{b64}"
    except:
        return ""

def build_carousel(image_paths):
    html = """
    <style>
    .gallery-container { width: 100%; overflow: hidden; border-radius: 8px; margin-bottom: 15px; }
    .gallery-scroll { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; scroll-behavior: smooth; }
    .gallery-scroll::-webkit-scrollbar { height: 6px; }
    .gallery-scroll::-webkit-scrollbar-track { background: transparent; }
    .gallery-scroll::-webkit-scrollbar-thumb { background-color: rgba(150, 150, 150, 0.5); border-radius: 10px; }
    .gallery-item { scroll-snap-align: center; flex: 0 0 100%; width: 100%; }
    .gallery-item img { width: 100%; height: 250px; object-fit: cover; display: block; }
    </style>
    <div class="gallery-container"><div class="gallery-scroll">
    """
    for p in image_paths:
        b64 = get_image_base64(p)
        if b64:
            html += f'<div class="gallery-item"><img src="{b64}"></div>'
    html += "</div></div>"
    return html

@st.cache_data(show_spinner=False, ttl=86400)
def fetch_image_online(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            og = soup.find('meta', property='og:image')
            if og and og.get('content'): return og.get('content')
            img = soup.find('img')
            if img and img.get('src') and len(img.get('src')) > 20: return img.get('src')
    except:
        pass
    return "https://via.placeholder.com/300x250?text=Image+Manquante"

# --- CONSTRUCTION DU SITE ---
try:
    df = pd.read_excel("Treck stuff.xlsx", header=0)
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    for col in ['lien', 'nom', 'prix', 'image', 'catégorie', 'sous-catégorie', 'favori']:
        if col not in df.columns:
            df[col] = ""

    df['catégorie'] = df['catégorie'].fillna('Non classé')
    df['sous-catégorie'] = df['sous-catégorie'].fillna('Général')

    # --- MENU LATÉRAL (SIDEBAR) ---
    st.sidebar.title("Navigation")
    liste_categories = df['catégorie'].unique().tolist()
    page_actuelle = st.sidebar.radio("Choisissez une catégorie :", liste_categories)

    st.sidebar.divider()
    for i in range(1, 4):
        chemin_sidebar = f"images/contexte/sidebar-{i}.jpg"
        if os.path.exists(chemin_sidebar):
            st.sidebar.image(chemin_sidebar, use_container_width=True)

    # --- EN-TÊTE DE LA PAGE PRINCIPALE ---
    st.title(f"Catégorie : {page_actuelle}")
    
    if page_actuelle.lower() == "trek":
        chemin_banniere = "images/contexte/banniere.jpg"
        if os.path.exists(chemin_banniere):
            b64_banniere = get_image_base64(chemin_banniere)
            if b64_banniere:
                st.markdown(f'<img src="{b64_banniere}" style="width:100%; max-height:450px; object-fit:cover; object-position:center; margin-bottom:20px;">', unsafe_allow_html=True)
        
        st.markdown("### Inspiration & Moodboard")
        
        col_vide1, col_vibe
