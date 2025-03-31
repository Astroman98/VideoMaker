import asyncio
import re
import os
import numpy as np
import textwrap
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy import concatenate_audioclips
import edge_tts
from moviepy.audio.AudioClip import AudioArrayClip
from generate_title import generate_title_video
from moviepy import concatenate_videoclips
from moviepy.video.fx.CrossFadeIn import CrossFadeIn
from moviepy.video.fx.CrossFadeOut import CrossFadeOut
from moviepy.audio.fx.AudioFadeIn import AudioFadeIn
from moviepy.audio.fx.AudioFadeOut import AudioFadeOut
from moviepy import CompositeAudioClip
import random


def split_sentences(texto):
    """
    Separa el texto en oraciones sin dividir las comillas de cierre.
    """
        # Filtrar partes que solo contienen puntuación o están vacías
    def is_valid_sentence(text):
        # Eliminar espacios en blanco
        text = text.strip()
        # Verificar si hay al menos un carácter que no sea puntuación
        return any(c.isalnum() for c in text)
    
    partes = []
    texto_actual = texto.strip()
    
    while texto_actual:
        match_punto_comilla = texto_actual.find('."')
        match_punto_comilla2 = texto_actual.find('.”')
        match_punto_interrogacion = texto_actual.find('?"')
        match_punto_interrogacion2 = texto_actual.find('?”')
        match_exclamacion_comilla = texto_actual.find('!"')
        match_exclamacion_comilla2 = texto_actual.find('!”')
        match_punto_parentesis = texto_actual.find('.)')  # Nuevo: buscar exclamación con comillas
        match_interrogacion = texto_actual.find('? ')
        match_interrogacion_salto = texto_actual.find('?\n')
        match_punto = texto_actual.find('. ')
        match_punto_salto = texto_actual.find('.\n')
        match_dos_puntos = texto_actual.find(': ')
        match_dos_puntos_salto = texto_actual.find(':\n')
        match_exclamacion = texto_actual.find('! ')
        
        # Mejorada la búsqueda de tres puntos seguidos de mayúscula
        match_tres_puntos_mayuscula = -1

        # Buscar tanto los tres puntos normales como el carácter unicode
        index_normal = texto_actual.find('...')
        index_unicode = texto_actual.find('…')

        # Procesar puntos suspensivos normales (...)
        if index_normal != -1:
            if len(texto_actual) > index_normal + 3:  # +3 para los tres puntos
                resto_texto = texto_actual[index_normal + 3:].lstrip()
                if resto_texto and resto_texto[0].isupper():
                    match_tres_puntos_mayuscula = index_normal + 3

        # Procesar punto suspensivo unicode (…)
        if index_unicode != -1:
            if len(texto_actual) > index_unicode + 1:  # +1 para el carácter unicode
                resto_texto = texto_actual[index_unicode + 1:].lstrip()
                if resto_texto and resto_texto[0].isupper():
                    # Si encontramos ambos tipos, usar el que aparezca primero
                    if match_tres_puntos_mayuscula == -1 or index_unicode < index_normal:
                        match_tres_puntos_mayuscula = index_unicode + 1
        
        indices = []
        if match_punto_comilla != -1:
            indices.append(match_punto_comilla + 2)
        if match_punto_comilla2 != -1:
            indices.append(match_punto_comilla2 + 2)
        if match_punto_interrogacion != -1:
            indices.append(match_punto_interrogacion + 2)
        if match_punto_interrogacion2 != -1:
            indices.append(match_punto_interrogacion2 + 2)
        if match_punto_parentesis != -1:
            indices.append(match_punto_parentesis + 2)
        if match_exclamacion_comilla != -1:  # Nuevo: agregar índice para !
            indices.append(match_exclamacion_comilla + 2)
        if match_exclamacion_comilla2 != -1:  # Nuevo: agregar índice para !
            indices.append(match_exclamacion_comilla2 + 2)
        elif match_interrogacion != -1:
            indices.append(match_interrogacion + 1)
        if match_punto != -1:
            # Buscar todos los puntos en el texto
            posiciones_puntos = []
            pos = 0
            while True:
                pos = texto_actual.find('. ', pos)
                if pos == -1:
                    break
                posiciones_puntos.append(pos)
                pos += 1

            
            # Verificar cada punto
            for pos in posiciones_puntos:
                
                # Verificar si este punto es parte de puntos suspensivos
                is_part_of_ellipsis = False
                if pos >= 2:
                    prev_chars = texto_actual[pos-2:pos]
                    if prev_chars == '..':
                        is_part_of_ellipsis = True
                
                if not is_part_of_ellipsis:

                    indices.append(pos + 1)

        if match_punto_salto != -1:
            if not texto_actual[match_punto_salto-2:match_punto_salto+1] == '...':
                indices.append(match_punto_salto + 1)
        if match_interrogacion_salto != -1:
            indices.append(match_interrogacion_salto + 1)
        if match_dos_puntos != -1:
            indices.append(match_dos_puntos + 2)
        if match_dos_puntos_salto != -1:
            indices.append(match_dos_puntos_salto + 2)
        if match_exclamacion != -1:
            indices.append(match_exclamacion + 2)
        if match_tres_puntos_mayuscula != -1:
            indices.append(match_tres_puntos_mayuscula + 1)
        



        if not indices:
            if texto_actual:
                partes.append(texto_actual)
            break


            
        primer_match = min(indices)
        partes.append(texto_actual[:primer_match])
        texto_actual = texto_actual[primer_match:].strip()


    return [p for p in partes if p and is_valid_sentence(p)]


'''
def split_sentences(texto):
    """
    Separa el texto en oraciones sin dividir las comillas de cierre.
    """
    partes = []
    texto_actual = texto.strip()
    
    while texto_actual:
        match_punto_comilla = texto_actual.find('."')
        match_punto_interrogacion = texto_actual.find('?"')
        match_interrogacion = texto_actual.find('?')
        match_punto = texto_actual.find('. ')
        match_punto_salto = texto_actual.find('.\n')
        match_dos_puntos = texto_actual.find(': ')
        match_dos_puntos_salto = texto_actual.find(':\n')
        match_exclamacion = texto_actual.find('! ')
        
        # Mejorada la búsqueda de tres puntos seguidos de mayúscula
        match_tres_puntos_mayuscula = -1
        indice = texto_actual.find('…')  # Buscar el carácter unicode de puntos suspensivos
        if indice == -1:  # Si no encuentra el carácter unicode, buscar tres puntos
            indice = texto_actual.find('...')
            
        if indice != -1 and len(texto_actual) > indice + 1:
            # Verificar si hay un espacio después de los puntos suspensivos
            siguiente_char = texto_actual[indice + 1] if indice + 1 < len(texto_actual) else ''
            if siguiente_char.isspace():
                # Buscar la siguiente palabra
                resto_texto = texto_actual[indice + 2:].lstrip()
                if resto_texto and resto_texto[0].isupper():
                    match_tres_puntos_mayuscula = indice + 1
        
        indices = []
        if match_punto_comilla != -1:
            indices.append(match_punto_comilla + 2)
        if match_punto_interrogacion != -1:
            indices.append(match_punto_interrogacion + 2)
        elif match_interrogacion != -1:
            indices.append(match_interrogacion + 1)
        if match_punto != -1:
            if not texto_actual[match_punto-2:match_punto+1] == '...':
                indices.append(match_punto + 1)
        if match_punto_salto != -1:
            if not texto_actual[match_punto_salto-2:match_punto_salto+1] == '...':
                indices.append(match_punto_salto + 1)
        if match_dos_puntos != -1:
            indices.append(match_dos_puntos + 2)
        if match_dos_puntos_salto != -1:
            indices.append(match_dos_puntos_salto + 2)
        if match_exclamacion != -1:
            indices.append(match_exclamacion + 2)
        if match_tres_puntos_mayuscula != -1:
            indices.append(match_tres_puntos_mayuscula + 1)
        
        if not indices:
            if texto_actual:
                partes.append(texto_actual)
            break
            
        primer_match = min(indices)
        partes.append(texto_actual[:primer_match])
        texto_actual = texto_actual[primer_match:].strip()
    
    return [p for p in partes if p]

'''
    

'''
def split_sentences(texto):
    
    Separa el texto en oraciones usando como delimitadores:
      - Un signo de interrogación (?)
      - Un punto (.) que no forme parte de una elipsis ("...").
    
    return re.split(r'(?<=[?]|(?<!\.)\.(?!\.)(?!"))\s+', texto.strip())

'''

import os
import subprocess
import asyncio
import tempfile

def generate_audio_with_edge_tts(text, output_file, voice="es-US-AlonsoNeural", rate="+10%"):
    """
    Genera audio usando edge-tts como herramienta de línea de comandos a través de subprocess.
    Esta es una función sincrónica que emula exactamente el método del primer código.
    
    Args:
        text: El texto a convertir en audio
        output_file: Ruta del archivo de salida
        voice: Voz a utilizar
        rate: Velocidad de habla
    """
    # Crear un archivo temporal para el texto
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(text)
        text_file_path = temp_file.name
    
    try:
        # Configurar el comando exactamente igual al primer código
        command = [
            "edge-tts",
            "--file", text_file_path,
            "--write-media", output_file,
            "--rate", rate,
            "--voice", voice
        ]
        
        # Ejecutar el comando
        subprocess.run(command, check=True)
        print(f"Audio generado: {output_file}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar edge-tts: {e}")
        return False
        
    finally:
        # Limpiar el archivo temporal
        try:
            os.unlink(text_file_path)
        except Exception as e:
            print(f"Error al eliminar archivo temporal: {e}")

async def generate_audio_for_sentence(sentence, output_file, voz="es-US-AlonsoNeural"):
    """
    Versión asincrónica que ejecuta la función sincrónica en un hilo separado.
    """
    return await asyncio.to_thread(
        generate_audio_with_edge_tts, 
        sentence, 
        output_file, 
        voz, 
        "+10%"
    )

async def generate_all_audios(sentences, seg_index):
    """
    Genera un audio para cada oración y devuelve una lista de rutas a los archivos generados.
    """
    audio_files = []
    os.makedirs("audio_esp", exist_ok=True)
    
    for i, sentence in enumerate(sentences):
        file_path = f"audio_esp/seg{seg_index}_sentence_{i}.mp3"
        success = await generate_audio_for_sentence(sentence, file_path)
        
        if success and os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            audio_files.append(file_path)
            print(f"Archivo de audio {i+1}/{len(sentences)} creado correctamente")
        else:
            print(f"ADVERTENCIA: Error al generar audio para la oración {i+1}")
        
        # Pequeña pausa entre generaciones de audio
        await asyncio.sleep(0.5)
    
    return audio_files

def generate_subtitle_entries(sentences, durations):
    """
    A partir de las duraciones reales de cada audio, genera una lista de tuplas:
      (inicio, fin, oración)
    para saber cuándo deben aparecer los subtítulos dentro del segmento.
    """
    entries = []
    start = 0
    for sentence, d in zip(sentences, durations):
        entries.append((start, start + d, sentence))
        start += d
    return entries



def solicitar_nombre_transicion():
    """
    Solicita al usuario el nombre del archivo de transición a utilizar.
    """
    # Verificar si ya tenemos un valor predefinido
    if 'ESP_TRANSICION' in os.environ:
        return os.environ['ESP_TRANSICION']
    
    # Si no hay valor predefinido, continuar con la solicitud normal
    print("\n--- CONFIGURACIÓN DE TRANSICIÓN ---")
    
    # Listar los archivos de transición disponibles
    archivos_transicion = [f for f in os.listdir("video") if f.startswith("transicion_") and f.endswith(".mp4")]
    
    if not archivos_transicion:
        print("No se encontraron archivos de transición en la carpeta 'video'.")
        return "transicion_1.mp4"  # valor por defecto
    
    for i, archivo in enumerate(archivos_transicion, 1):
        print(f"{i}. {archivo}")
    
    seleccion = input("\nSeleccione el número de la transición a utilizar (o presione Enter para usar transicion_1.mp4): ")
    
    if not seleccion:
        return "transicion_1.mp4"
    
    try:
        indice = int(seleccion) - 1
        if 0 <= indice < len(archivos_transicion):
            print(f"Se utilizará la transición: {archivos_transicion[indice]}")
            return archivos_transicion[indice]
        else:
            print("Selección fuera de rango. Se utilizará transicion_1.mp4")
            return "transicion_1.mp4"
    except ValueError:
        print("Entrada inválida. Se utilizará transicion_1.mp4")
        return "transicion_1.mp4"
    



def solicitar_nombre_background():
    """
    Solicita al usuario el nombre del archivo de fondo a utilizar.
    """
    # Verificar si ya tenemos un valor predefinido
    if 'ESP_BACKGROUND' in os.environ:
        return os.environ['ESP_BACKGROUND']
    
    # Si no hay valor predefinido, continuar con la solicitud normal
    print("\n--- CONFIGURACIÓN DE VIDEO DE FONDO ---")
    
    # Listar los archivos de video en la carpeta 'video'
    archivos_background = [f for f in os.listdir("video") if f.endswith((".mp4", ".avi", ".mov", ".mkv")) 
                          and not (f.startswith("transicion_") or f.startswith("intro") or f.startswith("transition_"))]
    
    if not archivos_background:
        print("No se encontraron archivos de fondo en la carpeta 'video'.")
        return "full_background_sh2.mp4"  # valor por defecto
    
    for i, archivo in enumerate(archivos_background, 1):
        print(f"{i}. {archivo}")
    
    seleccion = input("\nSeleccione el número del video de fondo a utilizar (o presione Enter para usar full_background_sh2.mp4): ")
    
    if not seleccion:
        return "full_background_sh2.mp4"
    
    try:
        indice = int(seleccion) - 1
        if 0 <= indice < len(archivos_background):
            print(f"Se utilizará el video de fondo: {archivos_background[indice]}")
            return archivos_background[indice]
        else:
            print("Selección fuera de rango. Se utilizará full_background_sh2.mp4")
            return "full_background_sh2.mp4"
    except ValueError:
        print("Entrada inválida. Se utilizará full_background_sh2.mp4")
        return "full_background_sh2.mp4"



def create_scrolling_text_clip(sentence, res, duration, font_size=60, scroll_speed=1.8):
    """
    Crea un TextClip con efecto de scroll si el texto supera las dos líneas.
    """
    # Crear clip temporal para medir el texto
    temp_clip = TextClip(
        text=sentence,
        font_size=font_size,
        color='#cfcfcf',
        font="font/HKGrotesk-SemiBoldLegacy.ttf",
        text_align='center',
        method='caption',
        stroke_width=2,
        stroke_color='black',
        size=(res[0] - 100, None)
    )
    
    # Calculamos la altura de una línea y dos líneas
    line_height = font_size * 1.1  # Un poco más de espacio para evitar cortes
    two_lines_height = line_height * 2.2  # Altura máxima para dos líneas con padding
    text_height = temp_clip.h
    
    # Agregar un margen de tolerancia para dos líneas
    margin_tolerance = line_height * 0.1  # 30% de una línea como margen
    
    # Si el texto es de dos líneas o menos (con margen de tolerancia)
    if text_height <= (two_lines_height + margin_tolerance):
        # Crear clip estático sin scroll
        final_clip = TextClip(
            text=sentence,
            font_size=font_size,
            color='#cfcfcf',
            font="font/HKGrotesk-SemiBoldLegacy.ttf",
            text_align='center',
            method='caption',
            stroke_width=2,
            stroke_color='black',
            size=(res[0] - 100, None)
        ).with_duration(duration)
        
        # Posicionar en la parte inferior con margen fijo
        bottom_margin = 90
        final_clip = final_clip.with_position(('center', res[1] - bottom_margin - text_height))
    
    else:
        txt_clip = TextClip(
            text=sentence,
            font_size=font_size,
            color='#cfcfcf',
            font="font/HKGrotesk-SemiBoldLegacy.ttf",
            text_align='center',
            method='caption',
            stroke_width=2,
            stroke_color='black',
            size=(res[0] - 100, None)
        )
        
        # Ajustar el tamaño del contenedor para exactamente dos líneas
        exact_two_lines = line_height * 2  # Altura exacta para dos líneas sin padding extra
        scroll_distance = text_height - exact_two_lines
        
        def scroll_position(t):
            if t < 2:
                return 0
            remaining_time = duration - 2
            scroll_time = remaining_time - 0.3
            progress = min(1, ((t - 2) / scroll_time) * scroll_speed)
            return progress * scroll_distance
        
        txt_clip = (txt_clip
                   .with_position(lambda t: ('center', -scroll_position(t)))
                   .with_duration(duration))
        
        # Crear el contenedor con la altura exacta de dos líneas
        container = CompositeVideoClip(
            [txt_clip],
            size=(res[0] - 100, int(exact_two_lines)),  # Usar la altura exacta
            bg_color=None  # Asegurar que el fondo sea transparente
        ).with_duration(duration)
        
        # Ajustar el margen inferior
        bottom_margin = 100
        final_clip = container.with_position(('center', res[1] - bottom_margin - exact_two_lines))
    
    return final_clip.with_duration(duration)




async def process_segment(segment_text, res, seg_index):
    """
    Procesa un segmento con soporte para subtítulos con scroll enmascarado.
    """
    # Dividir en oraciones
    sentences = split_sentences(segment_text)
    print(f"Segmento {seg_index} – oraciones:")
    for i, s in enumerate(sentences, 1):
        print(f"  {i}: {s}")
    
    # Generar audios por oración
    audio_files = await generate_all_audios(sentences, seg_index)
    audio_clips = []
    durations = []
    
    for file in audio_files:
        clip = AudioFileClip(file)
        new_duration = clip.duration - 0.7 if clip.duration > 0.7 else clip.duration
        clip = clip.subclipped(0, new_duration)
        audio_clips.append(clip)
        durations.append(new_duration)
    
    seg_duration = sum(durations)
    
    # Crear TextClips para cada oración, con soporte para scroll enmascarado
    text_clips = []
    cumulative = 0
    for sentence, d in zip(sentences, durations):
        txt_clip = create_scrolling_text_clip(
            sentence=sentence,
            res=res,
            duration=d
        ).with_start(cumulative)
        
        text_clips.append(txt_clip)
        cumulative += d
    
    segment_audio = concatenate_audioclips(audio_clips)
    return text_clips, segment_audio, seg_duration


# En la función main(), antes de procesar los segmentos:
def get_random_video_segment(video_clip, needed_duration):
    """
    Selecciona un fragmento aleatorio del video que dure needed_duration segundos,
    asegurándose de que haya suficiente video restante.
    """
    # Dejar un margen de seguridad al final del video (por ejemplo, 10 segundos)
    margin = 10
    max_start_time = video_clip.duration - needed_duration - margin
    
    if max_start_time < 0:
        raise ValueError("El video de gameplay es más corto que la duración necesaria")
    
    # Elegir un punto de inicio aleatorio
    start_time = random.uniform(0, max_start_time)
    
    return start_time



async def main():
    # Solicitar la transición a utilizar
    nombre_transicion = solicitar_nombre_transicion()
    
    # Solicitar el video de fondo a utilizar
    nombre_background = solicitar_nombre_background()
    
    target_resolution = (1920, 1080)
    # Abrir el video de fondo primero para obtener la resolución base
    main_bg = VideoFileClip(f"video/{nombre_background}").resized(target_resolution)
    res = target_resolution  # Usar la resolución estándar en lugar de la del video

    
    # Definir silence_duration al inicio
    silence_duration = 2

    await generate_title_video(
    text="¿Cuál ha sido?",
    resolution=res
    )
    


    texto = (
       """ 

En un campamento de verano, un amigo y yo subimos a un techo de hojalata de un gran salón construido en la ladera de una colina empinada.

---

Hola.

 """
    )

    # Antes de procesar el texto con split_sentences
    texto = ' '.join(texto.split())
    

    # Separar el texto en segmentos usando el separador '---'
    segments = re.split(r'\n?\s*---+\s*\n?', texto.strip())
    print(f"Se encontraron {len(segments)} segmento(s).")
    
    # Lista para almacenar los resultados del procesamiento
    processed_segments = []
    total_duration = 0

    # Procesar todos los segmentos una sola vez
    for i, seg in enumerate(segments):
        if seg.strip():
            text_clips, seg_audio, seg_duration = await process_segment(seg, res, i)
            processed_segments.append((text_clips, seg_audio, seg_duration))
            total_duration += seg_duration

    # Agregar duración del silencio final
    total_duration_with_silence = total_duration + silence_duration
    
    # Obtener un punto de inicio aleatorio para el video de fondo
    start_time = get_random_video_segment(main_bg, total_duration_with_silence)
    
    # Recortar el video de fondo al segmento seleccionado
    main_bg = main_bg.subclipped(start_time, start_time + total_duration_with_silence)

    overlays = []       # Acumular todos los TextClips (subtítulos) con tiempos absolutos
    audio_segments = [] # Acumular los clips de audio de cada segmento (con tiempos absolutos)
    current_time = 0    # Tiempo acumulado en la línea de tiempo final


    
    # Usar los segmentos ya procesados
    for seg_index, (text_clips, seg_audio, seg_duration) in enumerate(processed_segments):
            # Ubicar cada TextClip en la línea de tiempo
            for clip in text_clips:
                overlays.append(clip.with_start(current_time + clip.start))
            
            # Ubicar el audio del segmento en la línea de tiempo
            audio_segments.append(seg_audio.with_start(current_time))
            current_time += seg_duration
            
            # Si no es el último segmento, insertar la transición
            if seg_index < len(segments) - 1:
                transition_clip = VideoFileClip(f"video/{nombre_transicion}").resized(res).with_start(current_time)

                # Crear copias de los efectos
                fadein_effect = CrossFadeIn(0.3).copy()
                fadeout_effect = CrossFadeOut(0.3).copy()

                # Aplicar efectos de fade
                transition_clip = fadein_effect.apply(transition_clip)
                transition_clip = fadeout_effect.apply(transition_clip)

                # Agregar clips a las listas
                overlays.append(transition_clip)
                if transition_clip.audio is not None:
                    audio_segments.append(transition_clip.audio.with_start(current_time))
                current_time += transition_clip.duration




    total_duration = current_time
    print(f"Duración total del video: {total_duration} s")

    # Crear silencio final de 2 segundos
    #silence_duration = 2
    fps = 44100  # Frecuencia de muestreo estándar
    samples = int(fps * silence_duration)
    silence_array = np.zeros((samples, 2), dtype=np.float32)
    end_silence_clip = AudioArrayClip(silence_array, fps=fps)

    # Calcular la duración total incluyendo el silencio
    total_duration_with_silence = total_duration + silence_duration

    # En main.py, cuando cargas el video del título
    title_video = VideoFileClip("title(esp).mp4").resized(res).subclipped(0, -0.05)  # Quitar los últimos 0.05 segundos
    
    # Crear el contenido principal (sin crear un nuevo CompositeVideoClip)
    final_bg = main_bg.subclipped(0, total_duration_with_silence)
    main_content = CompositeVideoClip(
        [final_bg] + overlays,
        size=res
    ).with_duration(total_duration_with_silence)

    background_music = AudioFileClip("music/silence.mp3")

    if background_music.duration > total_duration_with_silence:
        background_music = background_music.subclipped(0, total_duration_with_silence)

    audio_fadein = AudioFadeIn(1.5).copy()
    audio_fadeout = AudioFadeOut(0.8).copy()

    background_music = audio_fadein.apply(background_music)
    background_music = audio_fadeout.apply(background_music)

    #Aquí puedes configurar el volumen de la música de fondo
    from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
    # Reducir el volumen de la música de fondo
    # volume_effect = MultiplyVolume(0.005).copy() # 0.5% del volumen original
    volume_effect = MultiplyVolume(0.05).copy()
    background_music = volume_effect.apply(background_music)

    
    # Agregar el audio al contenido principal
    main_audio = concatenate_audioclips(audio_segments + [end_silence_clip])
    final_audio = CompositeAudioClip([main_audio, background_music])
    main_content = main_content.with_audio(final_audio)

    #Aplicar fade in y fade out al contenido principal
    from moviepy.video.fx.FadeIn import FadeIn
    from moviepy.video.fx.FadeOut import FadeOut
    fade_in1 = FadeIn(1.5).copy()
    fade_out1 = FadeOut(1.5).copy()
    main_content = fade_in1.apply(main_content)
    main_content = fade_out1.apply(main_content)

    # Concatenar el título con el contenido principal
    final_video = concatenate_videoclips(
        [title_video, main_content],
        method="compose"  # Usar compose en lugar del método por defecto
    )
    
    



        # Exportar el video final
    final_video.write_videofile(
        "video_con_audio_y_subtitulos(esp).mp4",
        fps=60,
        codec="libx264",
        bitrate="20000k",  # Aumentado para mejor calidad
        audio_codec="aac",
        audio_bitrate="320k",
        preset="medium",   # Balance entre velocidad y calidad
        threads=8,
        ffmpeg_params=[
            "-crf", "17",  # Menor valor = mejor calidad (rango 0-51)
            "-profile:v", "high",
            "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-tune", "film",  # Optimizado para contenido de video
            "-movflags", "+faststart",  # Mejora la reproducción en streaming
            "-bf", "2",  # Frames B para mejor compresión
            "-g", "30",  # GOP size
            "-keyint_min", "25",  # Mínimo intervalo entre keyframes
            "-sc_threshold", "40",  # Umbral de detección de cambios de escena
            "-b_strategy", "1",  # Estrategia de frames B
            "-qmin", "10",  # Calidad mínima
            "-qmax", "51",  # Calidad máxima
        ]
    )
    print("Video final guardado")

    '''
    # Antes del write_videofile, redimensiona el video (SOLO APLICA CUANDO HACES TESTEOS)
    final_video = final_video.resized(width=426, height=240)
    final_video.write_videofile(
    "testvideo_con_audio_y_subtitulos(esp).mp4",
    fps=24,
    codec="libx264",
    bitrate="500k",
    audio_codec="aac", 
    audio_bitrate="64k",
    preset="ultrafast",
    threads=8,
    ffmpeg_params=[
        "-crf", "35",
        "-profile:v", "baseline",
        "-level", "3.0",
        "-pix_fmt", "yuv420p",
        "-tune", "fastdecode",
        "-movflags", "+faststart",
        "-maxrate", "600k",
        "-bufsize", "1000k"
    ]
    )
    '''


# Cerrar todos los clips
    print("Cerrando clips de video...")
    main_bg.close()
    title_video.close()
    
    # Cerrar el audio principal y la música de fondo
    print("Cerrando clips de audio...")
    main_audio.close()
    background_music.close()
    final_audio.close()
    
    # Limpiar los segmentos procesados
    print("Cerrando segmentos procesados...")
    for _, seg_audio, _ in processed_segments:
        seg_audio.close()
    
    # Esperar un momento para asegurar que todos los archivos se hayan liberado
    await asyncio.sleep(1)
    
    # Limpiar archivos de audio temporales
    print("Limpiando archivos temporales...")
    for file in os.listdir("audio_esp"):  # Cambiado de "audio" a "audio_esp"
        if file.endswith(".mp3"):
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    os.remove(os.path.join("audio_esp", file))  # Cambiado aquí también
                    break
                except Exception as e:
                    if attempt == max_attempts - 1:
                        print(f"Error al eliminar archivo temporal {file}: {str(e)}")
                    else:
                        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())