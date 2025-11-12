from datetime import datetime, timedelta

class ExceptionFechas(Exception):
    
    def __init__(self, mensaje="La fecha no puede ser futura."):
        super().__init__(mensaje)

    @staticmethod
    def validar_fecha(fecha):
        fecha_usuario = datetime.strptime(fecha, "%d/%m/%Y").date()
        fecha_actual = datetime.now().date()
        fecha_anio_atras = fecha_actual - timedelta(days=365)
        if fecha_usuario > fecha_actual:
            raise ExceptionFechas("La fecha no puede ser futura.")
        elif fecha_usuario < fecha_anio_atras:
            raise ExceptionFechas("Tu último periodo debería haber sido hace menos de un año.")
        return fecha_usuario

