#Procesamiento de mensajes del usuario

import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def cambiar_vocales(frase):
    frase = frase.replace("á", "a")
    frase = frase.replace("é", "e")
    frase = frase.replace("í", "i")
    frase = frase.replace("ó", "o")
    frase = frase.replace("ú", "u")
    return frase



def comparar_texto(frase, dataset):
    dataset_sin_tildes = [cambiar_vocales(texto.lower()) for texto in dataset]
    frase_sin_tildes = cambiar_vocales(frase.lower())
    stop_words = stopwords.words('spanish')
    vectorizer = TfidfVectorizer(stop_words=stop_words)
    tfidf_matrix = vectorizer.fit_transform(dataset_sin_tildes)
    vector_frase = vectorizer.transform([frase_sin_tildes])
    
    mejor_sim = -1
    mejor_respuesta = ""
    
    for i, vector_doc in enumerate(tfidf_matrix):
        sim = cosine_similarity(vector_frase, vector_doc)[0][0]
        if sim > mejor_sim:
            mejor_sim = sim
            mejor_respuesta = dataset[i]
    
    return mejor_respuesta, mejor_sim

