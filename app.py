import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import base64

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Mon Catalogue", page_icon="📦", layout="wide")

st.markdown("""
<style>
    img { object-fit: cover !important; border-radius: 8px; }
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
    # Boucle pour afficher sidebar-1, sidebar-2 et sidebar-3
    for i in range(1, 4):
        chemin_sidebar = f"images/contexte/sidebar-{i}.jpg"
        if os.path.exists(chemin_sidebar):
            st.sidebar.image(chemin_sidebar, use_container_width=True)

    # --- EN-TÊTE DE LA PAGE PRINCIPALE ---
    st.title(f"Catégorie : {page_actuelle}")
    
    # Section Trek (Bannière et Moodboard)
    if page_actuelle.lower() == "trek":
        # Bannière : max-height pour éviter qu'elle soit géante, mais sans couper bizarrement
        chemin_banniere = "images/contexte/banniere.jpg"
        if os.path.exists(chemin_banniere):
            b64_banniere = get_image_base64(chemin_banniere)
            if b64_banniere:
                st.markdown(f'<img src="{b64_banniere}" style="width:100%; max-height:450px; object-fit:cover; object-position:center; margin-bottom:20px;">', unsafe_allow_html=True)
        
        # Section Inspiration
        st.markdown("### Inspiration & Moodboard")
        
        # Astuce : On crée 4 colonnes [vide, image, image, vide] pour réduire la taille au centre
        col_vide1, col_vibe1, col_vibe2, col_vide2 = st.columns([1, 2.5, 2.5, 1])
        
        with col_vibe1:
            chemin_vibe1 = "images/contexte/vibe-1.jpg"
            if os.path.exists(chemin_vibe1):
                # Utilisation de st.image pour garder la proportion 100% intacte
                st.image(chemin_vibe1, use_container_width=True)
                    
        with col_vibe2:
            chemin_vibe2 = "images/contexte/Vibe-2.jpg" 
            if os.path.exists(chemin_vibe2):
                st.image(chemin_vibe2, use_container_width=True)
                    
        st.divider()

    # --- AFFICHAGE DES ARTICLES ---
    df_page = df[df['catégorie'] == page_actuelle]
    liste_sous_categories = df_page['sous-catégorie'].unique().tolist()

    for sous_cat in liste_sous_categories:
        st.header(f"📌 {sous_cat}")
        df_section = df_page[df_page['sous-catégorie'] == sous_cat]
        colonnes = st.columns(4)
        
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
                col_index = list(df_section.index).index(index)
                col = colonnes[col_index % 4]
                
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
