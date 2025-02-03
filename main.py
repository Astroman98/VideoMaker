import asyncio
import re
import os
import numpy as np
import textwrap
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy import concatenate_audioclips
import edge_tts
from moviepy.audio.AudioClip import AudioArrayClip

def split_sentences(texto):
    """
    Separa el texto en oraciones usando como delimitadores:
      - Un signo de interrogación (?)
      - Un punto (.) que no forme parte de una elipsis ("...").
    """
    return re.split(r'(?<=[?]|(?<!\.)\.(?!\.))\s+', texto.strip())

async def generate_audio_for_sentence(sentence, output_file, voz="es-US-AlonsoNeural"):
    """
    Genera el audio TTS para una oración y lo guarda en output_file.
    Opciones de voz: es-US-AlonsoNeural, en-US-ChristopherNeural, etc.
    También se añade un ajuste de velocidad (rate).
    """
    # En este ejemplo se añade rate="+7%" para aumentar la velocidad
    comunicador = edge_tts.Communicate(text=sentence, voice=voz, rate="+7%")
    await comunicador.save(output_file)
    print(f"Audio guardado: {output_file}")

async def generate_all_audios(sentences, seg_index):
    """
    Genera un audio para cada oración y devuelve una lista de rutas a los archivos generados.
    Se nombran de forma que se distingan por segmento.
    """
    audio_files = []
    os.makedirs("audio", exist_ok=True)
    for i, sentence in enumerate(sentences):
        file_path = f"audio/seg{seg_index}_sentence_{i}.mp3"
        await generate_audio_for_sentence(sentence, file_path)
        audio_files.append(file_path)
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

def create_scrolling_text_clip(sentence, res, duration, font_size=40, scroll_speed=1.8):
    """
    Crea un TextClip con efecto de scroll si el texto supera las dos líneas,
    asegurando que todo el texto sea visible durante el scroll.
    """
    # Primero creamos el TextClip para medir su altura
    temp_clip = TextClip(
        text=sentence,
        font_size=font_size,
        color='#dbdbdb',
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
            color='#dbdbdb',
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
            if t < 1.2:
                return 0
            # Usar el tiempo restante para el scroll
            remaining_time = duration - 1.2
            # Dejar 0.3s al final
            scroll_time = remaining_time - 0.3
            # Calcular la posición del scroll con velocidad ajustada
            progress = min(1, ((t - 1) / scroll_time) * scroll_speed)
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
            size=(res[0] - 100, int(two_lines_height))
        ).with_duration(duration)
        
        # Posicionar el contenedor más arriba en el video
        bottom_margin = 80  # Ajustar este valor según sea necesario
        final_clip = container.with_position(('center', res[1] - bottom_margin - two_lines_height))
        
    else:
        # Para textos de dos líneas o menos, simplemente centramos sin scroll
        # También ajustamos la posición vertical para mantener consistencia
        bottom_margin = 80
        final_clip = temp_clip.with_position(('center', res[1] - bottom_margin - two_lines_height))
    
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
        new_duration = clip.duration - 0.5 if clip.duration > 0.5 else clip.duration
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


async def main():
    # Abrir el video de fondo de forma continua (gameplay1.mp4)
    main_bg = VideoFileClip("video/gameplay1.mp4")
    res = (main_bg.w, main_bg.h)
    
    # Texto completo con separadores de segmento (líneas con '---')
    texto = (
       """ Al menos la mitad de las cosas en el templo están tomadas directamente de los masones, incluyendo la vestimenta y los adornos que habia alrededor del templo, y los adornos de dios, etc que parecía maldito, poseido por el diablo? los apretones de manos y las contraseñas. Ah, y necesitas conocer estos apretones de manos y señales para entrar al cielo. Obvio? Aquí termina la historia 1.
        ---
        Tuve un accidente cuando tenía doce años que me lesionó la espalda... sentarme me dolía, etc. y estar parado tambien me dolia y mucho, tanto que tenia que tomar medicacion para la molestia. Logré convencera mi madre de que me dejara caminar durante los servicios de varias horas en la biblioteca/cuarto de conferencias en el piso de abajo, donde había un altavoz que transmitía todo lo que pasaba en el púlpito. Aquí termina la historia 2. """
    )
    
    # Separar el texto en segmentos usando el separador '---'
    segments = re.split(r'\n?\s*---+\s*\n?', texto.strip())
    print(f"Se encontraron {len(segments)} segmento(s).")
    
    overlays = []       # Acumular todos los TextClips (subtítulos) con tiempos absolutos
    audio_segments = [] # Acumular los clips de audio de cada segmento (con tiempos absolutos)
    current_time = 0    # Tiempo acumulado en la línea de tiempo final
    
    for seg_index, seg in enumerate(segments):
        if seg.strip():
            # Procesar el segmento: se obtiene la lista de TextClips (con tiempos relativos),
            # el audio concatenado del segmento y la duración total del segmento.
            text_clips, seg_audio, seg_duration = await process_segment(seg, res, seg_index)
            # Ubicar cada TextClip en la línea de tiempo (sumando current_time al inicio relativo)
            for clip in text_clips:
                overlays.append(clip.with_start(current_time + clip.start))
            # Ubicar el audio del segmento en la línea de tiempo
            audio_segments.append(seg_audio.with_start(current_time))
            current_time += seg_duration
            # Si no es el último segmento, insertar la transición (video de transicion_1)
            if seg_index < len(segments) - 1:
                transition_clip = VideoFileClip("video/transicion_1.mp4").resized(res).with_start(current_time)
                # Importar las clases de efecto (asegúrate de que tu instalación de MoviePy sea reciente)
                from moviepy.video.fx.CrossFadeIn import CrossFadeIn
                from moviepy.video.fx.CrossFadeOut import CrossFadeOut

                # Crear copias de los efectos con una duración de 0.5 segundos
                fadein_effect = CrossFadeIn(0.3).copy()
                fadeout_effect = CrossFadeOut(0.3).copy()

                # Aplicar el efecto de fade in y luego el de fade out
                transition_clip = fadein_effect.apply(transition_clip)
                transition_clip = fadeout_effect.apply(transition_clip)

                # Agregar el clip de transición (con sus efectos) a la lista de overlays
                overlays.append(transition_clip)
                # Si el clip de transición tiene audio, agregarlo a la lista de audios en la posición actual
                if transition_clip.audio is not None:
                    audio_segments.append(transition_clip.audio.with_start(current_time))
                current_time += transition_clip.duration

    
    total_duration = current_time
    print(f"Duración total del video: {total_duration} s")
    
    # Extraer el fondo continuo para cubrir toda la duración
    final_bg = main_bg.subclipped(0, total_duration).resized(res)
    
    # Crear el composite final: fondo continuo + overlays (subtítulos y transiciones)
    final_video = CompositeVideoClip([final_bg] + overlays, size=res).with_duration(total_duration)
    
    # Concatenar los audios (de segmentos y de transiciones) para formar la pista de audio final
    final_audio = concatenate_audioclips(audio_segments)
    final_video = final_video.with_audio(final_audio)
    
    # Exportar el video final
    final_video.write_videofile(
        "video_con_audio_y_subtitulos.mp4",
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )
    print("Video final guardado como: video_con_audio_y_subtitulos.mp4")
    main_bg.close()

if __name__ == "__main__":
    asyncio.run(main())
