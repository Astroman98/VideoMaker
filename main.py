import asyncio
import re
import os
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy import concatenate_audioclips
import edge_tts

def split_sentences(texto):
    """
    Separa el texto en oraciones usando el punto final como delimitador.
    """
    oraciones = re.split(r'(?<=[.])\s+', texto.strip())
    return oraciones

async def generate_audio_for_sentence(sentence, output_file, voz="es-US-AlonsoNeural"):
    """
    Opciones de voz: es-US-AlonsoNeural,
                     en-US-ChristopherNeural
    """
    comunicador = edge_tts.Communicate(text=sentence, voice=voz)
    await comunicador.save(output_file)
    print(f"Audio guardado: {output_file}")

async def generate_all_audios(sentences):
    """
    Genera audios para cada oración y devuelve una lista de rutas a los archivos generados.
    """
    audio_files = []
    # Asegurarse de que la carpeta existe
    os.makedirs("audio", exist_ok=True)
    
    for i, sentence in enumerate(sentences):
        file_path = f"audio/salida_{i}.mp3"
        await generate_audio_for_sentence(sentence, file_path)
        audio_files.append(file_path)
    return audio_files

def generate_subtitle_entries(sentences, durations):
    """
    Con las duraciones exactas de cada audio, genera una lista de tuplas
    (inicio, fin, oración) para los subtítulos.
    """
    entries = []
    start = 0
    for sentence, d in zip(sentences, durations):
        entries.append((start, start + d, sentence))
        start += d
    return entries

async def main():
    # Texto completo pegado con comillas triples
    texto = (
       """Crecí como Testigo de Jehová y finalmente "me alejé" alrededor de los 14 años. 
En ese entonces no pensaba que fuera una secta, solo creía que estaban equivocados en su forma de ver las cosas. 
No tenían respuestas para mis preguntas, y sabía por mi mamá que habían predicho el fin del mundo docenas de veces, y todas habían fallado. 

Así que exploré otras religiones, terminando en la de mi mejor amigo: los mormones (o llamados como la Iglesia de Jesucristo de los Santos de los Últimos Días). 
Al principio, solo parecía un poco raro por el nuevo libro de escrituras y la casi adoración al fundador, Joseph Smith.
Para mí, comenzó con la ceremonia de Iniciación: estás casi sin ropa, solo con una especie de poncho, como una faja ancha abierta por ambos lados, y un hombre te toca la rodilla, el vientre y la cabeza con óleo consagrado. Después, te pones las prendas del templo, un conjunto de ropa interior que prometes usar el resto de tu vida. 
"""
    )
    
    # 1. Separar el texto en oraciones
    sentences = split_sentences(texto)
    print("Oraciones:")
    for i, s in enumerate(sentences, 1):
        print(f"{i}: {s}")
    
    # 2. Generar un audio para cada oración
    audio_file_paths = await generate_all_audios(sentences)
    
    # 3. Cargar cada audio y obtener su duración
    audio_clips = []
    durations = []
    for file in audio_file_paths:
        clip = AudioFileClip(file)
        audio_clips.append(clip)
        durations.append(clip.duration)
    
    total_duration = sum(durations)
    print(f"Duración total: {total_duration} segundos")
    
    # 4. Concatenar los audios en uno solo
    final_audio = concatenate_audioclips(audio_clips)
    
    # 5. Cargar el video y recortarlo a la duración total del audio concatenado
    video_clip = VideoFileClip("video/gameplay1.mp4").subclipped(0, total_duration)
    video_clip = video_clip.with_audio(final_audio)
    
    # 6. Generar entradas para los subtítulos basadas en las duraciones reales
    subtitle_entries = generate_subtitle_entries(sentences, durations)
    
    # 7. Crear clips de subtítulos para cada oración
    subtitle_clips = []
    for start, end, sentence in subtitle_entries:
        dur = end - start
        txt_clip = TextClip(
            text=sentence,
            font_size=24,
            color='white',
            font="font/arial.ttf",  # Asegúrate de tener esta fuente o cambia la ruta
            method='caption',
            size=(video_clip.w - 100, None)
        ).with_position(('center', video_clip.h - 100)
        ).with_start(start
        ).with_duration(dur)
        subtitle_clips.append(txt_clip)
    
    # 8. Combinar el video con los subtítulos
    final_video = CompositeVideoClip([video_clip, *subtitle_clips])
    
    # 9. Exportar el video final
    final_video.write_videofile(
        "video_con_audio_y_subtitulos.mp4",
        fps=video_clip.fps,
        codec="libx264",
        audio_codec="aac"
    )
    print("Video guardado como: video_con_audio_y_subtitulos.mp4")

if __name__ == "__main__":
    asyncio.run(main())
