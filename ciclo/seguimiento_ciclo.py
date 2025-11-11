import json
import os
from datetime import datetime, timedelta

class CycleTracker:
    def __init__(self, archivo_ciclos: str = "ciclos.json"):
        base_dir = os.path.dirname(__file__)
        self.archivo = os.path.join(base_dir, archivo_ciclos)
        self.registro = {}
        self._cargar()
    
    def _guardar_json(self):
        # Asegura que el directorio existe
        dirpath = os.path.dirname(self.archivo)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)

        with open(self.archivo, "w", encoding="utf-8") as f:
            json.dump(self.registro, f, ensure_ascii=False, indent=2)
    
    def _cargar(self):
        if not os.path.exists(self.archivo):
            self._guardar_json()
        else:
            try:
                with open(self.archivo, "r", encoding="utf-8") as f:
                    contenido = f.read().strip()
                    self.registro = json.loads(contenido) if contenido else {}
            except Exception as e:
                print(f"⚠️ Error al cargar ciclos: {e}")
                self.registro = {}
    
    def registrar_fecha(self, chat_id, fecha):
        self.registro[str(chat_id)] = fecha.strftime("%d-%m-%Y")
        self._guardar_json()
    
    def calcular_estado(self, chat_id, fecha=None):
        key = str(chat_id)
        if key not in self.registro:
            return None

        fecha_guardada = datetime.strptime(self.registro[key], "%d-%m-%Y")
        hoy = datetime.now()
        dias_desde = (hoy - fecha_guardada).days
        dia_ciclo = dias_desde + 1

        if 1 <= dia_ciclo <= 5:
            fase = "Menstruación"
        elif 6 <= dia_ciclo <= 13:
            fase = "Fase folicular"
        elif 14 <= dia_ciclo <= 16:
            fase = "Ovulación"
        else:
            fase = "Fase lútea"
        
        proximo = fecha_guardada + timedelta(days=28)
        dias_restantes = (proximo - hoy).days
        
        if dias_restantes < 0:
            atrasado = True
        else:
            atrasado = False

        return {
            "ultimo": fecha_guardada.strftime('%d/%m/%Y'),
            "dia_ciclo": dia_ciclo,
            "fase": fase,
            "proximo": proximo.strftime('%d/%m/%Y'),
            "restantes": dias_restantes,
            'atrasado': atrasado
        }
    
    def generar_mensaje(self, chat_id):
        estado = self.calcular_estado(chat_id)

        if not estado:
            return f"Todavía no registraste tu última fecha de ciclo 🌸\n Podés hacerlo con el botón 'Registrar mi ciclo' 📅"
        
        if estado["restantes"] < 0:
            dias = f"Días atrasado: {(estado['restantes'])*-1} días."
            aviso = "\n\n⚠️ Parece que tu ciclo está atrasado. Si la demora persiste, considerá consultar a un profesional de salud."
        else:
            if 5>= estado["restantes"] >= 0:
                aviso = (
                "\n\n🪷 ¡Atención! Tu próximo ciclo está por comenzar pronto. "
                "¡No olvides registrarlo!"
                )
            else:
                aviso = ""
            dias = f"Días restantes: {estado['restantes']} días."
            mensaje_atraso = ""

        mensaje = (
            f"📅 Última fecha registrada: {estado['ultimo']}\n"
            f"🔢 Día del ciclo: {estado['dia_ciclo']}\n"
            f"🌗 Fase actual: {estado['fase']}\n"
            f"➡️ Próximo ciclo estimado: {estado['proximo']}\n"
            f"🕓 {dias}"
            f"{aviso}"
        )
        return mensaje
    
    def borrar(self, chat_id):
        if chat_id in self.registro:
            del self.registro[chat_id]
            self._guardar_json()
            return True
        return False