from dataclasses import dataclass
from typing import Callable, Dict, List, Type




# ============================================================
# EVENTOS
# ============================================================


@dataclass
class Evento:
    """Clase base para todos los eventos del sistema."""
    pass




@dataclass
class PrestamoAprobado(Evento):
    estudiante: str
    equipo: str
    cantidad: int




@dataclass
class PrestamoRechazado(Evento):
    estudiante: str
    equipo: str
    cantidad: int
    motivo: str




# ============================================================
# BUS DE EVENTOS
# ============================================================


class BusDeEventos:
    """
    Mantiene consumidores registrados y distribuye eventos.
    """


    def __init__(self):
        self._suscriptores: Dict[Type[Evento], List[Callable]] = {}


    def suscribir(self, tipo_evento: Type[Evento], consumidor: Callable):
        if tipo_evento not in self._suscriptores:
            self._suscriptores[tipo_evento] = []


        self._suscriptores[tipo_evento].append(consumidor)


    def publicar(self, evento: Evento):
        tipo_evento = type(evento)
        consumidores = self._suscriptores.get(tipo_evento, [])


        for consumidor in consumidores:
            try:
                consumidor(evento)
            except Exception as error:
                print(
                    f"[BUS] Error en consumidor: "
                    f"{consumidor.__qualname__}: {error}"
                )




# ============================================================
# INVENTARIO
# ============================================================


class Inventario:
    """
    Administra los equipos disponibles en memoria.
    """


    def __init__(self, equipos_iniciales: Dict[str, int]):
        self._equipos = equipos_iniciales.copy()


    def disponible(self, equipo: str, cantidad: int) -> bool:
        if cantidad <= 0:
            return False


        return self._equipos.get(equipo, 0) >= cantidad


    def reservar(self, equipo: str, cantidad: int) -> bool:
        if not self.disponible(equipo, cantidad):
            return False


        self._equipos[equipo] -= cantidad
        return True


    def obtener_estado(self) -> Dict[str, int]:
        return self._equipos.copy()




# ============================================================
# MANEJADOR DE SOLICITUDES
# ============================================================


class ManejadorDeSolicitudes:
    """
    Valida solicitudes y publica eventos.
    No conoce directamente a los consumidores.
    """


    def __init__(self, inventario: Inventario, bus: BusDeEventos):
        self._inventario = inventario
        self._bus = bus
        self._solicitudes_procesadas = []


    def procesar_solicitud(
        self,
        estudiante: str,
        equipo: str,
        cantidad: int
    ) -> bool:


        if self._inventario.disponible(equipo, cantidad):
            self._inventario.reservar(equipo, cantidad)


            solicitud = {
                "estudiante": estudiante,
                "equipo": equipo,
                "cantidad": cantidad,
                "estado": "APROBADA"
            }


            self._solicitudes_procesadas.append(solicitud)


            evento = PrestamoAprobado(
                estudiante=estudiante,
                equipo=equipo,
                cantidad=cantidad
            )


            print(
                f"[MANEJADOR] Préstamo aprobado: "
                f"{estudiante} - {cantidad} {equipo}"
            )


            self._bus.publicar(evento)
            return True


        solicitud = {
            "estudiante": estudiante,
            "equipo": equipo,
            "cantidad": cantidad,
            "estado": "RECHAZADA"
        }


        self._solicitudes_procesadas.append(solicitud)


        evento = PrestamoRechazado(
            estudiante=estudiante,
            equipo=equipo,
            cantidad=cantidad,
            motivo="Cantidad no disponible"
        )


        print(
            f"[MANEJADOR] Préstamo rechazado: "
            f"{estudiante} - {cantidad} {equipo}"
        )


        self._bus.publicar(evento)
        return False


    def obtener_solicitudes(self):
        return self._solicitudes_procesadas.copy()




# ============================================================
# CONSUMIDOR: NOTIFICADOR
# ============================================================


class Notificador:
    """
    Reacciona a los eventos y muestra mensajes en consola.
    """


    def manejar_prestamo_aprobado(self, evento: PrestamoAprobado):
        print(
            f"[NOTIFICADOR] Notificación: el préstamo de "
            f"{evento.estudiante} fue aprobado."
        )


    def manejar_prestamo_rechazado(self, evento: PrestamoRechazado):
        print(
            f"[NOTIFICADOR] Notificación: el préstamo de "
            f"{evento.estudiante} fue rechazado. "
            f"Motivo: {evento.motivo}."
        )




# ============================================================
# CONSUMIDOR: REPORTE
# ============================================================


class ActualizadorDeReporte:
    """
    Mantiene un reporte de las solicitudes procesadas.
    """


    def __init__(self):
        self._reporte = []


    def registrar_aprobacion(self, evento: PrestamoAprobado):
        self._reporte.append({
            "estudiante": evento.estudiante,
            "equipo": evento.equipo,
            "cantidad": evento.cantidad,
            "estado": "APROBADA"
        })


    def registrar_rechazo(self, evento: PrestamoRechazado):
        self._reporte.append({
            "estudiante": evento.estudiante,
            "equipo": evento.equipo,
            "cantidad": evento.cantidad,
            "estado": "RECHAZADA",
            "motivo": evento.motivo
        })


    def obtener_reporte(self):
        return self._reporte.copy()




# ============================================================
# FUNCIONES DE PRESENTACIÓN
# ============================================================


def mostrar_inventario(inventario: Inventario):
    print("\nINVENTARIO ACTUAL")
    print("-----------------")


    for equipo, cantidad in inventario.obtener_estado().items():
        print(f"{equipo}: {cantidad}")




def mostrar_reporte(reporte: ActualizadorDeReporte):
    print("\nREPORTE DE SOLICITUDES")
    print("----------------------")


    for numero, solicitud in enumerate(
        reporte.obtener_reporte(),
        start=1
    ):
        print(
            f"{numero}. "
            f"{solicitud['estudiante']} - "
            f"{solicitud['cantidad']} {solicitud['equipo']} - "
            f"{solicitud['estado']}"
        )


        if "motivo" in solicitud:
            print(f"   Motivo: {solicitud['motivo']}")




# ============================================================
# PRUEBAS DE ACEPTACIÓN
# ============================================================


def ejecutar_pruebas():
    print("==============================================")
    print(" SISTEMA DE PRÉSTAMOS - ARQUITECTURA EVENTOS")
    print("==============================================")


    # 1. Crear inventario en memoria.
    inventario = Inventario({
        "portátiles": 2,
        "tabletas": 1
    })


    # 2. Crear bus de eventos.
    bus = BusDeEventos()


    # 3. Crear consumidores.
    notificador = Notificador()
    reporte = ActualizadorDeReporte()


    # 4. Registrar consumidores en el bus.
    bus.suscribir(
        PrestamoAprobado,
        notificador.manejar_prestamo_aprobado
    )


    bus.suscribir(
        PrestamoRechazado,
        notificador.manejar_prestamo_rechazado
    )


    bus.suscribir(
        PrestamoAprobado,
        reporte.registrar_aprobacion
    )


    bus.suscribir(
        PrestamoRechazado,
        reporte.registrar_rechazo
    )


    # 5. Crear manejador.
    manejador = ManejadorDeSolicitudes(inventario, bus)


    # Caso 1: Inventario inicial.
    print("\nCASO 1: INVENTARIO INICIAL")
    mostrar_inventario(inventario)


    # Caso 2: Solicitud aprobada.
    print("\nCASO 2: SOLICITUD APROBADA")
    manejador.procesar_solicitud(
        estudiante="Ana",
        equipo="portátiles",
        cantidad=1
    )
    mostrar_inventario(inventario)


    # Caso 3: Solicitud rechazada.
    print("\nCASO 3: SOLICITUD RECHAZADA")
    manejador.procesar_solicitud(
        estudiante="Juan",
        equipo="tabletas",
        cantidad=2
    )
    mostrar_inventario(inventario)


    # Caso 4: Reporte final.
    print("\nCASO 4: REPORTE FINAL")
    mostrar_reporte(reporte)




if __name__ == "__main__":
    ejecutar_pruebas()