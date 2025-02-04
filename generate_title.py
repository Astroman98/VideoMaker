from moviepy import TextClip, CompositeVideoClip, VideoFileClip, AudioFileClip
import edge_tts
import asyncio
import os

async def generate_title_video(
    text="Hola, este es un título",
    resolution=(1920, 1080),
    font_size=70,
    font_color='white',
    voz="es-US-AlonsoNeural"
):
    """
    Genera un video con un título sobre un video de fondo,
    con duración sincronizada al audio TTS más 1 segundo.
    """
    # Asegurar que existe el directorio para el audio
    os.makedirs("audio", exist_ok=True)
    
    # Generar el audio TTS
    audio_file = "audio/title_audio.mp3"
    comunicador = edge_tts.Communicate(text=text, voice=voz, rate="+7%")
    await comunicador.save(audio_file)
    
    # Cargar el video de fondo y el audio TTS
    background = VideoFileClip("video/intro1.mp4", audio=False)  # audio=False ya que no tiene audio
    tts_audio = AudioFileClip(audio_file)
    
    # Duración total: audio + 1 segundo de silencio
    duration = tts_audio.duration + 1
    
    # Recortar el video de fondo si es necesario
    background = background.subclipped(0, duration)
    
    # Crear el texto
    text_clip = TextClip(
        text=text,
        font_size=font_size,
        color=font_color,
        font="font/HKGrotesk-SemiBoldLegacy.ttf",
        text_align='center',
        method='caption',
        stroke_width=2,
        stroke_color='black',
        size=(resolution[0] - 100, None)
    ).with_position('center')
    
    # Crear la composición final
    final_clip = CompositeVideoClip(
        [background, text_clip], 
        size=resolution
    ).with_duration(duration)
    
    # Agregar solo el audio TTS
    final_clip = final_clip.with_audio(tts_audio)
    
    # Guardar el video
    final_clip.write_videofile(
        "title.mp4",
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )
    
    # Cerrar los clips
    background.close()
    tts_audio.close()

if __name__ == "__main__":
    asyncio.run(generate_title_video(
        text="Hola, este es un título"
    ))