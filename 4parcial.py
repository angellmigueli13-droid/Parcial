import queue
import time
import random
from datetime import datetime, timedelta

class Paciente:
    """Clase que representa a un paciente en el sistema"""
    def __init__(self, nombre, edad, motivo_consulta, es_urgencia=False):
        self.nombre = nombre
        self.edad = edad
        self.motivo_consulta = motivo_consulta
        self.es_urgencia = es_urgencia
        self.hora_llegada = datetime.now()
        self.hora_atencion = None
        self.id_paciente = random.randint(1000, 9999)
    
    def __str__(self):
        urgencia_str = " [URGENCIA]" if self.es_urgencia else ""
        return f"ID: {self.id_paciente} | {self.nombre} ({self.edad} años) - {self.motivo_consulta}{urgencia_str}"
    
    def marcar_atencion(self):
        """Marca la hora en que el paciente fue atendido"""
        self.hora_atencion = datetime.now()
    
    def tiempo_espera(self):
        """Calcula el tiempo de espera del paciente"""
        if self.hora_atencion:
            return self.hora_atencion - self.hora_llegada
        return datetime.now() - self.hora_llegada

class SistemaGestionTurnos:
    """Sistema principal de gestión de turnos médicos"""
    
    def __init__(self, nombre_clinica):
        self.nombre_clinica = nombre_clinica
        self.cola_normal = queue.Queue()  # Cola para pacientes normales
        self.cola_urgencias = queue.Queue()  # Cola para urgencias
        self.pacientes_atendidos = []  # Lista de pacientes ya atendidos
        self.pacientes_abandonaron = []  # Lista de pacientes que se fueron
        
    def registrar_paciente(self, nombre, edad, motivo_consulta, es_urgencia=False):
        """Registra un nuevo paciente en el sistema"""
        paciente = Paciente(nombre, edad, motivo_consulta, es_urgencia)
        
        if es_urgencia:
            self.cola_urgencias.put(paciente)
            print(f" Paciente con urgencia registrado: {paciente.nombre}")
        else:
            self.cola_normal.put(paciente)
            print(f" Paciente registrado: {paciente.nombre}")
        
        return paciente
    
    def atender_siguiente_paciente(self):
        """Atiende al siguiente paciente en orden de prioridad"""
        paciente = None
        
        # Prioridad: primero las urgencias, luego los normales
        if not self.cola_urgencias.empty():
            paciente = self.cola_urgencias.get()
            print(f" Atendiendo paciente con URGENCIA: {paciente.nombre}")
        elif not self.cola_normal.empty():
            paciente = self.cola_normal.get()
            print(f" Atendiendo paciente normal: {paciente.nombre}")
        else:
            print(" No hay pacientes en espera")
            return None
        
        paciente.marcar_atencion()
        self.pacientes_atendidos.append(paciente)
        
        # Simular tiempo de atención
        tiempo_atencion = random.randint(5, 15)
        print(f"⏱ Tiempo estimado de atención: {tiempo_atencion} minutos")
        
        return paciente
    
    def ver_siguiente_paciente(self):
        """Muestra quién es el siguiente paciente sin atenderlo"""
        if not self.cola_urgencias.empty():
            paciente = self.cola_urgencias.queue[0]
            print(f" Siguiente paciente con URGENCIA: {paciente}")
        elif not self.cola_normal.empty():
            paciente = self.cola_normal.queue[0]
            print(f" Siguiente paciente normal: {paciente}")
        else:
            print(" No hay pacientes en espera")
    
    def mostrar_cola_espera(self):
        """Muestra todos los pacientes en espera"""
        print("\n" + "="*60)
        print(f" COLA DE ESPERA - {self.nombre_clinica}")
        print("="*60)
        
        # Mostrar urgencias primero
        if not self.cola_urgencias.empty():
            print("\n PACIENTES CON URGENCIA:")
            for i, paciente in enumerate(list(self.cola_urgencias.queue), 1):
                tiempo_espera = paciente.tiempo_espera()
                print(f"  {i}. {paciente} | Esperando: {tiempo_espera}")
        
        # Mostrar pacientes normales
        if not self.cola_normal.empty():
            print("\n PACIENTES NORMALES:")
            for i, paciente in enumerate(list(self.cola_normal.queue), 1):
                tiempo_espera = paciente.tiempo_espera()
                print(f"  {i}. {paciente} | Esperando: {tiempo_espera}")
        
        if self.cola_urgencias.empty() and self.cola_normal.empty():
            print("\n No hay pacientes en espera")
        
        print("="*60)
    
    def paciente_abandona(self, tipo_cola, posicion):
        """Permite que un paciente abandone la cola"""
        if tipo_cola == "urgencia":
            if self.cola_urgencias.qsize() >= posicion:
                temp_lista = list(self.cola_urgencias.queue)
                paciente = temp_lista.pop(posicion - 1)
                
                # Reconstruir la cola sin el paciente
                while not self.cola_urgencias.empty():
                    self.cola_urgencias.get()
                
                for p in temp_lista:
                    self.cola_urgencias.put(p)
                
                self.pacientes_abandonaron.append(paciente)
                print(f" Paciente abandonó (urgencia): {paciente.nombre}")
                return True
        else:
            if self.cola_normal.qsize() >= posicion:
                temp_lista = list(self.cola_normal.queue)
                paciente = temp_lista.pop(posicion - 1)
                
                # Reconstruir la cola sin el paciente
                while not self.cola_normal.empty():
                    self.cola_normal.get()
                
                for p in temp_lista:
                    self.cola_normal.put(p)
                
                self.pacientes_abandonaron.append(paciente)
                print(f" Paciente abandonó (normal): {paciente.nombre}")
                return True
        
        print(" Posición inválida o cola vacía")
        return False
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas del sistema"""
        print("\n" + "="*50)
        print(" ESTADÍSTICAS DEL SISTEMA")
        print("="*50)
        
        total_espera = self.cola_urgencias.qsize() + self.cola_normal.qsize()
        print(f" Pacientes en espera: {total_espera}")
        print(f"   - Urgencias: {self.cola_urgencias.qsize()}")
        print(f"   - Normales: {self.cola_normal.qsize()}")
        
        print(f" Pacientes atendidos hoy: {len(self.pacientes_atendidos)}")
        print(f" Pacientes que abandonaron: {len(self.pacientes_abandonaron)}")
        
        if self.pacientes_atendidos:
            tiempo_promedio = sum(p.tiempo_espera().total_seconds() / 60 
                                for p in self.pacientes_atendidos) / len(self.pacientes_atendidos)
            print(f"⏱ Tiempo promedio de espera: {tiempo_promedio:.1f} minutos")
        
        print("="*50)
    
    def simular_dia_trabajo(self):
        """Simula un día completo de trabajo en la clínica"""
        print(" Iniciando simulación del día de trabajo...")
        
        # Registrar algunos pacientes de ejemplo
        pacientes_ejemplo = [
            ("Juan Pérez", 35, "Dolor de cabeza", False),
            ("María García", 28, "Fractura", True),
            ("Carlos López", 45, "Chequeo anual", False),
            ("Ana Martínez", 22, "Dolor abdominal agudo", True),
            ("Roberto Díaz", 60, "Presión alta", False),
            ("Laura Sánchez", 30, "Herida profunda", True),
        ]
        
        for nombre, edad, motivo, urgencia in pacientes_ejemplo:
            self.registrar_paciente(nombre, edad, motivo, urgencia)
            time.sleep(0.5)  # Simular tiempo entre llegadas
        
        print("\n Pacientes registrados. Iniciando atención...")
        self.mostrar_cola_espera()
        
        # Atender a algunos pacientes
        for _ in range(4):
            self.atender_siguiente_paciente()
            time.sleep(1)
            self.ver_siguiente_paciente()
            time.sleep(0.5)
        
        self.mostrar_estadisticas()

def menu_principal():
    """Función principal con menú interactivo"""
    sistema = SistemaGestionTurnos("Clínica Salud Integral")
    
    while True:
        print("\n" + "="*60)
        print(" SISTEMA DE GESTIÓN DE TURNOS MÉDICOS")
        print("="*60)
        print("1.  Registrar nuevo paciente")
        print("2.  Atender siguiente paciente")
        print("3.  Ver siguiente paciente")
        print("4.  Mostrar cola de espera")
        print("5.  Paciente abandona")
        print("6.  Ver estadísticas")
        print("7.  Simular día de trabajo")
        print("8.  Salir")
        print("="*60)
        
        try:
            opcion = int(input("Seleccione una opción (1-8): "))
            
            if opcion == 1:
                print("\n REGISTRO DE NUEVO PACIENTE")
                nombre = input("Nombre del paciente: ")
                edad = int(input("Edad: "))
                motivo = input("Motivo de consulta: ")
                urgencia = input("¿Es urgencia? (s/n): ").lower() == 's'
                
                sistema.registrar_paciente(nombre, edad, motivo, urgencia)
                
            elif opcion == 2:
                print("\n ATENDIENDO SIGUIENTE PACIENTE")
                sistema.atender_siguiente_paciente()
                
            elif opcion == 3:
                print("\n SIGUIENTE PACIENTE EN ESPERA")
                sistema.ver_siguiente_paciente()
                
            elif opcion == 4:
                sistema.mostrar_cola_espera()
                
            elif opcion == 5:
                print("\n PACIENTE ABANDONA")
                tipo = input("Tipo de cola (urgencia/normal): ").lower()
                if tipo in ["urgencia", "normal"]:
                    posicion = int(input("Posición en la cola: "))
                    sistema.paciente_abandona(tipo, posicion)
                else:
                    print(" Tipo de cola inválido")
                    
            elif opcion == 6:
                sistema.mostrar_estadisticas()
                
            elif opcion == 7:
                print("\n SIMULACIÓN DEL DÍA")
                sistema.simular_dia_trabajo()
                
            elif opcion == 8:
                print("\n ¡Gracias por usar el sistema! ¡Hasta pronto!")
                break
                
            else:
                print(" Opción no válida. Intente de nuevo.")
                
        except ValueError:
            print(" Error: Ingrese un número válido.")
        except KeyboardInterrupt:
            print("\n\n Programa interrumpido. ¡Hasta pronto!")
            break

if __name__ == "__main__":
    print(" BIENVENIDO AL SISTEMA DE GESTIÓN DE TURNOS MÉDICOS")
    print("Este sistema utiliza estructuras de datos lineales (colas) para")
    print("gestionar eficientemente la atención de pacientes en una clínica.")
    menu_principal()
