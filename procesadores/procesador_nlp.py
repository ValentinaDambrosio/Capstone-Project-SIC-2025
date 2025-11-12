import json
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Optional, Tuple


class TextNLPProcessor:
    # Clase para procesamiento y comparación de textos
    def __init__(self, dataset: Optional[List[str]] = None, language: str = 'spanish') -> None:
        self.dataset = dataset or []
        self.language = language

    @staticmethod
    def cambiar_vocales(frase: str) -> str:
        frase = frase.replace("á", "a")
        frase = frase.replace("é", "e")
        frase = frase.replace("í", "i")
        frase = frase.replace("ó", "o")
        frase = frase.replace("ú", "u")
        frase = frase.replace("Á", "A")
        frase = frase.replace("É", "E")
        frase = frase.replace("Í", "I")
        frase = frase.replace("Ó", "O")
        frase = frase.replace("Ú", "U")
        return frase

    def _get_stopwords(self):
        try:
            return stopwords.words(self.language)
        except LookupError:
            return None

    def comparar_texto(self, frase: str, dataset: Optional[List[str]] = None) -> Tuple[str, float]:
        data = dataset if dataset is not None else self.dataset
        if not data:
            raise ValueError("No hay dataset disponible para comparar.")

        dataset_sin_tildes = [self.cambiar_vocales(texto.lower()) for texto in data]
        frase_sin_tildes = self.cambiar_vocales(frase.lower())

        stop_words = self._get_stopwords()
        vectorizer = TfidfVectorizer(stop_words=stop_words)
        tfidf_matrix = vectorizer.fit_transform(dataset_sin_tildes)
        vector_frase = vectorizer.transform([frase_sin_tildes])

        sims = cosine_similarity(vector_frase, tfidf_matrix)[0]
        mejor_idx = int(sims.argmax())
        mejor_sim = float(sims[mejor_idx])
        mejor_respuesta = data[mejor_idx]

        return mejor_respuesta, mejor_sim


class NLPProcessor:
    def __init__(self, path_json: str):
        self.path_json = path_json
        self.dataset = self.cargar_dataset()
        # Extrae preguntas para el procesador de texto
        self.preguntas = [item.get("pregunta", "") for item in self.dataset]
        # Instancia el procesador de NLP (alias para evitar colisión de nombres)
        self.text_processor: Optional[TextNLPProcessor] = None
        if any(self.preguntas):
            self.text_processor = TextNLPProcessor(dataset=self.preguntas)

    def cargar_dataset(self):
        try:
            with open(self.path_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def buscar_en_dataset(self, pregunta: str, umbral: float = 0.5):
        if not self.text_processor:
            return None

        respuesta_texto, score = self.text_processor.comparar_texto(pregunta)
        if score >= umbral:
            for item in self.dataset:
                if item.get("pregunta") == respuesta_texto:
                    return item.get("respuesta")
        return None
    
#   HERENCIA
# class MenstrualNLPProcessor(NLPProcessor):
#     def __init__(self, path_json: str, fase_actual: str):
#         super().__init__(path_json)  # llama al constructor de la clase base
#         self.fase_actual = fase_actual

#     def buscar_en_dataset(self, pregunta: str, umbral: float = 0.5):
#         if not self.text_processor:
#             return None

#         # Llamamos al comparar_texto pasando la fase
#         respuesta_texto, score = self.text_processor.comparar_texto(
#             frase=pregunta,
#             dataset=self.dataset,
#             fase=self.fase_actual
#         )
#         if score >= umbral:
#             return respuesta_texto
#         return None

# ---------------- HERENCIA ----------------
class MenstrualNLPProcessor(NLPProcessor):
    def __init__(self, path_json: str, fase_actual: str):
        super().__init__(path_json)
        self.fase_actual = fase_actual

    def buscar_en_dataset(self, pregunta: str, umbral: float = 0.5):
        """
        Busca respuestas dentro del dataset filtradas por la fase menstrual actual.
        """
        if not self.text_processor:
            return None

        # Filtramos solo las preguntas de la fase actual
        dataset_filtrado = [
            item for item in self.dataset
            if item.get("fase") == self.fase_actual
        ]
        if not dataset_filtrado:
            return None

        # Extraemos solo las preguntas para comparar
        preguntas_fase = [item["pregunta"] for item in dataset_filtrado]

        # Reutilizamos tu clase TextNLPProcessor sin modificarla
        procesador = TextNLPProcessor(dataset=preguntas_fase)
        mejor_pregunta, score = procesador.comparar_texto(pregunta)

        if score >= umbral:
            for item in dataset_filtrado:
                if item.get("pregunta") == mejor_pregunta:
                    return item.get("respuesta")
        return None

