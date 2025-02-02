import asyncio
import edge_tts
import re
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

async def generar_audio(texto, archivo_salida, voz="es-ES-AlvaroNeural"):
    """
    Genera un archivo de audio a partir de un texto usando edge_tts.
    """
    comunicador = edge_tts.Communicate(text=texto, voice=voz)
    await comunicador.save(archivo_salida)
    print(f"Audio guardado como: {archivo_salida}")

    print("Hola")
    print("Hola 2")

def generar_subtitulos(texto, duracion_total):
    """
    Divide el texto en subtítulos (usando signos de puntuación como delimitadores) y
    asigna a cada uno una duración proporcional a su longitud.
    
    Retorna una lista de tuplas (inicio, fin, texto_del_subtítulo).
    """
    # Dividir el texto en fragmentos en cada punto, signo de exclamación o interrogación.
    subtitulos = re.split(r'(?<=[.!?])\s+', texto)
    subtitulos = [s.strip() for s in subtitulos if s.strip()]
    
    # Calcular la cantidad total de caracteres para distribuir el tiempo
    total_chars = sum(len(s) for s in subtitulos)
    
    entradas = []
    tiempo_acumulado = 0
    for s in subtitulos:
        # Duración proporcional (mínimo 1 segundo por fragmento)
        dur = max((len(s) / total_chars) * duracion_total, 1.0)
        entradas.append((tiempo_acumulado, tiempo_acumulado + dur, s))
        tiempo_acumulado += dur
    return entradas

def agregar_subtitulos(video, lista_subtitulos):
    """
    Recibe un clip de video y una lista de subtítulos (con tiempos de inicio y fin)
    y genera un nuevo clip con los textos sobrepuestos.
    """
    clips_subtitulos = []
    for inicio, fin, texto in lista_subtitulos:
        dur = fin - inicio
        txt_clip = TextClip(
            text=texto,
            font_size=24,           # Se usa "font_size" (con guión bajo)
            color='white',
            font="font/arial.ttf",  # Especifica la ruta a tu archivo de fuente
            method='caption',
            size=(video.w - 100, None)
        ).with_position(('center', video.h - 100)
        ).with_start(inicio
        ).with_duration(dur)
        clips_subtitulos.append(txt_clip)
    
    # Combinar el video y los clips de subtítulos
    return CompositeVideoClip([video, *clips_subtitulos])

async def main():
    # Texto a sintetizar y usar para los subtítulos
    texto = (
        'Crecí como Testigo de Jehová y finalmente "me alejé" alrededor de los 14 años. '
        'En ese entonces no pensaba que fuera una secta, solo creía que estaban equivocados en su forma de ver las cosas. '
        'No tenían respuestas para mis preguntas, y sabía por mi mamá que habían predicho el fin del mundo docenas de veces, y todas habían fallado.'
    )
    
    # Generar el audio TTS y guardarlo en la carpeta "audio"
    archivo_audio = "audio/salida.mp3"
    await generar_audio(texto, archivo_audio, voz="es-ES-AlvaroNeural")
    
    # Cargar el audio generado para obtener su duración
    audio_clip = AudioFileClip(archivo_audio)
    duracion = audio_clip.duration
    
    # Cargar el video de gameplay desde la carpeta "video"
    video_clip = VideoFileClip("video/gameplay1.mp4").subclipped(0, duracion)
    
    # Asignar el audio TTS al video
    video_clip = video_clip.with_audio(audio_clip)
    
    # Generar la lista de subtítulos a partir del texto y la duración total
    lista_subtitulos = generar_subtitulos(texto, duracion)
    
    # Agregar los subtítulos al video
    video_final = agregar_subtitulos(video_clip, lista_subtitulos)
    
    # Exportar el video final con audio y subtítulos
    video_final.write_videofile(
        "video_con_audio_y_subtitulos.mp4",
        fps=video_clip.fps,
        codec="libx264",
        audio_codec="aac"
    )
    print("Video guardado como: video_con_audio_y_subtitulos.mp4")

if __name__ == "__main__":
    asyncio.run(main())
