import json
import os
from datetime import datetime, timedelta

class CycleTracker:
    def __init__(self, archivo_ciclos: str = "ciclos.json"):
        base_dir = os.path.dirname(__file__)
        self.archivo = os.path.join(base_dir, archivo_ciclos)
        self.registro = {}
        self._cargar()
    
    def _guardar(self):
        # Asegura que el directorio existe
        dirpath = os.path.dirname(self.archivo)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)

        with open(self.archivo, "w", encoding="utf-8") as f:
            json.dump(self.registro, f, ensure_ascii=False, indent=2)
    
    def _cargar(self):
        if not os.path.exists(self.archivo):
            self._guardar()
        else:
            try:
                with open(self.archivo, "r", encoding="utf-8") as f:
                    contenido = f.read().strip()
                    self.registro = json.loads(contenido) if contenido else {}
            except Exception as e:
                print(f"⚠️ Error al cargar ciclos: {e}")
                self.registro = {}
    
    def registrar_fecha(self, chat_id, fecha):
        self.registro[str(chat_id)] = fecha.strftime("%Y-%m-%d")
        self._guardar()
    
    def calcular_estado(self, chat_id, fecha=None):
        key = str(chat_id)
        if key not in self.registro:
            return None

        fecha_guardada = datetime.strptime(self.registro[key], "%Y-%m-%d")
        hoy = datetime.now()
        dias_desde = (hoy - fecha_guardada).days
        dia_ciclo = (dias_desde % 28) + 1

        if 1 <= dia_ciclo <= 5:
            fase = "Menstruación 🩸"
        elif 6 <= dia_ciclo <= 13:
            fase = "Fase folicular 🌱"
        elif 14 <= dia_ciclo <= 16:
            fase = "Ovulación 🌸"
        else:
            fase = "Fase lútea 🌕"
        
        proximo = fecha_guardada + timedelta(days=28)
        dias_restantes = (proximo - hoy).days

        return {
            "ultimo": fecha_guardada.strftime('%d/%m/%Y'),
            "dia_ciclo": dia_ciclo,
            "fase": fase,
            "proximo": proximo.strftime('%d/%m/%Y'),
            "restantes": dias_restantes
        }
    
    def borrar(self, chat_id):
        if chat_id in self.registro:
            del self.registro[chat_id]
            self._guardar()
            return True
        return False