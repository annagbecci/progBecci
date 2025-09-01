import numpy as np
from libreria.models import Utente, Tag


def cosine_similarity(user1, user2):
    # Lista di tutti i tag esistenti
    all_tags = list(Tag.objects.values_list("id", flat=True))

    # Vettore binario per user1: quello autenticato
    tags1 = set(user1.tags.values_list("id", flat=True))
    vec1 = np.array([1 if tag in tags1 else 0 for tag in all_tags])

    # Vettore binario per user2: ogni altro utente con cui mi confronto
    tags2 = set(user2.tags.values_list("id", flat=True))
    vec2 = np.array([1 if tag in tags2 else 0 for tag in all_tags])

    # Cosine similarity
    """np.dot fa il prodotto scalare tra vec1 e vec2 => 
    => poiché i vettori sono binari, equivale a contare i tag in comune"""
    dot_product = np.dot(vec1, vec2)

    """np.linalg è il modulo di NumPy per l'algebra lineare
    norm è il prodotto delle norme dei due vettori"""
    norm = (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    if norm == 0:  # uno dei due utenti non ha tag => non può succedere per costruzione
        return 0.0

    """calcolo della similarità
    - numeratore: quanti tag hanno in comune (prod scalare)
    - denominatore: quanto sono "lunghi" i  profili (NORMALIZZAZIONE)"""
    return dot_product / norm


