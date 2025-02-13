import asyncio
import multiprocessing
import os
import shutil
import time
from main import main as render_spanish
from englishoption import main as render_english

def run_spanish():
    """Wrapper para ejecutar el renderizado en español"""
    try:
        os.makedirs("audio_esp", exist_ok=True)
        asyncio.run(render_spanish())
    except Exception as e:
        print(f"Error en renderizado español: {str(e)}")
    finally:
        # Dar tiempo para que se liberen los archivos
        time.sleep(2)
        cleanup_directory("audio_esp")

def run_english():
    """Wrapper para ejecutar el renderizado en inglés"""
    try:
        os.makedirs("audio_eng", exist_ok=True)
        asyncio.run(render_english())
    except Exception as e:
        print(f"Error en renderizado inglés: {str(e)}")
    finally:
        time.sleep(2)
        cleanup_directory("audio_eng")

def cleanup_directory(directory):
    """Limpieza segura de directorios"""
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            for root, dirs, files in os.walk(directory, topdown=False):
                for name in files:
                    try:
                        os.unlink(os.path.join(root, name))
                    except:
                        continue
                for name in dirs:
                    try:
                        os.rmdir(os.path.join(root, name))
                    except:
                        continue
            if os.path.exists(directory):
                os.rmdir(directory)
            break
        except:
            time.sleep(1)

if __name__ == "__main__":
    # Configurar procesos con mayor prioridad de recursos
    process_spanish = multiprocessing.Process(
        target=run_spanish,
        name="Spanish_Render"
    )
    process_english = multiprocessing.Process(
        target=run_english,
        name="English_Render"
    )
    
    # Iniciar procesos
    process_spanish.start()
    process_english.start()
    
    # Esperar finalización
    process_spanish.join()
    process_english.join()
    
    print("Renderizado completado")