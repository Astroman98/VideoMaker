import asyncio
import re
import os
import numpy as np
import textwrap
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy import concatenate_audioclips
from moviepy.audio.AudioClip import AudioArrayClip
from generate_titleeng import generate_title_video
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
    partes = []
    texto_actual = texto.strip()

    # Filtrar partes que solo contienen puntuación o están vacías
    def is_valid_sentence(text):
        # Eliminar espacios en blanco
        text = text.strip()
        # Verificar si hay al menos un carácter que no sea puntuación
        return any(c.isalnum() for c in text)
    
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

''' def split_sentences(texto):
    """
    Separa el texto en oraciones usando como delimitadores:
      - Un signo de interrogación (?)
      - Un punto (.) que no forme parte de una elipsis ("...").
    """
    return re.split(r'(?<=[?]|(?<!\.)\.(?!\.)(?!"))\s+', texto.strip())
 '''


import os
import asyncio
from xml.sax.saxutils import escape
import azure.cognitiveservices.speech as speechsdk


def _guess_lang_from_voice(voice_name: str) -> str:
    parts = voice_name.split("-")
    return "-".join(parts[:2]) if len(parts) >= 2 else "en-US"


import asyncio


def _azure_tts_single(sentences: list, output_file: str, voice: str, rate: str) -> list:
    """
    Genera un único audio con todas las oraciones en una sola llamada a Azure TTS.
    Usa SSML bookmarks para obtener el timestamp exacto de inicio/fin de cada oración.
    Retorna lista de (start_sec, end_sec) por oración.
    """
    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION")

    if not key or not region:
        raise RuntimeError("Faltan AZURE_SPEECH_KEY o AZURE_SPEECH_REGION en el entorno.")

    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.speech_synthesis_voice_name = voice
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Riff48Khz16BitMonoPcm
    )

    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    lang = _guess_lang_from_voice(voice)

    # Insertar un bookmark después de cada oración (excepto la última)
    # El bookmark dispara cuando la oración anterior termina de sintetizarse
    ssml_parts = []
    for i, sentence in enumerate(sentences):
        ssml_parts.append(escape(sentence))
        if i < len(sentences) - 1:
            ssml_parts.append(f'<bookmark mark="sent_{i}"/>')

    ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{lang}">
  <voice name="{voice}">
    <prosody rate="{rate}">{" ".join(ssml_parts)}</prosody>
  </voice>
</speak>""".strip()

    bookmark_offsets = {}

    def on_bookmark(evt):
        bookmark_offsets[evt.text] = evt.audio_offset / 10_000_000

    synthesizer.bookmark_reached.connect(on_bookmark)

    result = synthesizer.speak_ssml_async(ssml).get()
    del synthesizer

    if result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        msg = f"TTS cancelado: {details.reason}"
        if details.error_details:
            msg += f" | {details.error_details}"
        raise RuntimeError(msg)

    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        raise RuntimeError(f"TTS falló: {result.reason}")

    total_duration = result.audio_duration.total_seconds()

    # Calcular (start, end) para cada oración
    # sent_i bookmark marca el FIN de la oración i → es el INICIO de la oración i+1
    timestamps = []
    for i in range(len(sentences)):
        start = bookmark_offsets.get(f"sent_{i - 1}", 0.0) if i > 0 else 0.0
        end = bookmark_offsets.get(f"sent_{i}", total_duration)
        timestamps.append((start, end))

    return timestamps


def create_scrolling_text_clip(sentence, res, duration, font_size=60, scroll_speed=1.8):
    """
    Crea un TextClip con efecto de scroll si el texto supera las dos líneas,
    asegurando que todo el texto sea visible durante el scroll.
    """
    # Primero creamos el TextClip para medir su altura
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
    
    # Calculamos la altura de dos líneas y la altura total del texto
    line_height = font_size * 1.1  # Aproximación del alto de línea con espaciado, anteriormente era 1.2
    two_lines_height = line_height * 2
    text_height = temp_clip.h
    
    # Solo aplicamos scroll si el texto supera las dos líneas
    if text_height > two_lines_height:
        # Creamos el clip de texto completo
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
        
        # Calculamos la distancia total de scroll necesaria
        scroll_distance = text_height - two_lines_height
        
        def scroll_position(t):
            # Esperar 1 segundo antes de comenzar el scroll
            if t < 1.8:
                return 0
            # Usar el tiempo restante para el scroll
            remaining_time = duration - 1.8
            # Dejar 0.3s al final
            scroll_time = remaining_time - 0.3
            # Calcular la posición del scroll con velocidad ajustada
            progress = min(1, ((t - 1.8) / scroll_time) * scroll_speed)
            # Asegurarnos de que el scroll llegue hasta el final del texto
            return progress * scroll_distance
        
        # Posicionar el texto dentro del contenedor
        txt_clip = (txt_clip
                   # Comenzar con el texto en la parte superior del contenedor
                   .with_position(lambda t: ('center', -scroll_position(t)))
                   .with_duration(duration))
        
        # Crear un contenedor del tamaño de dos líneas
        container = CompositeVideoClip(
            [txt_clip],
            size=(res[0] - 95, int(two_lines_height))
        ).with_duration(duration)
        
        # Posicionar el contenedor más arriba en el video
        bottom_margin = 90  # Ajustar este valor según sea necesario
        final_clip = container.with_position(('center', res[1] - bottom_margin - two_lines_height))
        
    else:
        # Para textos de dos líneas o menos, simplemente centramos sin scroll
        # También ajustamos la posición vertical para mantener consistencia
        bottom_margin = 90
        text_height = temp_clip.h
        padding_vertical = 60  # Agregar padding adicional
        final_clip = temp_clip.with_position(
            ('center', res[1] - bottom_margin - text_height - padding_vertical)
        )
    
    return final_clip.with_duration(duration)



def solicitar_nombre_transicion():
    """
    Solicita al usuario el nombre del archivo de transición a utilizar.
    """
    if 'ENG_TRANSICION' in os.environ:
        return os.environ['ENG_TRANSICION']
    
    print("\n--- TRANSITION CONFIGURATION ---")
    print("Available transition files in 'video' folder:")
    
    # Listar los archivos de transición disponibles
    archivos_transicion = [f for f in os.listdir("video") if f.startswith("transition_") and f.endswith(".mp4")]
    
    if not archivos_transicion:
        print("No transition files found in the 'video' folder.")
        return "transition_1.mp4"  # valor por defecto
    
    for i, archivo in enumerate(archivos_transicion, 1):
        print(f"{i}. {archivo}")
    
    seleccion = input("\nSelect the transition number to use (or press Enter to use transition_1.mp4): ")
    
    if not seleccion:
        return "transition_1.mp4"
    
    try:
        indice = int(seleccion) - 1
        if 0 <= indice < len(archivos_transicion):
            print(f"Using transition: {archivos_transicion[indice]}")
            return archivos_transicion[indice]
        else:
            print("Selection out of range. Using transition_1.mp4")
            return "transition_1.mp4"
    except ValueError:
        print("Invalid input. Using transition_1.mp4")
        return "transition_1.mp4"

def solicitar_nombre_background():
    """
    Solicita al usuario el nombre del archivo de fondo a utilizar.
    """
    if 'ENG_BACKGROUND' in os.environ:
        return os.environ['ENG_BACKGROUND']
    print("\n--- BACKGROUND VIDEO CONFIGURATION ---")
    print("Available background files in 'video' folder:")
    
    # Listar los archivos de video en la carpeta 'video'
    archivos_background = [f for f in os.listdir("video") if f.endswith((".mp4", ".avi", ".mov", ".mkv")) 
                          and not (f.startswith("transition_") or f.startswith("intro") or f.startswith("transicion_"))]
    
    if not archivos_background:
        print("No background video files found in the 'video' folder.")
        return "Gameplay1.mp4"  # valor por defecto
    
    for i, archivo in enumerate(archivos_background, 1):
        print(f"{i}. {archivo}")
    
    seleccion = input("\nSelect the background video number to use (or press Enter to use Gameplay1.mp4): ")
    
    if not seleccion:
        return "Gameplay1.mp4"
    
    try:
        indice = int(seleccion) - 1
        if 0 <= indice < len(archivos_background):
            print(f"Using background video: {archivos_background[indice]}")
            return archivos_background[indice]
        else:
            print("Selection out of range. Using Gameplay1.mp4")
            return "Gameplay1.mp4"
    except ValueError:
        print("Invalid input. Using Gameplay1.mp4")
        return "Gameplay1.mp4"



async def process_segment(segment_text, res, seg_index):
    """
    Procesa un segmento generando un único audio para todas las oraciones.
    Usa SSML bookmarks para sincronizar subtítulos con precisión.
    """
    sentences = split_sentences(segment_text)
    print(f"Segmento {seg_index} – oraciones:")
    for i, s in enumerate(sentences, 1):
        print(f"  {i}: {s}")

    os.makedirs("audio_eng", exist_ok=True)
    audio_file = f"audio_eng/seg{seg_index}.wav"

    timestamps = await asyncio.to_thread(
        _azure_tts_single, sentences, audio_file, "en-US-ChristopherNeural", "+5%"
    )
    print(f"Audio guardado: {audio_file}")

    full_audio = AudioFileClip(audio_file)
    total_duration = full_audio.duration

    # Ajustar el fin de la última oración a la duración real del audio
    last_start, _ = timestamps[-1]
    timestamps[-1] = (last_start, total_duration)

    text_clips = []
    for sentence, (start, end) in zip(sentences, timestamps):
        d = max(end - start, 0.1)
        txt_clip = create_scrolling_text_clip(
            sentence=sentence,
            res=res,
            duration=d
        ).with_start(start)
        text_clips.append(txt_clip)

    return text_clips, full_audio, total_duration





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
    # Solicitar la transición y el fondo a utilizar
    nombre_transicion = solicitar_nombre_transicion()
    nombre_background = solicitar_nombre_background()
    
    target_resolution = (1920, 1080)
    # Abrir el video de fondo primero para obtener la resolución base
    main_bg = VideoFileClip(f"video/{nombre_background}").resized(target_resolution)
    res = target_resolution  # Usar la resolución estándar en lugar de la del video
    
    # Definir silence_duration al inicio
    silence_duration = 2

    #AQUI VA EL TÍTULO. PUEDES CAMBIARLO A TU GUSTO
    await generate_title_video(
    text=""" What's your worst "friend betrayed you" story? """,
    resolution=res
    )
    
    # Abrir el video de fondo de forma continua (gameplay1.mp4)
    #main_bg = VideoFileClip("video/gameplay1.mp4")
    #res = (main_bg.w, main_bg.h)
    
    # Texto completo con separadores de segmento (líneas con '---')
    texto = (

""" 



My friend was dating a girl who I could tell just didn't like me, but at least we were civil to one another, until the camping trip on the May 24 holiday weekend. She was adamant about keeping our alcohol separate, that was fine. I had my beer, they had their Mike's Hard Lemonades, fine. Then I got up early on the first morning and made pancakes for everyone. Why? Because that's just how I roll. When the campers rolled out of their tents to the smell of apple cinnamon pancakes and campfire coffee, she was the only one to flip out. I'd gone into her cooler and used her margarine. My buddy just looked pained and tried to keep the peace as I tossed her a couple of bucks and apologized. Her reaction was to grab a lock from his gym bag and lock "their tent" with "their booze" and "their food". Later, he came to me and asked if he could borrow the car, so that they could run into town, get some personal items and have some words about being a bit easier with the other campers. I said okay, and handed him the keys. When they returned hours later, the tank was empty, and the field kitchen (a wooden box with straps called a wannigan with plates, cutlery, pots and pans, etc.) was missing from the back of the station wagon. We searched the camp, nothing. It was my dad's and had been handed down in the family for generations. I drove off to fill the tank and buy a new tub of margarine, and was halfway down the country road when I saw the wannigan on the side of the road, smashed in the ditch. There were marks along the back panels beside the flattened down seats where one of them had clearly pushed it out the back of the moving car.

After piling it all, stunned, piece by piece back into the wagon, I gassed up and drove back, then packed up. Not a word was said by anyone, until I tore up the camping permit and peeled out with their shouts behind me in the dust.

Never spoke to either one of them again.
---

I had one "friend" who would steal from friends pretty regularly.

One time I had a small social gathering (about 6 or 7 people) and my new smartphone went missing. This guy helps me look for the phone in my house for over an hour. Later on, I see my phone in his room on his desk. I just took it back. No words were exchanged. I just stopped talking to him altogether after that.

Later, he was at a mutual friend's party. Her 80GB iPod goes missing. Some other friends and I were suspicious that it was him, so the next day we called up the local pawn shop and described the iPod. The pawnshop guy said he got one that day. Sure enough, it was under his name. The pawnshop owner offered to call the cops, but we declined. We approached him and told him we knew. He tried to deny it, but we managed to shame him into admitting it.

Screw people who steal from friends.




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
    title_video = VideoFileClip("title(eng).mp4").resized(res).subclipped(0, -0.05)  # Quitar los últimos 0.05 segundos
    
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
    


    

    
    '''
    # Antes del write_videofile, redimensiona el video (SOLO APLICA CUANDO HACES TESTEOS)
    final_video = final_video.resized(width=426, height=240)
    final_video.write_videofile(
    "testvideo_con_audio_y_subtitulos(eng).mp4",
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


    
        # Exportar el video final
    final_video.write_videofile(
        "video_con_audio_y_subtitulos(eng).mp4",
        #"Testvideo(eng).mp4",
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
    for file in os.listdir("audio_eng"):  # Cambiado de "audio" a "audio_eng"
        if file.endswith((".mp3", ".wav")):
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    os.remove(os.path.join("audio_eng", file))  # Cambiado aquí también
                    break
                except Exception as e:
                    if attempt == max_attempts - 1:
                        print(f"Error al eliminar archivo temporal {file}: {str(e)}")
                    else:
                        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())