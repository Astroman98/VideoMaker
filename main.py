import asyncio
import re
import os
import numpy as np
import textwrap
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy import concatenate_audioclips
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




import subprocess

import tempfile

import os
import asyncio
from xml.sax.saxutils import escape
import azure.cognitiveservices.speech as speechsdk

def _guess_lang_from_voice(voice_name: str) -> str:
    # Ej: "es-US-AlonsoNeural" -> "es-US"
    parts = voice_name.split("-")
    return "-".join(parts[:2]) if len(parts) >= 2 else "en-US"












import time
from xml.sax.saxutils import escape
import azure.cognitiveservices.speech as speechsdk

def generate_audio_with_azure_tts(
    text: str,
    output_file: str,
    voice: str = "es-US-AlonsoNeural",
    rate: str = "10%"
) -> bool:
    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION")

    if not key or not region:
        print("Faltan variables de entorno AZURE_SPEECH_KEY o AZURE_SPEECH_REGION")
        return False

    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.speech_synthesis_voice_name = voice
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Riff48Khz16BitMonoPcm
    )

    # NUEVO: más tolerancia a latencia de red y picos de síntesis
    # Si tu SDK es viejo y esto falla, actualiza el paquete a la versión más reciente.
    speech_config.set_property(
        speechsdk.PropertyId.SpeechSynthesis_FrameTimeoutInterval,
        "10000"
    )
    speech_config.set_property(
        speechsdk.PropertyId.SpeechSynthesis_RtfTimeoutThreshold,
        "25"
    )

    lang = _guess_lang_from_voice(voice)
    safe_text = escape(text)

    ssml = f"""
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{lang}">
  <voice name="{voice}">
    <prosody rate="{rate}">{safe_text}</prosody>
  </voice>
</speak>
""".strip()

    attempt = 0
    backoff = 15.0

    while True:
        attempt += 1
        result = None
        synthesizer = None
        try:
            audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            result = synthesizer.speak_ssml_async(ssml).get()

        except Exception as e:
            print(f"TTS excepción en intento {attempt}: {e}")

        finally:
            if synthesizer is not None:
                try:
                    synthesizer.close()
                except Exception:
                    pass

        if result and result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return True

        is_429 = False
        if result and result.reason == speechsdk.ResultReason.Canceled:
            details = result.cancellation_details
            print(f"TTS cancelado (intento {attempt}): {details.reason}")
            if details.error_details:
                print(f"Detalle: {details.error_details}")
                err = details.error_details.lower()
                is_429 = "429" in err or "too many requests" in err
        elif result is not None:
            print(f"TTS falló (intento {attempt}): {result.reason}")

        if not is_429:
            return False

        espera = round(backoff)
        print(f"Reintentando en {espera} segundos... (intento {attempt})")
        time.sleep(espera)
        backoff = min(backoff * 1.5, 90.0)













async def generate_audio_for_sentence(sentence, output_file, voz="es-US-AlonsoNeural"):
    return await asyncio.to_thread(
        generate_audio_with_azure_tts,
        sentence,
        output_file,
        voz,
        "+10%"
    )

async def generate_all_audios(sentences, seg_index):
    audio_files = []
    os.makedirs("audio_esp", exist_ok=True)

    for i, sentence in enumerate(sentences):
        file_path = f"audio_esp/seg{seg_index}_sentence_{i}.wav"
        success = await generate_audio_for_sentence(sentence, file_path)

        if success and os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            audio_files.append(file_path)
            print(f"Archivo de audio {i+1}/{len(sentences)} creado correctamente")
        else:
            print(f"ADVERTENCIA: Error al generar audio para la oración {i+1}")

        await asyncio.sleep(5.0)

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
        new_duration = clip.duration - 0.6 if clip.duration > 0.6 else clip.duration
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
    text=""" ¿Cuál es tu peor historia de "un amigo te traicionó por la espalda"? """,
    resolution=res
    )
    


    texto = (
       """ 


Mi amigo salía con una chica a la que, según me daba cuenta, simplemente no le caía bien, pero al menos éramos cordiales el uno con el otro, hasta el viaje de campamento del fin de semana festivo del 24 de mayo. Ella se empeñó en mantener nuestro alcohol separado, lo cual estaba bien. Yo tenía mi cerveza, ellos tenían sus limonadas con alcohol, así que bien. Luego me levanté temprano en la primera mañana e hice panqueques para todos, ¿por qué? Porque así es como soy. Cuando los campistas salieron de sus tiendas de campaña atraídos por el olor a panqueques de manzana y canela y café de fogata, ella fue la única que perdió los estribos. Yo había abierto su nevera portátil y usado su margarina. Mi amigo solo pareció apenado y trató de mantener la paz mientras yo le lanzaba una moneda de dos dólares y me disculpaba. Su reacción fue sacar un candado de su bolso de gimnasio y cerrar "su tienda de campaña" con "su alcohol" y "su comida". Más tarde, él se me acercó y me preguntó si le podía prestar el auto, para que pudieran ir rápido al pueblo, comprar unas cosas y hablar sobre ser un poco más tolerantes con los demás campistas. Le dije que estaba bien y le entregué las llaves. Cuando regresaron horas después, el tanque estaba vacío y la cocina de campaña (una caja de madera con correas llamada wannigan con platos, cubiertos, ollas y sartenes, etc.) había desaparecido de la parte trasera de la camioneta. Buscamos por el campamento, nada. Era de mi padre y había pasado de generación en generación en la familia. Fui conduciendo para llenar el tanque y comprar un envase nuevo de margarina, y estaba a la mitad del camino rural cuando vi el wannigan a un lado de la carretera, destrozado en la zanja. Había marcas a lo largo de los paneles traseros junto a los asientos abatidos donde uno de ellos claramente lo había empujado hacia afuera por la parte trasera del auto en movimiento.

Después de apilarlo todo de vuelta en la camioneta, atónito, pieza por pieza, llené el tanque de combustible y conduje de regreso, y luego empaqué mis cosas. Nadie dijo una palabra, hasta que rompí el permiso para acampar y arranqué a toda velocidad dejando sus gritos detrás de mí en el polvo.

Nunca volví a hablar con ninguno de los dos.

---
Tuve un "amigo" que le robaba a los amigos con bastante regularidad.

Una vez tuve una pequeña reunión social (6 o 7 personas) y mi nuevo teléfono desapareció. El muy miserable me ayudó a buscar el teléfono en mi casa durante más de una hora, y más tarde vi mi teléfono en su habitación sobre su escritorio. Simplemente lo tomé de vuelta, no se intercambiaron palabras. Solo dejé de hablarle por completo después de eso.

Más tarde, él estuvo en la fiesta de una amiga en común. El iPod de 80 gb de ella desapareció. Algunos amigos y yo sospechábamos que había sido él, así que al día siguiente llamamos a la casa de empeño local y describimos el iPod. El sujeto de la casa de empeño dijo que había recibido uno ese día. Efectivamente, estaba a nombre de este miserable. El dueño de la casa de empeño se ofreció a llamar a la policía, pero nosotros nos negamos. Nos acercamos al miserable y le dijimos que lo sabíamos. Intentó negarlo, pero logramos avergonzarlo hasta que lo admitió.

Al diablo con las personas que le roban a sus amigos.

---
Mientras trabajaba de forma independiente en un excelente proyecto que surgió de la nada, descubrí que trabajaría con Sean, un sujeto que estaba en mi grupo en una antigua agencia de publicidad. Genial, una cara conocida.

Bueno, Sean era un nerd. A nadie le caía bien y, como su director creativo asociado (supervisor), yo lo cuidaba. Parecía esforzarse mucho y yo no entendía por qué todos lo excluían. Durante dos rondas de despidos, di la cara por él y salvé su trabajo, prometiendo trabajar con él. Siempre estaba ocupado y, poco después, me fui a un nuevo trabajo. Así que esperaba con ansias trabajar un poco más con él y demostrarles a esos malditos de nuestra antigua agencia que estaban equivocados.

Mientras trabajaba en este proyecto independiente, sentí que algo andaba mal poco después de que comenzara. Sean no tenía ideas. ¡Ninguna! Literalmente traía una libreta en blanco día tras día. Las excusas eran que estaba cansado, que la tarea lo confundía, etc. Yo estaba nervioso, pero estaba atrapado. Así que, como estábamos en un equipo, compartí mis ideas, nuestras únicas ideas, con él. Teníamos que presentar una hora después del almuerzo.

Durante el almuerzo, tuve que ir a una cita médica con mi esposa, quien estaba gravemente enferma. En mi camino de regreso a la oficina, el taxi en el que iba tuvo un accidente. Un idiota en un Lexus se estrelló contra nosotros. Nadie resultó herido, pero ambos automóviles fueron pérdida total. Además, no me sentía cómodo dejando al taxista, ya que era extranjero y hablaba poco inglés. El sujeto que nos golpeó estaba despotricando, así que me quedé para dar una declaración a la policía. Llamé a Sean para explicarle, le pregunté si le importaba encargarse de la reunión y le pedí que informara sobre mi situación.

Entonces el imbécil presentó mi trabajo, afirmó que todo era suyo y me enviaron a casa porque "Sean lo hizo a la perfección".

Tardé 9 meses en que me pagaran por el tiempo que invertí. Todo el tiempo traté de explicarlo, pero nadie me creyó. Él copió mis notas con su propia letra y las presentó como prueba. En lo que a ellos respectaba, yo me estaba aprovechando del trabajo de este sujeto. Podría haberle pateado sus partes íntimas durante una semana sin aburrirme.

Dos meses después, fue descubierto cuando intentó hacerlo de nuevo. Docenas de antiguos compañeros de trabajo llamaron para restregármelo en la cara. "¿Todavía crees que solo estamos molestando a Sean?". Aprendí que a veces las personas son rechazadas porque se lo merecen.
---
Hace años, cuando cursaba mi licenciatura en ciencias de la salud, la mayoría de mis compañeros estaba decidida a entrar a la facultad de medicina. Nuestro programa de medicina aceptaba principalmente a estudiantes de nuestra competitiva carrera debido a los requisitos previos de las materias. Todos nos conocíamos y éramos amistosos; pasábamos tiempo juntos y formábamos grupos de estudio.

Muchos de mis amigos eran geniales: compartíamos consejos, recursos y practicábamos juntos para los exámenes y las entrevistas. Pero había un puñado que realmente quería entrar a medicina y, como el programa clasifica a los solicitantes principalmente en función de los resultados de la licenciatura, cuanto mejor se desempeñan tus amigos, más baja es tu posición en la clasificación para la selección.

Así que, cerca de la época de solicitudes, algunos de nosotros íbamos a la biblioteca de la universidad a pedir prestados libros de texto para buscar los capítulos o los números de página que el profesor mencionó que vendrían en el examen.

Y estaban arrancados. Ibas a buscar otra copia del libro en la biblioteca y esa página también estaba arrancada. Todas, eliminadas apresuradamente.

No creía que alguien de nuestro grupo hubiera hecho eso, hasta que comenzaron las prácticas de entrevista. Los estudiantes empezaron a conseguir copias de las preguntas de años anteriores y mentían cuando otros preguntaban si las tenían. Vi a alguien dar una respuesta terrible y espantosa en una entrevista, y el otro estudiante le daba comentarios positivos y le sugería que dijera eso, palabra por palabra, durante la entrevista real. Fue un desastre y muchas relaciones se vinieron abajo o nunca volvieron a ser las mismas.
---
Mi "mejor amiga" y yo trabajamos juntas durante 3 años en un restaurante. Yo era la gerente nocturna y me llevaba muy bien con todos los empleados, especialmente con ella. Pasábamos tiempo juntas fuera del trabajo todo el tiempo; ella me acompañaba a la playa y a ferias con mis hijos, quienes la adoraban.

Ella comenzó a salir con un sujeto del trabajo que se estaba convirtiendo poco a poco en un adicto a las drogas. Yo podía notarlo (mi tía adicta al crack hacía que fuera fácil de identificar), pero nadie más podía. Después de que él cometió errores por décima vez en una semana y comenzó a quedarse dormido de pie en el fregadero, mi jefe lo despidió un sábado.

La noche del lunes siguiente, a la hora del cierre, él entró por la puerta trasera usando una máscara de esquí. Yo caminaba hacia la puerta principal para cerrarla cuando me agarraron por detrás y sentí algo frío contra mi cuello. Me tomó un segundo darme cuenta de que era un cuchillo. Él dijo: "dame el dinero", pero yo no podía moverme. Estaba literalmente paralizada por el miedo. Mi cerebro me gritaba que me moviera hacia la caja registradora, pero mis pies simplemente no respondían. Él gritó "dame el dinero" de nuevo, pero yo seguía congelada.

Luego me arrastró hasta la caja, me obligó a abrirla, tomó un puñado de billetes de 20 dólares y salió corriendo por la parte trasera.

¿Dónde estaba mi mejor amiga mientras todo esto sucedía? Convenientemente, en el baño. Yo todavía estaba en shock intentando explicarle a la policía por teléfono lo que acababa de pasar. Cuando colgué, ella preguntó qué había ocurrido y le dije que acababan de robarme a punta de cuchillo. Su respuesta exacta fue: "espero que nadie piense que tuve algo que ver con esto".

¿Cómo? En resumen, encontraron al tipo (les dije que reconocí su voz) y él la delató sobre la planificación del robo (el "plan" era que ella le enviara un mensaje de texto avisándole cuando solo estábamos ella y yo en el edificio). Él no tenía por qué hacerlo, pero ella renunció al día siguiente y dejó de responder a mis mensajes.

Cuando me enteré, me sentí destrozada. Era alguien que frecuentaba a mis hijos regularmente. Me diagnosticaron ansiedad y trastorno de estrés postraumático después del robo y todavía tengo recuerdos repentinos de aquel momento. Si alguien se acerca por detrás y me asusta, entro en pánico.

¿La cantidad de dinero por la que valía mi vida para ellos? Unos 450 dólares.

¿El castigo que recibieron? Él recibió 2 años de cárcel, con 10 años de sentencia suspendida y 1 año de libertad condicional.

Ella recibió 1 año de libertad condicional.

Tuve que renunciar al trabajo que tuve durante más de una década porque ya no podía soportar estar allí.
---
Todo esto comienza mal por mi parte, al seguir a mi novio a la misma universidad a la que él iba (él era un año mayor; aun así no me arrepiento, ya que amé mi universidad y todo lo demás de esos 4 años). Tuvimos una relación intermitente durante el primer semestre que estuve allí (de nuevo, ¡señales de alerta!). Mi nueva compañera de cuarto, que vivía cruzando el pasillo, se convirtió en mi "mejor amiga". Ella y mi novio realmente no se llevaban bien, pero no era un gran problema; solo un choque de personalidades y a ella no le gustaba cómo él me trataba con las tonterías de terminar y volver.

Nuestra universidad tenía un periodo de invierno en enero. Mi novio vivía fuera del campus, así que estaba allí, y mi mejor amiga estaba tomando una clase; yo estaba en casa. Mi mejor amiga se sentía sola y no conocía a mucha gente en el campus durante ese periodo, así que le dije que saliera con los chicos de la fraternidad de mi novio, con quienes ella tenía una relación más o menos amistosa. Así que todos empezaron a salir.

Y por eso, por supuesto, quiero decir que empezaron a tener relaciones.

Regresé a la universidad e inmediatamente pude notar que las cosas estaban raras con mi mejor amiga (sin que yo lo supiera en ese momento, mi novio había tenido prácticamente toda nuestra relación para practicar cómo cubrir sus huellas y, para ese punto, ya era un mentiroso hábil y experimentado). En un par de semanas, todo salió a la luz: habían estado juntos y mi mejor amiga, de hecho, me dijo: "sabes cuánto he querido un novio; si fueras una buena amiga, me dejarías quedármelo". (Por qué yo aún quería salir con él en ese momento escapa a la comprensión de muchas, muchas, MUCHAS personas, incluida la mía, pero involucraba a un perro al que yo estaba profundamente apegada).

Culpo a ambos por igual, y también lo hice en aquel entonces; no recuerdo haber estado tan enojada con ellos como devastada. Él estuvo disculpándose desde el principio; ella fue cruel y manipuladora (de nuevo, no intento decir que fue "culpa de la otra mujer", solo explico cómo sucedieron las cosas). Fue algo terrible y me sentí muy traicionada por ambos. Como era de esperar, he tenido muchos problemas de confianza y lealtad desde entonces.
---
Tuve un amigo desde la escuela secundaria hasta hace unos 4 años (aproximadamente 8 o 9 años de amistad en total). Era un amigo muy cercano y, un día, nos confesó a mi novio (ahora mi esposo) y a mí que su compañero de cuarto se mudaba con su novia y que él no podría pagar el alquiler ese mes. Mi novio y yo teníamos un contrato de arrendamiento a punto de vencer, así que decidimos ayudarlo y nos mudamos con él (faltaban 2 meses para que terminara nuestro contrato, es decir, 2 pagos de alquiler). Vivimos allí cerca de 2 meses y nos enteramos de que estábamos embarazados y esperando un bebé. Todo parecía ideal, ya que el compañero de cuarto nos había informado que deseaba cedernos el contrato de la casa para mudarse de vuelta con sus padres. Era una casa perfecta, con 3 habitaciones, 2 baños y mucho espacio.

El día antes de reunirnos con el propietario, llegamos a casa y encontramos una notificación de desalojo en la puerta; todas las cosas del compañero de cuarto habían desaparecido. Lo llamé, pero no contestaba. Llamé al número del propietario que figuraba en la notificación y descubrí que el tipo nos había mentido y nunca le había dicho nada al dueño. El propietario ni siquiera quiso negociar con nosotros; simplemente dijo que teníamos 30 días para irnos. Resulta que el compañero de cuarto se había estado quedando con nuestro dinero del alquiler durante meses. Tuvimos que encontrar un lugar nuevo de forma inesperada en 30 días, pagar el primer mes, el último mes y un depósito de seguridad, además de mudarnos en pleno invierno de Michigan mientras estaba embarazada... fue un verdadero idiota.
---
En la universidad, mi mejor amiga y yo compartíamos una clase de arte con un chico con el que salía frecuentemente; nos estábamos conociendo para ver si había algo más entre nosotros. Salíamos, pasábamos el rato, nos divertíamos, etcétera. Todavía no había nada formal ni hablado, pero hablábamos a diario. Éramos más que amigos, aunque no una pareja formal.

Un día pasé por su casa después de una clase matutina por una razón que ya olvidé. Toqué, nadie respondió, así que entré por la puerta, que estaba sin seguro (en un pequeño pueblo de Kansas, nadie cierra nada) para dejarle una nota (era antes de los celulares y los mensajes de texto, al menos para mí).

Bueno, el bolso de ella estaba en la silla junto a la puerta. Nadie respondió cuando grité su nombre. Ni el de ella. Su auto estaba allí, su bolso estaba ahí, los dos estaban ahí... qué horror.

Sin embargo, me vengué de ella casi 20 años después: me envió una solicitud de amistad en Facebook y rechacé a esa mujer. ¡Toma eso, Jessica!
---
Hace varios años me mudé a Florida. Casi inmediatamente después conocí a un amigo; era un gran sujeto (o eso pensaba) y constantemente pasábamos tiempo juntos, él me mostraba la ciudad, el estado, etcétera.

Aproximadamente un año y medio después de conocerlo, me robó un par de tarjetas de crédito y acumuló cuentas muy altas. Desafortunadamente para mí, y esto lo sé ahora pero no en ese momento, simplemente pensé que llamar a la compañía de la tarjeta para reportar el robo y cancelar la cuenta también anulaba los cargos. Eso no es cierto: en realidad tienes que impugnar los cargos formalmente por separado, y solo tienes 60 días para hacerlo.

Para cuando me di cuenta, ya era demasiado tarde. Intenté, en vano, llegar a un medio acuerdo con él para tratar de establecer un plan de pagos. Me rogó que no llamara a la policía. Ahora me arrepiento de no haberlo hecho. Creía que había pasado por una mala racha, que se recuperaría y que intentaría pagarme. Eso no sucedió. Aunque, más adelante, lo arrestaron por otra cosa y le dieron libertad condicional.

Pensé que ese habría sido el mejor momento para intentar recuperar el dinero perdido (me había atrasado en los pagos y mi crédito comenzaba a sufrir. Tuve que abandonar la universidad por eso). En cambio, intenté llevarlo a un tribunal de reclamos menores. Entiendo que un tribunal civil no es penal, pero con él siendo ya un criminal convicto, pensé que tendría más posibilidades de que mi caso se viera mejor.

Sin embargo, cuando llegamos a la corte, lo negó todo, dijo que todo había sido un regalo y me difamó por completo en audiencia pública. No entiendo cómo se le permitió salirse con la suya, pero el caso fue desestimado: no obtuve nada.

Mi crédito sufrió durante años por eso. Con el tiempo, ahorré suficiente dinero para declararme en bancarrota y así deshacerme de esa deuda que no podía pagar (ni debería haber tenido que pagar). Nunca lo he perdonado realmente por lo que me hizo. Hasta donde sé, él todavía vive por la zona; afortunadamente no lo he visto en varios años. No sé ni qué le diría si llegara a encontrarme con él. La bancarrota eliminó esa deuda, así que no puedo (ni voy a) decir nunca que me debe nada monetariamente. Sin embargo, me debe una disculpa enorme. Pero, como dije, dudo seriamente de su sinceridad y probablemente no la aceptaría de todos modos. Creo que lo mejor es como está ahora: que simplemente se mantenga alejado de mí.
---
Tuve un amigo durante 20 años. Me llamó por la noche para pedirme prestados 3600 dólares. Era para su último año de carrera universitaria y le darían un aumento al graduarse. En ese momento yo ganaba bastante dinero y tenía mucho en el banco. Dijo que me lo devolvería en un año. Tres años después, tras la crisis económica, todavía no me había devuelto el dinero y me daba constantemente excusas patéticas como que "necesita tres vacaciones al año" y "está ahorrando para comprar una casa". Mi situación había cambiado y él no solo seguía negándose a pagarme, sino que seguía pidiendo favores y préstamos. Finalmente le dije que estaba sin dinero, a lo que él respondió "eres estúpido, nunca voy a pagarte ni a ayudarte". Corté mi amistad con él y he tenido muy poco contacto con él desde entonces. Él sí contrató a mi esposa en una empresa que administra. Supongo que debí haberlo visto venir.

Me acababa de casar y tenía dos hijos. En otra ocasión me dijo "¡tus hijos no se están muriendo de hambre!". Siempre pensaba solo en sí mismo. No le importaba nadie más. Supongo que yo pensaba que él era divertido. Escuchaba sus historias estando con damas de la noche y finalmente fue suficiente. La última vez que hablé con él como amigo, me estaba pidiendo que le consiguiera marihuana. Le dije que me desviaba mucho de mi camino. Estaba demasiado ocupado. Él dijo "¿es mucho pedir, eh?". Yo le respondí "bueno, ¿qué harías tú por mí?". Cuando creces con un sujeto, simplemente parece demasiado difícil reconocer que en realidad no es un amigo. Me guardé esto por un tiempo. Ya no tengo amigos de la escuela secundaria porque todos eran así. Realmente debí haberme juntado con una mejor clase de personas.

---
Era mi mejor amigo desde hacía 12 años y vivíamos juntos; le confiaba mi vida. Crecimos juntos e incluso fuimos a la universidad a la par.

Resultó que se estuvo acostando con mi novia (con la que yo llevaba 3 años) durante 6 meses antes de que yo me diera cuenta. Yo ya sabía que ella no era feliz en la relación.

Durante esos 6 meses le confié mis problemas; él se hacía el tonto e intentaba consolarme. ¿Cómo puedes hacerle eso a un hermano y que te salga tan bien?

Pensándolo en retrospectiva, debió haber sido obvio para mí. Todas las señales estaban ahí, pero uno simplemente no sospecha de su mejor amigo.

Al final, ella me robó £1000 y él me robó mi ps2 junto con todos mis juegos, y se mudó con ella. El día que fui a golpear su puerta, ella me abrió y él estaba allí. Había cajas de mudanza por todas partes y él me lanzó una mirada desafiante y llena de desprecio. Yo estaba en estado de shock; en ese momento aún no sabía que me habían robado, así que simplemente me quedé ahí, totalmente paralizado. Luego, me di la vuelta y me fui.

Ni siquiera la miré a ella. Sabía que las cosas iban de mal en peor desde hacía mucho tiempo, pero la traición de él fue brutal y yo no podía creerlo.

Seis meses después, empecé a salir con otra chica y pasé un año increíble a su lado. Olvidé todo lo que había sucedido; era el amor de mi vida. Sin embargo, las cosas también se complicaron y, lamentablemente, falleció a causa de una convulsión. Recién ahora (5 años después) he logrado superar eso.

Supongo que no tengo mucha suerte con las mujeres.

Imagino que la mayoría de las historias serán similares a la mía, pero simplemente es increíble que tu mejor amigo pueda hacerte algo así. Me dejó destrozado durante muchísimo tiempo.


---
Tuve que salir de la ciudad por trabajo durante seis semanas. No era una distancia tan grande como para no poder volver cada fin de semana.

Mi novia en aquel entonces era una psicópata oculta. Aún no se había manifestado, pero estaba en una espiral descendente. Estar juntos dos días seguidos y pasar cinco separados no era suficiente para ella.

Mi mejor amigo tenía muchas novias; yo acudía a él por consejos, para desahogarme o simplemente para mantener la cordura y tener un compañero con quien hablar. Él me preguntó si podía hablar con ella sobre cualquier tema, pero le dije que no, que solo me diera consejos a mí. Al llegar a la quinta semana, mi novia tuvo una crisis nerviosa; me llamó diciendo que me odiaba y mencionó quejas que yo le había hecho a mi mejor amigo sobre ella, pero mucho más exageradas de lo que yo realmente había dicho. Yo le dije cuánto la amaba.

Pensé que era imposible que fuera mi mejor amigo. Habíamos sido compañeros por más de una década y compartíamos historias todo el tiempo; creí que alguien más se estaba burlando de mí, así que lo enfrenté.

"No le he dicho nada", afirmó él. Le echó la culpa a su exnovia loca. Mi novia de ese entonces lo confirmó: era su ex. Supuestamente, ella había hackeado su correo electrónico y enviado todos los registros de mis quejas fuera de contexto a mi novia "porque estaba preocupada por nuestra relación". Pensé que podía solucionar esto; soy una buena persona y era obvio que todo estaba fuera de contexto, así que intenté explicárselo todo. Mi amigo fingía estar molesto por su "ex loca". "Ella también está arruinando mi relación, hombre", decía. Él estaba con una chica diferente en ese momento, llevaban juntos más de un año; tenían problemas, pero yo creía que podrían superarlos. "La amo más que a nada", decía. "Quiero casarme con ella. Estoy cansado de las citas, ella es la indicada".

Seguí acudiendo a mi amigo por consejos. Me decía que me relajara, que todo mejoraría cuando yo regresara y que me concentrara en mi trabajo. Fui ingenuo.

Nada funcionaba. Ella decía que no podía soportar que yo estuviera fuera todo el tiempo (viajaba cinco horas a casa cada fin de semana y otras cinco horas de vuelta al trabajo). Decía que estaba "viendo a alguien más para mantenerse feliz". Yo le dije que estaba bien que saliera con alguien más, que ella seguía siendo mía. Le pregunté a mi mejor amigo y me respondió: "de ninguna manera, hombre, no está viendo a nadie; no puede darte un nombre, así que no es cierto. Solo está jugando contigo, mantente fuerte".

Al regresar, lidié con su actitud de psicópata durante un par de semanas. Ella comenzó a quererme de nuevo. Yo intentaba hacer lo correcto; me sentía mal por haberla dejado sola, aunque no fuera por mucho tiempo.

No hubo ningún hackeo. No hubo explicación. Mi mejor amigo me mintió en la cara. Él era el "sujeto al que ella estaba viendo" y ambos consumían muchas drogas. Mi mejor amigo nos mintió a mi novia y a mí para que ella se molestara y me dejara de querer, así él podía salir de fiesta con ella. Mientras tanto, me decía que quería casarse con su novia actual y culpaba de todos mis problemas a una de sus ex. Sus mentiras duraron semanas. Yo estaba molesto, pero él seguía siendo mi mejor amigo.

Cuando lo descubrí, él me dijo: "lo siento, ahora estoy tratando de mantener distancia con tu novia, los sentimientos se interpusieron hace dos semanas", pero aseguró que no había pasado nada. Por cierto, añadió: "ella te engañó justo antes de tu cumpleaños". Ahí es donde debí haber cortado todo, pero fui ingenuo. Yo respondí: "no, quiero hacer lo correcto, amo a esta chica, me siento mal por lo mal que está ella", etc. (Ella no había terminado sus estudios, no tenía trabajo y estaba sufriendo, pero definitivamente podría haber salido adelante si lo hubiera intentado). Él me preguntaba mucho: "¿cómo lo haces, cómo te mantienes fuerte?". Yo siempre le explicaba que quería hacer lo correcto y que amaba a esa chica. Fui estúpido. Era adicto a ella.

Intenté pasar todo el tiempo posible con ella. Mi mejor amigo seguía hablando de cómo quería casarse con su novia y de cómo le había contado todo lo que pasó entre él y mi novia. Decía que quería que nuestras vidas volvieran a la normalidad.

Pasaron unas semanas. Todo seguía siendo difícil. Ella me trataba mal, pero las cosas iban mejorando poco a poco. Ahora yo era honesto con todo y ella decía que también lo era. Finalmente, ella se quebró; me amaba de nuevo y me confesó que "verlo a él" significaba acostarse con él. Se estaba acostando con mi mejor amigo mientras yo estaba fuera. Él me mentía en la cara diciendo que quería casarse con su novia, mientras engañaba a su pareja con la mía, y ambos me ocultaban la verdad. Me fui de la ciudad por dos semanas, distante y destrozado. Ella se molestó y peleamos. Se había estado acostando con él todo el tiempo, incluso cuando yo había regresado. Todo el tiempo.

Él era mi mejor amigo, decía que quería ayudarme y siempre me ofrecía su apoyo. Usó todo lo que le conté en confianza mientras yo le pedía consejos sentimentales para ponerla en mi contra durante meses. Todos los consejos que me dio estaban diseñados para que ella me odiara más. "Prepárale una cena, te daré una receta para una salsa de carne increíble, hazla con vino tinto". Ella odiaba esa salsa y el vino tinto. Él se la estaba acostando y dándole drogas gratis después de que yo había pasado un año con ella, todo mientras me mentía a la cara, mirándome a los ojos y diciéndome cuánto lo sentía y cómo arreglar las cosas. Ambos me mintieron.

Ahora ambos son adictos; mi ex tiene una deuda enorme, vive con sus padres y ambos tienen trabajos mediocres en ventas. Yo recibí un bono de $4000 después de mis seis semanas fuera de la ciudad. Todavía estoy enojado por esto; mi corazón late con fuerza en este momento. He perdido mucha fe en la humanidad y la confianza incondicional que antes tenía en que las personas querían ser buenas entre sí. No salgas con una chica que sea tan insegura que necesite la atención de otros hombres en las fiestas para ser feliz, pero que se altere cuando tú apenas miras a otra mujer, aunque sea una anciana tomando tu pedido en un restaurante.

---
Cuando estaba en el grado 11, conocí a mi primera novia. Éramos realmente geniales juntos. Aunque tenía que conducir 45 minutos para verla, siempre esperaba con ansias pasar tiempo con ella porque era increíble.

Sin embargo, unos 4 meses después de iniciada la relación, mi mejor amigo comenzó a hablar con mi novia. No vi nada malo en ello porque confiaba tanto en él como en ella. Gran error. Una noche, mi novia me envió un mensaje instantáneo: "¿Cómo pudiste hacerme esto?". Mi corazón se hundió de inmediato. No tenía idea de qué estaba hablando. Le pregunté repetidamente qué había hecho, pero ella insistía en que me estaba haciendo el tonto. La llamé por teléfono para hablar. Me dijo que mi mejor amigo le había contado que yo estaba coqueteando con otra chica en mi escuela.

No importaba cuánto lo intentara, no podía convencerla de lo contrario. Terminó conmigo. Aproximadamente un mes después, fui al pueblo donde ella vivía. Un amigo y yo íbamos a pasar el rato con unos conocidos en común de mi ex. Fuimos a su casa y, ¿quién estaba ahí? Mi mejor amigo y mi ex, ella sentada en su regazo. Al parecer, mi "mejor amigo" le había pedido salir poco después de que terminara conmigo, y ella había aceptado. Ella confiaba en él porque él me había "delatado". Hasta el día de hoy, esta es la mayor traición que he sentido.





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
        #"Test(esp).mp4",
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
        if file.endswith((".mp3", ".wav")):
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