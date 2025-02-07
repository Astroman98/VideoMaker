import asyncio
import multiprocessing
from main import main as render_spanish
from englishoption import main as render_english

def run_spanish():
    """Wrapper para ejecutar el renderizado en español"""
    asyncio.run(render_spanish())

def run_english():
    """Wrapper para ejecutar el renderizado en inglés"""
    asyncio.run(render_english())

if __name__ == "__main__":
    print("Iniciando renderizado paralelo verdadero...")
    
    # Crear procesos separados para cada renderizado
    process_spanish = multiprocessing.Process(target=run_spanish)
    process_english = multiprocessing.Process(target=run_english)
    
    # Iniciar ambos procesos
    process_spanish.start()
    process_english.start()
    
    # Esperar a que ambos procesos terminen
    process_spanish.join()
    process_english.join()
    
    print("¡Renderizado completado! Ambos videos han sido generados en paralelo.")