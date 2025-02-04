from moviepy import TextClip, CompositeVideoClip, ColorClip

def generate_title_video(
    text="Hola, este es un título",
    duration=5,
    resolution=(1920, 1080),
    bg_color=(0, 255, 0),
    font_size=70,
    font_color='white'
):
    """
    Genera un video con un título centrado y fondo de color.
    
    Args:
        text (str): Texto a mostrar como título
        duration (int): Duración del video en segundos
        resolution (tuple): Resolución del video (ancho, alto)
        bg_color (tuple): Color de fondo en RGB
        font_size (int): Tamaño de la fuente
        font_color (str): Color del texto
    
    Returns:
        None: Guarda el video como 'title.mp4'
    """
    # Crear el fondo de color
    background = ColorClip(size=resolution, color=bg_color)
    
    # Crear el texto usando los mismos parámetros que funcionan en main.py
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
    )
    
    # Centrar el texto
    text_clip = text_clip.with_position('center')
    
    # Crear la composición final
    final_clip = CompositeVideoClip(
        [background, text_clip], 
        size=resolution
    ).with_duration(duration)
    
    # Guardar el video
    final_clip.write_videofile(
        "title.mp4",
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

if __name__ == "__main__":
    # Ejemplo de uso
    generate_title_video(
        text="Hola, este es un título",
        duration=5,
        resolution=(1920, 1080),
        bg_color=(0, 255, 0)  # Verde
    )