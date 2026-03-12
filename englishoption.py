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


def _azure_tts_to_mp3(text: str, output_mp3: str, voice: str, rate: str) -> None:
    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION")

    if not key or not region:
        raise RuntimeError("Faltan AZURE_SPEECH_KEY o AZURE_SPEECH_REGION en el entorno.")

    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.speech_synthesis_voice_name = voice
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Riff48Khz16BitMonoPcm
    )


    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_mp3)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    lang = _guess_lang_from_voice(voice)
    safe_text = escape(text)

    ssml = f"""
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{lang}">
  <voice name="{voice}">
    <prosody rate="{rate}">{safe_text}</prosody>
  </voice>
</speak>
""".strip()

    result = synthesizer.speak_ssml_async(ssml).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return

    if result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        msg = f"TTS cancelado: {details.reason}"
        if details.error_details:
            msg += f" | {details.error_details}"
        raise RuntimeError(msg)

    raise RuntimeError(f"TTS falló: {result.reason}")


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
---
Years ago, when I did a health sciences undergraduate degree, most of the cohort was determined to get into medical school. Our medical school program mainly accepted students from only our competitive undergraduate course, due to subject prerequisites. We all knew each other and were friendly, hanging out together and forming study groups.

Many of my friends were great. We shared tips, resources, practiced exams, and interviews together. But there were a handful who really wanted to get into medical school, and since the program ranks applicants mainly based on undergraduate results, the better your friends perform, the lower your ranking is for selection.

So near application time, some of us would head off to the university library to borrow textbooks to find chapters or page numbers that the lecturer mentioned would be on the exam.

And they would be ripped out. You'd go and find another library copy of the textbook, and that page would be ripped out too. All of them, totally removed in a hurry.

I didn't believe that someone from our cohort did it until interview practice began. Students began obtaining copies of the questions from previous years and lying when others asked if they had them. I saw someone give a terrible, awful interview answer, and the other student would give them glowing feedback and inform them they should say that, word-for-word, during the interview. It was a mess and a lot of relationships fell apart, or were never the same again.
---
My "best friend" and I worked together for 3 years at a restaurant. I was the night manager and was really cool with all of the employees, but especially her. We hung out outside of work all the time; she went with me to the beach and carnivals with my kids, who adored her.

She started dating this guy at work who was slowly becoming a drug addict. I could see it, but no one else could. After he messed up for the 10th time in a week and started nodding out at the sink, he was fired by my boss on a Saturday.

The following Monday night, at closing time, he came in the back door wearing a ski mask. I was walking towards the front door to lock it when I was grabbed from behind and felt something cold against my neck. It took me a second to realize it was a knife. He said "get me the money," but I couldn't move. I was literally paralyzed with fear. My brain was screaming at me to move towards the register, but my feet just wouldn't move. He screamed "give me the money" again, but I was frozen.

He then dragged me to the register, made me open it, grabbed a fistful of 20s, and ran out the back.

My best friend at the time this whole thing went down? Conveniently, she was in the bathroom. I was still in shock trying to explain to the police on the phone what had just happened. When I hung up the phone, she asked what had happened and I told her I had just been robbed at knifepoint. Her exact response was, "I hope no one thinks I had anything to do with this."

Umm, what? So, long story short, they found the guy (I told them I recognized his voice) and he told them about her involvement in the setup. The setup was her texting him an "all clear" when only she and I were in the building. He didn't have to tell them, though; she quit the next day and stopped replying to my texts.

When I found out, I was heartbroken. This is someone who was around my kids regularly. I was diagnosed with extreme anxiety and PTSD after being robbed and still have flashbacks randomly. If someone comes up behind me and startles me, I panic.

The amount of money my life was worth to them? $440.

The punishment they received? He got 2 years in jail and 1 year of probation.

She got 1 year of probation.

I had to quit the job I had held for over a decade because I couldn't stand being in there anymore.
---
This all starts out poorly by me following my boyfriend to the same college he went to (he was a year older; I still don't regret it after all as I loved my school and everything else about those 4 years). We were a bit off and on that first semester I was there (again, red flags!). My new across-the-hall-mate in my dorm became my "best friend." She and my boyfriend didn't really like each other, but it wasn't a huge deal; it was just a personality clash, and she didn't like how he treated me with the off and on crap.

Our school had a winter term in January. My boyfriend lived off-campus so he was there, and my best friend was taking a class; I was home. My best friend was lonely and didn't know many other people on campus for the winter term, so I told her to hang out with the boys in my boyfriend's fraternity house, whom she had been friendly with. So, they all started hanging out.

And by that, of course, I mean they started hooking up.

I got back to school and I immediately could tell things were weird with my best friend (unbeknownst to me at the time, my boyfriend had had basically our entire relationship to practice covering his tracks and was a smooth and practiced liar by this point). Within a couple of weeks, it all came out that they had been hooking up and my best friend actually told me, "You know how much I've wanted a boyfriend; if you were a good friend, you'd let me have him." (Why I still wanted to date him at this point is beyond many, many people's comprehension, including mine, but it did involve a dog that I was beyond attached to).

I do fault them both equally, and did at the time too; I don't remember being mad at either of them as much as I was just devastated. He was apologetic from the start; she was mean and manipulative (again, not trying to say it was the other woman's fault, just explaining how it all went down). It totally sucked and I felt so betrayed by both of them. Unsurprisingly, I have had a lot of trust and loyalty issues since.
---
I had a friend from high school until about 4 years ago (about 8 to 9 years total of friendship). He was a very close friend, and one day he confided in my boyfriend (now husband) and me that his roommate was moving out to live with his girlfriend and he wouldn't make rent that month. My boyfriend and I had an apartment lease ending, so we decided we could be of help and moved in (2 months before our lease was up, 2 rent payments). We lived there for about 2 months and found out we were pregnant and having a baby, which seemed like a happy scenario as the roommate had informed us he wished to turn over the lease for the house to us so he could move back in with his parents. It was a perfect 3-bedroom house with 2 bathrooms and plenty of space. The day before we were set to meet up with the landlord, we came home to an eviction notice on the door and all of the roommate's stuff was moved out. I called him, but there was no answer. I called the number on the eviction notice from the landlord and found out he lied and never told the landlord anything; he wouldn't even work with us at all, just said we had 30 days to get out. The roommate had been pocketing our rent money for months. We had 30 days to unexpectedly find a new place, pay first and last month's rent plus a security deposit, and move in the middle of a Michigan winter while I was pregnant. What a terrible person.

---
While freelancing on a sweet gig that came out of the blue, I found out that I would be working with Sean, a guy who was in my group at a former ad agency. Awesome, a friendly face.

Sean was a geek. No one liked him, and as his associate creative director (supervisor), I looked out for him. He seemed to try hard, and I didn't understand why everyone excluded him. During two rounds of layoffs, I went to bat for the guy and saved his job, promising to work with him. He was always busy, and soon after, I moved on to a new job. So I looked forward to working with him some more and proving those mean jerks from our old agency wrong.

While working this freelance job, I sensed something was wrong soon after it began. Sean had no ideas. None! He literally brought a blank pad in day after day. Excuses were that he was tired, the assignment confused him, etc. I was nervous, but I was stuck. So, since we were on a team, I shared my ideas, our only ideas, with him. We had to present an hour after lunch.

During lunch, I had to go to a doctor's appointment with my wife, who was seriously ill. On my way back to the office, the cab I was in had an accident. A jerk in a Lexus slammed into us. No one was hurt, but it totaled both cars. Further, I didn't feel comfortable leaving the cabbie, as he was foreign and spoke little English. The guy who hit us was ranting, so I stayed to give a statement to the police. I called Sean to explain and asked if he minded handling the meeting and asked him to relay my situation.

Then, this guy presented my work, claimed it was all his, and they sent me home because 'Sean nailed it.'

Salt in the wound? Took 9 months to get paid for the time I did put in. All along, I tried to explain, but no one believed me. He copied my notes in his own writing and submitted them as proof. As far as they were concerned, I was riding this guy's coat-tails. I coulda kicked his behind for a week without getting bored.

Two months later, he was found out when he tried it again. Dozens of former coworkers called to rub my nose in it. 'Still think we're just picking on Sean?' I learned that sometimes people are shunned because they deserve it.

---
I had a friend for 20 years. He called me at night to ask to borrow $3,600. It was for his last year of a degree and would get him a raise when he graduated. At the time, I was making quite a bit of money and had lots in the bank. He said he would pay me back in a year. Three years later, after the crash, he still had not paid me back and was constantly giving me lame excuses like he "needs three vacations a year" and "is saving to buy a house." My situation had changed, and he was still not only refusing to pay me back but still asking for favors and loans. I finally said I was broke, to which he replied, "You are stupid, I am never going to pay you back or help you out." I dropped him as a friend and have had very little contact with him since. He did hire my wife at a company he manages. I guess I should have seen this coming.

I had just gotten married and had two kids. Another time he said, "Your kids aren't starving!" He always just thought of himself. Could not care about anybody else. I guess I thought he was funny. Listened to his escort stories and finally enough was enough. The last time I talked to him as a friend, he was asking me to get him some marijuana. I said it was way out of my way. I was too busy. He said, "Too much to ask for, eh?" I said, "Well, what would you do for me?" When you grow up with a guy, it just seems it is too hard to recognize he isn't really a friend. Kept this inside for a while. Don't have any friends from high school anymore because they were all like this. Should have hung out with a better class, really.

---
My best friend of 12 years, we were living together. I trusted him with my life, I mean we grew up together, we even went to college together.

Turned out he was seeing my girlfriend of 3 years for 6 months before it dawned on me; I knew she was unhappy with the relationship.

I confided in him during those 6 months and he would play dumb to it and try to console me. How do you do that so well to a bro?

I mean thinking back on it, it should have been obvious to me, all the signs were there, but you just don't suspect your best friend.

In the end, she stole £1,000 from me and he stole my PS2, all my games and moved in with her. The day I came banging on her door, she answered the door with him, moving boxes everywhere and he had this cold stare on him and I was just in shock. I didn't know they had stolen from me at the time, so I just stood there in total shock, I turned around and walked away.

I didn't even look at her, I knew things were going south with her for a long time, but he really betrayed me and I couldn't believe it.

6 months later I got together with another girl, spent an incredible year with her and forgot about everything that happened. She was the love of my life, but it went south with her too and unfortunately she died of a seizure and only now (5 years since) have I gotten over that.

Not much luck with women I guess.

I imagine most stories will be similar to mine, but man, just can't believe your best bro could do that. It really crippled me for the longest time.
---
Several years ago, I moved to Florida. Almost immediately after I met a friend. He was a great guy (so I thought) and we would constantly hang out, he would show me around the town, this state, etc.

About a year and a half into knowing him, he stole a couple of my credit cards and racked up really big bills. Unfortunately for me, and I know this now but didn't then, I simply thought calling the credit card company to report your card stolen and canceling the account also vacated the charges. That's not true; you actually have to formally contest the charges separately, and you only have 60 days.

By the time I realized this, it was too late. I tried, in vain, to semi-reconcile with him to try to get a payment plan. He begged me not to call the police. I regret now that I didn't. I did believe that he had fallen on hard times, and that he would get back on his feet and try to repay me. That didn't happen. Although, later on, he did get arrested for something else and was put on probation.

I figured that would have been the best time to try to recoup the money lost (I had fallen behind on these payments and my credit was starting to suffer; I had to drop out of college because of that). I did try instead to take him to small claims court. I do realize that civil court is not criminal, but with him now being a convicted felon, I might stand a better chance at looking much better.

Instead, when we got to court, he denied everything, said everything was a gift, and completely slandered me in open court. Why he was allowed to get away with it is beyond me, but that case was dismissed; I got nothing.

My credit suffered for years because of that. I eventually did save up enough money to file for bankruptcy just to get rid of that debt that I couldn't repay (nor should I have had to). I have never really forgiven him for what he did to me. As far as I know, he still lives around; luckily, I haven't seen him in several years. I don't know what I would even say if I ever did encounter him. The bankruptcy did eliminate that debt, so I cannot (and will not) ever say he owes me anything monetarily. However, he owes me a huge apology, but like I said, I would seriously doubt the sincerity of it and likely wouldn't accept it anyway. I think the best thing is as it is now: he just stays away from me.
---
In college, my best friend and I had an art class together with a guy I was hanging out with on the regular, getting to know each other to see if there was anything more there. He and I hung out, messed around, had fun, etc. Nothing formal or spoken just yet, but we communicated daily. We were more than friends, but not a dedicated couple.

One day I stopped by his house after a morning class for a reason that I forget. I knocked and got no answer, so I let myself in through the unlocked door (small Kansas town, nobody locks anything) so I could leave him a note.

Well, her purse was on the chair by the door. Nobody answered when I called out his name, or hers, even though his car and her purse were there. They were clearly together, which was just awful.

I got back at her though, almost 20 years later; she sent me a friend request on Facebook and I denied that woman. Take that, Jessica.
---
I had to go out of town for work for 6 weeks. It wasn't far enough that I couldn't come back every weekend.

My girlfriend at the time was secretly unhinged. It hadn't shown yet, but she was on a downward spiral. Two solid days together with five days apart wasn't good enough for her.

My best friend had a lot of girlfriends, so I would go to him for advice, to vent, you know, to keep it together, to have a buddy to talk to. He asked if he could talk to her about anything, and I said no, just give me advice. Fast forward to week 5. My girlfriend had a meltdown and called me saying she hated me, citing complaints I had made about her to my best friend, but way amplified from what I had said. I told her how much I loved her.

There was no way it could be my best friend. We'd been buddies for over a decade. We shared stories all the time. Somebody was playing games with me. I confronted him.

"I haven't said a thing to her," my friend told me. He blamed it on his unstable ex, and my girlfriend at the time confirmed it was her. She supposedly hacked his email, sending out-of-context logs of my complaints to my girlfriend "because she was worried about our relationship." I thought I could recover from this. I'm a good person, and it was clearly out of context, so I tried explaining everything to her. My friend was upset about his "unstable ex," saying, "She's messing with my relationship too, man." He was with a different girl, together for over a year, and despite their troubles, I believed he'd pull through. He expressed deep affection for her, wanting to marry her and declaring, "I'm tired of dating, this girl is the one."

I still went to my friend for advice. He told me to relax, that it would get better when I got back, and to concentrate on my work. I was naive.

It wasn't working. She said she couldn't handle me being away all the time, five days at a time. I drove five hours home every weekend and five hours back to work. She said she was "seeing somebody else to stay happy." Okay, go hang out with somebody else. You're still mine. I asked my best friend about it, and he said, "No way, man, she isn't. She can't give you a name, therefore she isn't. She's just messing with you, stay strong."

Fast forward. I got back, and I dealt with her completely unhinged attitude for a couple of weeks. She started to like me again. I was trying to do the right thing. I felt bad for leaving her, even though it wasn't that long.

There was no hack. There was no explanation. My best friend lied to my face. He was the "guy she was seeing," and he was doing loads of drugs. My best friend lied to my girlfriend and me to get her upset and dislike me so he could party with her, all while telling me he wanted to marry his current girlfriend and blaming all of my issues on one of his exes. His lies went on for weeks. I was upset, but he was still my best friend.

I found out the truth. "I'm sorry, man, I'm trying to keep my distance from your girlfriend now. Feelings got in the way two weeks ago," but nothing happened, he claimed. "By the way, she cheated on you right before your birthday." This is where I should have cut it off. But I was naive. I replied, "No, I'm trying to do the right thing. I love this girl, and I feel bad for how messed up she is, and everything else." (She was a dropout, no job, hurting, but could definitely climb out if she tried.) Him: "How do you do it, man? How do you stay strong?" He asked this a lot. I always explained I wanted to do the right thing and that I loved this girl. I was stupid. 

I tried to spend as much time with her as possible, while my best friend still talked about how he wanted to marry his girlfriend and how he told her everything that happened between him and my girlfriend. He wanted both of our lives to go back to normal, he said.

A few weeks later, things were still rough and she was treating me poorly, but it was slowly getting better. I was being honest about everything, and she claimed she was too, until she finally broke down and admitted that "seeing him" meant they were sleeping together the whole time I was away. He was lying to my face saying he wanted to marry his girlfriend. He was cheating on his girlfriend with mine, and both of them were lying to me the entire time. After I left town for two weeks feeling broken and distant, we fought because she had been with him behind my back since the very beginning, even while I was home.

He was my best friend, he said he wanted to help me, and he always offered help. He used everything I ever told him in confidence, while asking me for relationship advice, to turn her against me for months. All of the advice he gave me was designed to get her to dislike me more. "Make dinner for her, man, I'll give you a recipe for an awesome meat sauce, do it with a red wine." She hated meat sauce and red wine. He was with her and loading her up with free drugs after I had spent a year with her, all while lying to my face. He looked into my eyes and told me how bad he felt and told me how to fix it. They both lied to me.

Now they are both addicted to drugs, my ex is massively in debt, lives at home with her parents, and both work dead-end retail jobs. I got a $4,000 bonus check after my 6 weeks out of town. I'm still angry about it. My heart is pounding right now. I've lost a lot of faith in humanity and my once unconditional trust that people wanted to be good. Don't date a girl who is so insecure that she needs the attention of other guys at parties to be happy, but freaks out when you so much as glance at another girl, even if she is an old lady taking your order at a restaurant.

---
In grade 11, I met my first girlfriend. We were really great together. Even though I had to drive 45 minutes to meet her, I always looked forward to hanging out with her because she was awesome.

About 4 months into the relationship, however, my best friend started talking to my girlfriend. I didn't see anything wrong with it because I trusted him and her. Big mistake. One night, my girlfriend sent me an IM: "How could you do this to me?" My heart sank immediately. I had no idea what she was talking about. I kept asking what I did, but she kept saying I was just playing dumb. I called her on the phone to talk to her. She said that my best friend had told her that I had been flirting with another girl at my school.

No matter how hard I tried, I couldn't convince her otherwise. She broke up with me. About a month later, I went into the town where she lived. A friend and I were going to hang out with some mutual friends of my ex. We went to their house, and who was there but my best friend and my ex, with her sitting on my best friend's lap. Apparently, my "best friend" had asked her out a bit after she broke up with me, and she had said yes. She trusted him because he had told her those lies about me. To this day, this is the biggest betrayal I have ever felt.




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