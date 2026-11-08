import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import base64

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Mon Catalogue", page_icon="📦", layout="wide", initial_sidebar_state="collapsed")

# --- CSS MAGIQUE ---
st.markdown("""
<style>
    /* 1. Style des images global */
    img { object-fit: cover !important; border-radius: 8px; }
    
    /* 2. Suppression de la sidebar native et de l'en-tête de base */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    header { visibility: hidden; }
    
    /* 3. Remonter le contenu tout en haut */
    div.block-container {
        padding-top: 0rem !important;
    }
    
    /* 4. Figer le premier élément (notre menu horizontal) en haut de la page */
    div.block-container > div:first-child > div:first-child {
        position: sticky;
        top: 0;
        z-index: 999;
        background-color: var(--background-color); /* S'adapte au mode sombre ou clair */
        padding-top: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(150, 150, 150, 0.2);
        margin-bottom: 1rem;
    }
    
    /* Style pour centrer un peu plus les choix du menu */
    .stRadio > div {
        justify-content: center;
        gap: 30px;
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

    # --- MENU DE NAVIGATION FIGÉ EN HAUT ---
    liste_categories = df['catégorie'].unique().tolist()
    # Le label_visibility="collapsed" permet de ne pas afficher le mot "Navigation", on garde juste les boutons
    page_actuelle = st.radio("Navigation", liste_categories, horizontal=True, label_visibility="collapsed")

    # --- LAYOUT DYNAMIQUE (LE NOUVEAU "SIDEBAR" QUI DÉFILE) ---
    col_gauche, col_droite = st.columns([1, 4]) # 1/5ème pour les montagnes, 4/5ème pour le catalogue

    with col_gauche:
        # On empile les images d'ambiance ici. Elles défileront naturellement.
        for i in range(1, 4):
            chemin_sidebar = f"images/contexte/sidebar-{i}.jpg"
            if os.path.exists(chemin_sidebar):
                st.image(chemin_sidebar, use_container_width=True)

    with col_droite:
        st.title(f"{page_actuelle}")
        
        # --- SECTION TREK (Bannière et Moodboard) ---
        if page_actuelle.lower() == "trek":
            chemin_banniere = "images/contexte/banniere.jpg"
            if os.path.exists(chemin_banniere):
                b64_banniere = get_image_base64(chemin_banniere)
                if b64_banniere:
                    st.markdown(f'<img src="{b64_banniere}" style="width:100%; max-height:450px; object-fit:cover; object-position:center; margin-bottom:20px;">', unsafe_allow_html=True)
            
            st.markdown("### Inspiration & Moodboard")
            
            col_vide1, col_vibe1, col_vibe2, col_vide2 = st.columns([0.5, 2, 2, 0.5])
            
            with col_vibe1:
                chemin_vibe1 = "images/contexte/vibe-1.jpg"
                if os.path.exists(chemin_vibe1):
                    b64_v1 = get_image_base64(chemin_vibe1)
                    if b64_v1:
                        st.markdown(f'<img src="{b64_v1}" style="width:100%; height:450px; object-fit:cover; border-radius:8px;">', unsafe_allow_html=True)
                        
            with col_vibe2:
                chemin_vibe2 = "images/contexte/Vibe-2.jpg" 
                if os.path.exists(chemin_vibe2):
                    b64_v2 = get_image_base64(chemin_vibe2)
                    if b64_v2:
                        st.markdown(f'<img src="{b64_v2}" style="width:100%; height:450px; object-fit:cover; border-radius:8px;">', unsafe_allow_html=True)
                        
            st.divider()

        # --- AFFICHAGE DES ARTICLES ---
        df_page = df[df['catégorie'] == page_actuelle]
        liste_sous_categories = df_page['sous-catégorie'].unique().tolist()

        for sous_cat in liste_sous_categories:
            st.header(f"📌 {sous_cat}")
            df_section = df_page[df_page['sous-catégorie'] == sous_cat]
            colonnes = st.columns(3) # Affichage sur 3 colonnes 
            
            for index, row in df_section.iterrows():
                lien = str(row['lien']).strip() if pd.notna(row['lien']) else ""
                nom = str(row['nom']).strip() if pd.notna(row['nom']) else "Article sans nom"
                prix = str(row['prix']).strip() if pd.notna(row['prix']) else "N/A"
                image_cellule = str(row['image']).strip() if pd.notna(row['image']) else ""
                
                favori_val = str(row['favori']).strip().lower()
                est_favori = favori_val in ['oui', 'x', '1', 'true']
                titre_affiche = f"⭐ {nom.capitalize()}" if est_favori else nom.capitalize()
                
                image_paths = []
                if image_cellule and image_cellule.lower() != 'nan':
                    if os.path.isdir(image_cellule):
                        fichiers = sorted(os.listdir(image_cellule))
                        for f in fichiers:
                            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                                image_paths.append(os.path.join(image_cellule, f))
                    elif os.path.isfile(image_cellule):
                        image_paths.append(image_cellule)

                if lien.startswith("http"):
                    # On utilise % 3 car on est sur 3 colonnes
                    col_index = list(df_section.index).index(index)
                    col = colonnes[col_index % 3]
                    
                    with col:
                        if len(image_paths) > 1:
                            st.markdown(build_carousel(image_paths), unsafe_allow_html=True)
                        elif len(image_paths) == 1:
                            st.markdown(f'<img src="{get_image_base64(image_paths[0])}" style="width:100%; height:250px; margin-bottom:15px;">', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<img src="{fetch_image_online(lien)}" style="width:100%; height:250px; margin-bottom:15px;">', unsafe_allow_html=True)
                        
                        st.subheader(titre_affiche)
                        st.write(f"**Prix : {prix} €**")
                        st.link_button("Voir l'article", lien)
            
            st.divider()

except FileNotFoundError:
    st.error("Le fichier 'Treck stuff.xlsx' est introuvable.")
except Exception as e:
    st.error(f"Une erreur s'est produite : {e}")
