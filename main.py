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

async def process_segment(segment_text, res, seg_index):
    """
    Procesa un segmento (bloque de texto sin el separador '---'):
      - Separa el segmento en oraciones.
      - Genera el audio TTS para cada oración.
      - Carga cada audio, recorta 0.5 s del final y obtiene su duración.
      - Crea un TextClip por oración (con start relativo y duración correspondiente).
    Retorna una tupla:
      (lista de TextClips, audio concatenado del segmento, duración total del segmento)
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
    # Crear TextClips para cada oración, con tiempos relativos
    text_clips = []
    cumulative = 0
    for sentence, d in zip(sentences, durations):
        txt_clip = TextClip(
            text=sentence,
            font_size=24,
            color='white',
            font="font/arial.ttf",  # Ajusta la ruta si es necesario
            method='caption',
            size=(res[0] - 100, None)
        ).with_position(('center', res[1] - 100)).with_start(cumulative).with_duration(d)
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
       """Crecí como Testigo de Jehová y finalmente "me alejé" alrededor de los 14 años. 
En ese entonces no pensaba que fuera una secta, solo creía que estaban equivocados en su forma de ver las cosas... 
¿Será posible cambiar algo? 
No tenían respuestas para mis preguntas, y sabía por mi mamá que habían predicho el fin del mundo docenas de veces, y todas habían fallado. 

---
Así que exploré otras religiones, terminando en la de mi mejor amigo: los mormones (o llamados como la Iglesia de Jesucristo de los Santos de los Últimos Días). 
Al principio, solo parecía un poco raro por el nuevo libro de escrituras y la casi adoración al fundador, Joseph Smith.
Para mí, comenzó con la ceremonia de Iniciación: estás casi sin ropa, solo con una especie de poncho, como una faja ancha abierta por ambos lados, y un hombre te toca la rodilla, el vientre y la cabeza con óleo consagrado. Después, te pones las prendas del templo, un conjunto de ropa interior que prometes usar el resto de tu vida."""
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
                # Usar la duración completa del video de transición
                trans_duration = transition_clip.duration
                overlays.append(transition_clip)
                # Incluir también el audio de la transición (si lo tiene) en la pista de audio
                if transition_clip.audio is not None:
                    audio_segments.append(transition_clip.audio.with_start(current_time))
                current_time += trans_duration
    
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
