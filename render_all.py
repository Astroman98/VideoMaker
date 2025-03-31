import asyncio
import multiprocessing
import os
import shutil
import time
from main import main as render_spanish, solicitar_nombre_transicion as solicitar_transicion_esp, solicitar_nombre_background as solicitar_background_esp
from generate_title import solicitar_intro_video as solicitar_intro_esp
from englishoption import main as render_english, solicitar_nombre_transicion as solicitar_transicion_eng, solicitar_nombre_background as solicitar_background_eng
from generate_titleeng import solicitar_intro_video as solicitar_intro_eng

# Variables globales para almacenar las selecciones
configuracion_espanol = {}
configuracion_ingles = {}

def obtener_configuraciones():
    """Solicita todas las configuraciones antes de iniciar el renderizado"""
    
    print("\n===== CONFIGURACIÓN PARA VERSIÓN EN ESPAÑOL =====")
    configuracion_espanol['transicion'] = solicitar_transicion_esp()
    configuracion_espanol['background'] = solicitar_background_esp()
    configuracion_espanol['intro'] = solicitar_intro_esp()
    
    print("\n===== CONFIGURATION FOR ENGLISH VERSION =====")
    configuracion_ingles['transicion'] = solicitar_transicion_eng()
    configuracion_ingles['background'] = solicitar_background_eng()
    configuracion_ingles['intro'] = solicitar_intro_eng()
    
    return configuracion_espanol, configuracion_ingles

def run_spanish(config):
    """Wrapper para ejecutar el renderizado en español con configuración predefinida"""
    try:
        os.makedirs("audio_esp", exist_ok=True)
        
        # Guardar la configuración en variables de entorno o archivos temporales
        os.environ['ESP_TRANSICION'] = config['transicion']
        os.environ['ESP_BACKGROUND'] = config['background']
        os.environ['ESP_INTRO'] = config['intro']
        
        asyncio.run(render_spanish())
    except Exception as e:
        print(f"Error en renderizado español: {str(e)}")
    finally:
        # Dar tiempo para que se liberen los archivos
        time.sleep(2)
        cleanup_directory("audio_esp")

def run_english(config):
    """Wrapper para ejecutar el renderizado en inglés con configuración predefinida"""
    try:
        os.makedirs("audio_eng", exist_ok=True)
        
        # Guardar la configuración en variables de entorno o archivos temporales
        os.environ['ENG_TRANSICION'] = config['transicion']
        os.environ['ENG_BACKGROUND'] = config['background']
        os.environ['ENG_INTRO'] = config['intro']
        
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
    # Primero obtenemos todas las configuraciones
    config_esp, config_eng = obtener_configuraciones()
    
    # Configurar procesos con mayor prioridad de recursos
    process_spanish = multiprocessing.Process(
        target=run_spanish,
        args=(config_esp,),
        name="Spanish_Render"
    )
    process_english = multiprocessing.Process(
        target=run_english,
        args=(config_eng,),
        name="English_Render"
    )
    
    # Iniciar procesos
    process_spanish.start()
    process_english.start()
    
    # Esperar finalización
    process_spanish.join()
    process_english.join()
    
    print("Renderizado completado")