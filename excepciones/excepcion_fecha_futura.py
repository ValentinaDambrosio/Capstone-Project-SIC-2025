from datetime import datetime

class ExceptionFechaFutura(Exception):
    
    def __init__(self, mensaje="La fecha no puede ser futura."):
        super().__init__(mensaje)

    @staticmethod
    def validar_fecha(fecha):
        fecha_usuario = datetime.strptime(fecha, "%d/%m/%Y").date()
        fecha_actual = datetime.now().date()
        if fecha_usuario > fecha_actual:
            raise ExceptionFechaFutura("La fecha no puede ser futura.")
        return fecha_usuario
    

