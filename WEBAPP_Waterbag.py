import streamlit as st
import matplotlib.pyplot as plt
import firebase_admin
from firebase_admin import credentials, db, initialize_app
import os
import json
from matplotlib.patches import FancyBboxPatch

# Configura il layout della pagina per avere tre colonne
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    div.stColumn {
        border: 2px solid #ccc;
        border-radius: 10px;
        padding: 10px;
        background-color: #f9f9f9;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Carica l'intera sezione FIREBASE_KEY dalle Streamlit Secrets
firebase_secrets = st.secrets["FIREBASE_KEY"]

# Carica le credenziali Firebase
firebase_creds = {
    "type": firebase_secrets["type"],
    "project_id": firebase_secrets["project_id"],
    "private_key_id": firebase_secrets["private_key_id"],
    "private_key": firebase_secrets["private_key"].replace("\\n", "\n"),
    "client_email": firebase_secrets["client_email"],
    "client_id": firebase_secrets["client_id"],
    "auth_uri": firebase_secrets["auth_uri"],
    "token_uri": firebase_secrets["token_uri"],
    "auth_provider_x509_cert_url": firebase_secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": firebase_secrets["client_x509_cert_url"],
    "universe_domain": firebase_secrets["universe_domain"]
}

# Evita di inizializzare Firebase più volte
if not firebase_admin._apps:
    # Leggi il databaseURL dalle secrets
    database_url = st.secrets["FIREBASE_KEY"]["databaseURL"]

    # Fornisci il certificato e inizializza Firebase
    cred = credentials.Certificate(firebase_creds)  # Il percorso del certificato deve essere ancora gestito.
    firebase_admin.initialize_app(cred, {
        "databaseURL": database_url
    })

# Test della connessione
try:
    ref = db.reference("/")  # Accedi al nodo principale
    data = ref.get()
    if data is not None:
        print("Connessione riuscita. Dati trovati:", data)
    else:
        print("Connessione riuscita, ma nessun dato trovato.")
except Exception as e:
    print("Errore durante la connessione al database:", e)

    
# Funzione per caricare il listino personalizzato
def carica_listino(cliente):
    try:
        # Riferimento al nodo del cliente
        ref = db.reference(f"listini/{cliente}")
        listino_esistente = ref.get()

        # Listino di default con tutte le misure
        listino_default = [
            {"misura": 2, "prezzo_unitario": 10},
            {"misura": 3, "prezzo_unitario": 11.8},
            {"misura": 4, "prezzo_unitario": 13.4},
            {"misura": 5, "prezzo_unitario": 15},
            {"misura": 6, "prezzo_unitario": 20.6},
            {"misura": 8, "prezzo_unitario": 23.5},
            {"misura": 10, "prezzo_unitario": 26.3},
            {"misura": 12, "prezzo_unitario": 29},
            {"misura": 14, "prezzo_unitario": 32.7},
            {"misura": 15, "prezzo_unitario": 34.6},
            {"misura": 16, "prezzo_unitario": 36},
            {"misura": 18, "prezzo_unitario": 39},
            {"misura": 20, "prezzo_unitario": 42},
            {"misura": 24, "prezzo_unitario": 48},
            {"misura": 26, "prezzo_unitario": 52},
            {"misura": 28, "prezzo_unitario": 56},
            {"misura": 30, "prezzo_unitario": 60},
        ]

        # Se il listino non esiste, lo crea da zero
        if listino_esistente is None:
            ref.set(listino_default)
            return listino_default
        
        # Se il listino esiste, aggiorna solo le voci mancanti senza sovrascrivere i prezzi esistenti
        listino_aggiornato = {item["misura"]: item["prezzo_unitario"] for item in listino_esistente}

        for item in listino_default:
            if item["misura"] not in listino_aggiornato:
                listino_aggiornato[item["misura"]] = item["prezzo_unitario"]  # Aggiungi solo se manca

        # Converti il dizionario in lista per mantenere la struttura originale
        listino_finale = [{"misura": misura, "prezzo_unitario": prezzo} for misura, prezzo in sorted(listino_aggiornato.items())]

        # Salva il listino aggiornato nel database
        ref.set(listino_finale)

        return listino_finale

    except Exception as e:
        st.error(f"Errore durante il caricamento del listino: {e}")
        return []


# Funzione per salvare il listino personalizzato
def salva_listino(cliente, listino):
    ref = db.reference(f"listini/{cliente}")  # Percorso nel database per il cliente
    ref.set(listino)  # Salva il nuovo listino nel database






translations = {
    "it": {
        "title": "Calcola Waterbag Trincea",
        "customer_id": "Identificazione Cliente",
        "enter_name": "Inserisci il tuo nome o ID cliente:",
        "draw_button": "Disegna Trincea",
        "save_button": "Salva Prezzi",
        "drawing_section": "Disegno della Trincea",
        "summary_section": "Riepilogo Waterbag Utilizzati",
        "total_price": "Prezzo Totale",
        "total_volume": "Volume Totale Acqua",
	"width": "Larghezza (metri)",
	"lenght": "Lunghezza (metri)",
	"insert": "Inserisci i dati della Trincea",
	"price_list": "Listino di",
	"saved": "I prezzi sono stati salvati per il cliente",
	"insert_draw": "Inserisci i dati e premi 'Disegna Trincea' per visualizzare il disegno",
	"result": "Nessun waterbag disegnato. Premi 'Disegna Trincea'.",
	"unit_prize": "Prezzo unitario per",
	"horizontal": "Orizzontale",
	"vertical": "Verticale",
	"bunker": "Trincea con waterbag:",
	"prize_u": "prezzo_unitario",
	"size": "misura",
	"tot": "Totale",
	"single_volume": "Volume singolo",
	"pieces": "pezzi",
        "warning": "ATTENZIONE: Il campo del nome cliente distingue tra maiuscole e minuscole. Assicurati di inserire i dati correttamente",
        "warning_price": "ATTENZIONE: Se modifichi un prezzo, clicca su 'Salva Prezzi' in fondo al listino prima di disegnare la Trincea"
    },
    "en": {
        "title": "Calculate Waterbag Bunker",
        "customer_id": "Customer Identification",
        "enter_name": "Enter your name or customer ID:",
        "draw_button": "Draw Bunker",
        "save_button": "Save Prices",
        "drawing_section": "Bunker Drawing",
        "summary_section": "Waterbag Summary",
        "total_price": "Total Price",
        "total_volume": "Total Water Volume",
	"width": "Width (metres)",
	"lenght": "Lenght (metres)",
	"insert": "Enter the Bunker data",
	"price_list": "Price list",
	"saved": "Prices have been saved for the customer",
	"insert_draw": "Enter the data and press 'Draw Bunker' to view the drawing",
	"result": "No waterbag drawn. Press 'Draw Bunker'.",
	"unit_prize": "unit price for",
	"horizontal": "Horizontal",
	"vertical": "Vertical",
	"bunker": "Bunker with waterbag:",
	"prize_u": "unitary price",
	"size": "size",
	"tot": "Total",
	"single_volume": "Single volume",
	"pieces": "pieces",
        "warning": "CAUTION: The customer name field is case sensitive. Please make sure you enter your data correctly",
        "warning_price": "CAUTION: If you change a price, click on 'Save Prices' at the bottom of the list before you draw the Trench"
	}
}

# Selettore lingua
lang = st.sidebar.selectbox("Seleziona Lingua / Select Language", ["it", "en"])

# Funzione per tradurre
def t(key):
    return translations[lang].get(key, key)



# Titolo principale
st.title(t("title"))


# Selezione del cliente
st.subheader(t("customer_id"))

cliente = st.text_input(t("enter_name"), value="Default")
cliente = cliente.upper()
#st.markdown(f"<span style='color:red;'>{t('warning')}</span>", unsafe_allow_html=True)

# Crea tre sezioni: colonna per i dati di input, colonna per il disegno e colonna per il riepilogo
col1, col2, col3 = st.columns([1, 2, 1])  # Layout personalizzato: [1/4, 1/2, 1/4]

# Carica il listino per il cliente
listino = carica_listino(cliente)

# Dizionario per memorizzare i waterbag
waterbag_dict = {}
    

# Colonna di sinistra: inserimento dati
with col1:
    st.header(t("insert"))
	
    # Input per larghezza e lunghezza
    larghezza = st.number_input(t("width"), min_value=1, value=5, step=1)
    lunghezza = st.number_input(t("lenght"), min_value=1, value=10, step=1)
    
    # Bottone per disegnare
    disegna = st.button(t("draw_button"))

    st.markdown("---")

    # Mostra il listino e consenti la modifica
    st.subheader(f"{t('price_list')} {cliente}")
    nuovi_prezzi = []
    
    for item in listino:
        misura = item["misura"]
        prezzo = float(item["prezzo_unitario"])  # Forza il prezzo in float
        
        # Usa st.number_input per creare campi modificabili
        nuovo_prezzo = st.number_input(
            f"{t('unit_prize')} {misura} mt:",
            value=float(prezzo),  # Assicurati che value sia un float
            min_value=0.0,        # Assicurati che min_value sia un float
            step=0.1,             # Lo step è già un float
            format="%.2f"
        )
        nuovi_prezzi.append({"misura": misura, "prezzo_unitario": nuovo_prezzo})
    
    # Bottone per salvare i nuovi prezzi
    if st.button(t("save_button")):
        salva_listino(cliente, nuovi_prezzi)
        st.success(f"{t('saved')} '{cliente}'!")
    


# Colonna di destra: disegno
with col2:
    st.header(t("drawing_section"))
    
    # Se il bottone viene premuto, disegna la trincea
    if disegna:
        # Creazione del grafico
        fig, ax = plt.subplots(figsize=(6, 6))

        # Disegna la trincea principale (rettangolo blu)
        ax.add_patch(FancyBboxPatch((0, 0), larghezza, lunghezza, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='blue', facecolor='lightblue', lw=2))

        # Calcola il numero di sezioni e l'avanzamento
        num_sezioni = lunghezza // 5  # Quante sezioni complete di 5 metri ci sono
        avanzamento = lunghezza % 5  # Quanti metri avanzano oltre i multipli di 5

        # Funzione per aggiungere waterbag al dizionario
        def aggiungi_waterbag(tipologia, dimensione, posizione):
            key = f"{tipologia} {dimensione}m"
            if key not in waterbag_dict:
                waterbag_dict[key] = 0
            waterbag_dict[key] += 1

        # Funzione per disegnare rettangoli orizzontali
        def disegna_orizzontali(y_start):
            if larghezza in [7, 9, 11]:
                # Rettangolo unico da larghezza + 1 metro
                extra_larghezza = larghezza + 1
                x_start = (larghezza - extra_larghezza) / 2
                ax.add_patch(FancyBboxPatch((x_start, y_start), extra_larghezza, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                aggiungi_waterbag(t("horizontal"), extra_larghezza, f"y={y_start}")
            elif larghezza <= 12:
                # Rettangolo unico da larghezza
                ax.add_patch(FancyBboxPatch((0, y_start), larghezza, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                aggiungi_waterbag(t("horizontal"), larghezza, f"y={y_start}")
            elif larghezza in [15, 18, 19, 22]:
                # Due rettangoli da metà larghezza + 1 metro
                segment_length = (larghezza // 2) + 1
                # Punto di partenza disegno rettangoli diverso
                if larghezza in [15, 19]:
                    ax.add_patch(FancyBboxPatch((-0.5, y_start), segment_length, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                    ax.add_patch(FancyBboxPatch((larghezza / 2, y_start), segment_length, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                else:
                    ax.add_patch(FancyBboxPatch((-1, y_start), segment_length, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                    ax.add_patch(FancyBboxPatch((larghezza / 2, y_start), segment_length, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                aggiungi_waterbag(t("horizontal"), segment_length, f"y={y_start}")
                aggiungi_waterbag(t("horizontal"), segment_length, f"y={y_start}")
            elif larghezza in [13, 16, 17, 20, 21]:
                # Due rettangoli, uno da metà larghezza e uno da metà larghezza + 2
                segment_length_1 = larghezza // 2
                segment_length_2 = segment_length_1 + 2
                if larghezza in [13, 17]:
                    ax.add_patch(FancyBboxPatch((-0.5, y_start), segment_length_1, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                    ax.add_patch(FancyBboxPatch((segment_length_1 - 0.5, y_start), segment_length_2, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                else:
                    ax.add_patch(FancyBboxPatch((-1, y_start), segment_length_1, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                    ax.add_patch(FancyBboxPatch((segment_length_1 - 1, y_start), segment_length_2, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                aggiungi_waterbag(t("horizontal"), segment_length_1, f"y={y_start}")
                aggiungi_waterbag(t("horizontal"), segment_length_2, f"y={y_start}")
            elif larghezza == 14:
                segment_length_1 = (larghezza // 2) -1
                segment_length_2 = segment_length_1 + 2
                ax.add_patch(FancyBboxPatch((0, y_start), segment_length_1, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                ax.add_patch(FancyBboxPatch((segment_length_1, y_start), segment_length_2, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                aggiungi_waterbag(t("horizontal"), segment_length_1, f"y={y_start}")
                aggiungi_waterbag(t("horizontal"), segment_length_2, f"y={y_start}")              
            #elif larghezza == 24:
                #segment_length_1 = (larghezza // 3) +2
                #segment_length_2 = (larghezza // 3)
                #segment_length_3 = (larghezza // 3)
                #ax.add_patch(FancyBboxPatch((-1, y_start), segment_length_1, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                #ax.add_patch(FancyBboxPatch((segment_length_1-1, y_start), segment_length_2, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                #ax.add_patch(FancyBboxPatch((segment_length_1 + segment_length_2 -1, y_start), segment_length_3, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                #aggiungi_waterbag(t("horizontal"), segment_length_1, f"y={y_start}")
                #aggiungi_waterbag(t("horizontal"), segment_length_2, f"y={y_start}")
                #aggiungi_waterbag(t("horizontal"), segment_length_3, f"y={y_start}")
            elif larghezza in [24, 28, 32, 36, 40, 48, 52, 56, 60]:
                # Due rettangoli da metà larghezza
                segment_length_1 = (larghezza // 2)
                segment_length_2 = (larghezza // 2)
                ax.add_patch(FancyBboxPatch((0, y_start), segment_length_1, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                ax.add_patch(FancyBboxPatch((segment_length_1, y_start), segment_length_2, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                aggiungi_waterbag(t("horizontal"), segment_length_1, f"y={y_start}")
                aggiungi_waterbag(t("horizontal"), segment_length_2, f"y={y_start}")

            elif larghezza in [26, 30, 34, 38, 50, 54, 58]:
                # Due rettangoli, uno da metà larghezza -1 e uno +1
                segment_length_1 = (larghezza // 2) -1
                segment_length_2 = (larghezza // 2) +1
                ax.add_patch(FancyBboxPatch((0, y_start), segment_length_1, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                ax.add_patch(FancyBboxPatch((segment_length_1, y_start), segment_length_2, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                aggiungi_waterbag(t("horizontal"), segment_length_1, f"y={y_start}")
                aggiungi_waterbag(t("horizontal"), segment_length_2, f"y={y_start}")
            elif larghezza in [24, 26, 30, 34, 38, 50, 54, 58]:
                # Due rettangoli da metà larghezza
                segment_length_1 = (larghezza // 2)
                segment_length_2 = (larghezza // 2)
                ax.add_patch(FancyBboxPatch((0, y_start), segment_length_1, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                ax.add_patch(FancyBboxPatch((segment_length_1, y_start), segment_length_2, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                aggiungi_waterbag(t("horizontal"), segment_length_1, f"y={y_start}")
                aggiungi_waterbag(t("horizontal"), segment_length_2, f"y={y_start}")
            elif larghezza in [42, 44]:
                # Due rettangoli, uno da metà larghezza -1 e uno +1
                segment_length_1 = 20
                segment_length_2 = 24
                if larghezza == 42:
                    ax.add_patch(FancyBboxPatch((-1, y_start), segment_length_1, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                    ax.add_patch(FancyBboxPatch((segment_length_1-1, y_start), segment_length_2, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                else:
                    ax.add_patch(FancyBboxPatch((0, y_start), segment_length_1, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                    ax.add_patch(FancyBboxPatch((segment_length_1, y_start), segment_length_2, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                aggiungi_waterbag(t("horizontal"), segment_length_1, f"y={y_start}")
                aggiungi_waterbag(t("horizontal"), segment_length_2, f"y={y_start}")
            elif larghezza in [46]:
                segment_length_1 = 24
                segment_length_2 = 24
                ax.add_patch(FancyBboxPatch((-1, y_start), segment_length_1, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                ax.add_patch(FancyBboxPatch((segment_length_1-1, y_start), segment_length_2, 0.5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
                aggiungi_waterbag(t("horizontal"), segment_length_1, f"y={y_start}")
                aggiungi_waterbag(t("horizontal"), segment_length_2, f"y={y_start}")
                

        # Disegna i rettangoli orizzontali sopra, sotto e ogni 5 metri dentro la trincea
        disegna_orizzontali(-1)  # Sopra la trincea
        disegna_orizzontali(lunghezza + 0.6)  # Sotto la trincea
        for y in range(5, int(lunghezza), 5):  # Ogni 5 metri dentro la trincea
            disegna_orizzontali(y)

        # Disegna i rettangoli verticali_____________________________________________________________________
        for i in range(int(num_sezioni)):
            if avanzamento == 1 and i==(int(num_sezioni)-1):
                break
            y_start = i * 5
            bordo_raggio = 0.5 
            ax.add_patch(FancyBboxPatch((-1, y_start), 0.5, 5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))  # Sinistra
            ax.add_patch(FancyBboxPatch((larghezza + 0.5, y_start), 0.5, 5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))  # Destra
            aggiungi_waterbag(t("vertical"), 5, f"x=-1, y={y_start}")
            aggiungi_waterbag(t("vertical"), 5, f"x={larghezza + 0.5}, y={y_start}")

        # Gestione dell'avanzamento
        if avanzamento == 1:
            # Aggiungi un ulteriore rettangolo da 6 metri
            y_start = (num_sezioni-1) * 5
            ax.add_patch(FancyBboxPatch((-1, y_start), 0.5, 6, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))  # Sinistra
            ax.add_patch(FancyBboxPatch((larghezza + 0.5, y_start), 0.5, 6, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))  # Destra
            aggiungi_waterbag(t("vertical"), 6, f"x=-1, y={y_start}")
            aggiungi_waterbag(t("vertical"), 6, f"x={larghezza + 0.5}, y={y_start}")
        elif avanzamento == 2:
            # Disegna un rettangolo aggiuntivo da 2 metri
            y_start = num_sezioni * 5
            ax.add_patch(FancyBboxPatch((-1, y_start), 0.5, 2, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))  # Sinistra
            ax.add_patch(FancyBboxPatch((larghezza + 0.5, y_start), 0.5, 2, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
            aggiungi_waterbag(t("vertical"), 2, f"x=-1, y={y_start}")
            aggiungi_waterbag(t("vertical"), 2, f"x={larghezza + 0.5}, y={y_start}")# Destra
        elif avanzamento in [3, 4]:
            # Disegna un rettangolo aggiuntivo da 5 metri (sborda rispetto alla trincea)
            y_start = num_sezioni * 5
            ax.add_patch(FancyBboxPatch((-1, y_start), 0.5, 5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))  # Sinistra
            ax.add_patch(FancyBboxPatch((larghezza + 0.5, y_start), 0.5, 5, boxstyle=f"round,pad=0.02,rounding_size=0.3", edgecolor='black', facecolor='red', lw=1))
            aggiungi_waterbag(t("vertical"), 5, f"x=-1, y={y_start}")
            aggiungi_waterbag(t("vertical"), 5, f"x={larghezza + 0.5}, y={y_start}")# Destra
            
        # Configura gli assi
        ax.set_xlim(-2, larghezza + 2)  # Imposta i limiti dell'asse x in metri
        ax.set_ylim(-1, lunghezza + 6)  # Imposta i limiti dell'asse y in metri
        ax.set_aspect('equal', adjustable='box')

        # Aggiungi una griglia con tacche ogni 5 metri
        ax.set_xticks(range(0, larghezza + 3, 5))  # Tacche sull'asse x ogni 5 metri
        ax.set_yticks(range(0, lunghezza + 7, 5))  # Tacche sull'asse y ogni 5 metri
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

        # Titoli ed etichette
        ax.set_title(f"{t('bunker')} {larghezza}m x {lunghezza}m", fontsize=8)
        ax.set_xlabel(f"{t('width')}")
        ax.set_ylabel(f"{t('lenght')}")

        # Mostra il grafico nella colonna di destra
        st.pyplot(fig)
        
    else:
        st.write(t("insert_draw"))
        
        
# Colonna destra: riepilogo
with col3:
    st.subheader(t("summary_section"))
    st.markdown(f"<span style='color:red;'>{t('warning_price')}</span>", unsafe_allow_html=True)
    prezzo_totale = 0
    volume_totale = 0  # Variabile per calcolare il volume totale

    if disegna:
        for waterbag, count in waterbag_dict.items():
            # Estrai la dimensione del waterbag come float
            dimensione = float(waterbag.split()[1].replace("m", ""))
            
            # Calcola il prezzo unitario dal listino
            prezzo_unitario = next((item["prezzo_unitario"] for item in listino if item["misura"] == dimensione), 0)
            
            # Calcola il costo totale per questo tipo di waterbag
            costo_totale = prezzo_unitario * count
            prezzo_totale += costo_totale
            
            # Calcola il volume di acqua per singolo waterbag
            volume_per_bag = (dimensione * 14.2) - 4.2
            
            # Aggiungi il volume totale per il numero di waterbag di questa dimensione
            volume_totale += volume_per_bag * count
            
            # Mostra i dettagli del waterbag nel riepilogo
            st.write(f"{waterbag}: {count} {t('pieces')} {t('prize_u')}: {prezzo_unitario:.2f}, {t('tot')}: {costo_totale:.2f}, {t('single_volume')}: {volume_per_bag:.2f} l")
	    

        # Mostra il prezzo totale alla fine
        st.markdown(f"### {t('total_price')}: {prezzo_totale:.2f}")
        
        # Mostra il volume totale necessario
        st.markdown(f"### {t('total_volume')}: {volume_totale:.2f} l")
    else:
        st.write(t("result"))

