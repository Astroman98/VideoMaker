from moviepy import TextClip, CompositeVideoClip, VideoFileClip, AudioFileClip
from moviepy import VideoFileClip, vfx
import edge_tts
import asyncio
import os
from moviepy import concatenate_videoclips
from moviepy.audio.AudioClip import AudioArrayClip
from moviepy import concatenate_audioclips
import numpy as np
from moviepy.video.fx.FadeOut import FadeOut  # Importar las clases correctas
from moviepy.video.fx.FadeIn import FadeIn



async def generate_title_video(
    text="Hola, este es un título",
    resolution=(1920, 1080),
    font_size=60,
    font_color='#cfcfcf',
    voz="es-US-AlonsoNeural",
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
    background = VideoFileClip("video/intro1.mp4", audio=False)
    tts_audio = AudioFileClip(audio_file)


    # Duración del silencio inicial
    silence_duration = 1

    # Usamos las mismas características de audio (fps) que el TTS
    fps = tts_audio.fps  
    samples = int(fps * silence_duration)
    silence_array = np.zeros((samples, 2), dtype=np.float32)
    silence_clip = AudioArrayClip(silence_array, fps=fps)
    combined_audio = concatenate_audioclips([silence_clip, tts_audio])
    
    # Duración total: audio + 1 segundo de silencio
    duration = combined_audio.duration
    
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
    
    # En generate_title.py, modifica la parte donde se aplican los efectos:

    # Crear la composición final
    final_clip = CompositeVideoClip(
        [background, text_clip], 
        size=resolution
    ).with_duration(duration)
    
    # Agregar el audio
    final_clip = final_clip.with_audio(combined_audio)

    # Crear y aplicar los efectos de fade
    fade_in = FadeIn(1.5).copy()  # 2 segundos de fade in
    fade_out = FadeOut(0.5).copy()  # 2 segundos de fade out
    
    final_clip = fade_in.apply(final_clip)
    final_clip = fade_out.apply(final_clip)
    
    
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