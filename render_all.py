import asyncio
import multiprocessing
import os
import shutil
from main import main as render_spanish  # Importar la función main de main.py
from englishoption import main as render_english  # Importar la función main de englishoption.py

def run_spanish():
    """Wrapper para ejecutar el renderizado en español"""
    # Crear directorio temporal específico para español
    os.makedirs("audio_esp", exist_ok=True)
    
    try:
        asyncio.run(render_spanish())
    finally:
        # Limpiar directorio temporal
        if os.path.exists("audio_esp"):
            shutil.rmtree("audio_esp")

def run_english():
    """Wrapper para ejecutar el renderizado en inglés"""
    # Crear directorio temporal específico para inglés
    os.makedirs("audio_eng", exist_ok=True)
    
    try:
        asyncio.run(render_english())
    finally:
        # Limpiar directorio temporal
        if os.path.exists("audio_eng"):
            shutil.rmtree("audio_eng")

if __name__ == "__main__":
    print("Iniciando renderizado paralelo...")
    
    # Crear procesos separados
    process_spanish = multiprocessing.Process(target=run_spanish)
    process_english = multiprocessing.Process(target=run_english)
    
    # Iniciar procesos
    process_spanish.start()
    process_english.start()
    
    # Esperar finalización
    process_spanish.join()
    process_english.join()
    
    print("¡Renderizado completado!")