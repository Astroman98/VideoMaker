import asyncio
import re
import os
import numpy as np
import textwrap
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy import concatenate_audioclips
import edge_tts
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


'''
def split_sentences(texto):
    """
    Separa el texto en oraciones sin dividir las comillas de cierre.
    """
    partes = []
    texto_actual = texto.strip()
    
    while texto_actual:
        match_punto_comilla = texto_actual.find('."')
        match_punto_interrogacion = texto_actual.find('?"')
        match_interrogacion = texto_actual.find('?')
        match_punto = texto_actual.find('. ')
        match_punto_salto = texto_actual.find('.\n')
        match_dos_puntos = texto_actual.find(': ')
        match_dos_puntos_salto = texto_actual.find(':\n')
        match_exclamacion = texto_actual.find('! ')
        
        # Mejorada la búsqueda de tres puntos seguidos de mayúscula
        match_tres_puntos_mayuscula = -1
        indice = texto_actual.find('…')  # Buscar el carácter unicode de puntos suspensivos
        if indice == -1:  # Si no encuentra el carácter unicode, buscar tres puntos
            indice = texto_actual.find('...')
            
        if indice != -1 and len(texto_actual) > indice + 1:
            # Verificar si hay un espacio después de los puntos suspensivos
            siguiente_char = texto_actual[indice + 1] if indice + 1 < len(texto_actual) else ''
            if siguiente_char.isspace():
                # Buscar la siguiente palabra
                resto_texto = texto_actual[indice + 2:].lstrip()
                if resto_texto and resto_texto[0].isupper():
                    match_tres_puntos_mayuscula = indice + 1
        
        indices = []
        if match_punto_comilla != -1:
            indices.append(match_punto_comilla + 2)
        if match_punto_interrogacion != -1:
            indices.append(match_punto_interrogacion + 2)
        elif match_interrogacion != -1:
            indices.append(match_interrogacion + 1)
        if match_punto != -1:
            if not texto_actual[match_punto-2:match_punto+1] == '...':
                indices.append(match_punto + 1)
        if match_punto_salto != -1:
            if not texto_actual[match_punto_salto-2:match_punto_salto+1] == '...':
                indices.append(match_punto_salto + 1)
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
    
    return [p for p in partes if p]

'''
    

'''
def split_sentences(texto):
    
    Separa el texto en oraciones usando como delimitadores:
      - Un signo de interrogación (?)
      - Un punto (.) que no forme parte de una elipsis ("...").
    
    return re.split(r'(?<=[?]|(?<!\.)\.(?!\.)(?!"))\s+', texto.strip())

'''

async def generate_audio_for_sentence(sentence, output_file, voz="es-US-AlonsoNeural"):
    """
    Genera el audio TTS para una oración y lo guarda en output_file.
    Opciones de voz: es-US-AlonsoNeural, en-US-ChristopherNeural, etc.
    También se añade un ajuste de velocidad (rate).
    """
    # En este ejemplo se añade rate="+7%" para aumentar la velocidad
    comunicador = edge_tts.Communicate(text=sentence, voice=voz, rate="+8%")
    await comunicador.save(output_file)
    print(f"Audio guardado: {output_file}")

async def generate_all_audios(sentences, seg_index):
    """
    Genera un audio para cada oración y devuelve una lista de rutas a los archivos generados.
    Se nombran de forma que se distingan por segmento.
    """
    audio_files = []
    # Usar el directorio específico para cada idioma
    audio_dir = os.getenv("AUDIO_DIR", "audio")  # "audio" como fallback
    os.makedirs(audio_dir, exist_ok=True)
    
    for i, sentence in enumerate(sentences):
        file_path = f"audio_esp/seg{seg_index}_sentence_{i}.mp3"
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
        new_duration = clip.duration - 0.7 if clip.duration > 0.7 else clip.duration
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
    target_resolution = (1920, 1080)
    # Abrir el video de fondo primero para obtener la resolución base
    main_bg = VideoFileClip("video/Gameplay1.mp4").resized(target_resolution)
    res = target_resolution  # Usar la resolución estándar en lugar de la del video
    
    # Definir silence_duration al inicio
    silence_duration = 2

    await generate_title_video(
    text="¿Cuál es la cosa más espeluznante o inexplicable que has visto y que nunca has compartido en ningún lado?",
    resolution=res
    )
    


    texto = (
       """ 

Cuando tenía unos 9 años, mi amigo y yo estábamos teniendo una pijamada. Sus padres estaban en una cena y su hermano estaba por ahí fumando. Alrededor de las 9 PM, sus padres llamaron para decir que la cena se había convertido en una salida de copas y que tardarían un poco más en volver. No le dimos mucha importancia y seguimos jugando Minecraft en la Xbox 360.

De repente, escuchamos que la puerta principal se abría. Era un sonido inconfundible, muy chirriante y casi siniestro. Pensamos: "Debe ser tu hermano" y seguimos jugando. Luego oímos pasos en el piso de arriba, justo encima de donde estábamos en el sótano. De nuevo, no nos preocupamos, ya que la cocina estaba justo sobre nosotros y supusimos que su hermano estaba allí con antojos por la hierba.

Pero entonces escuchamos otro par de pasos. Ahí empezamos a sentirnos un poco confundidos, aunque asumimos que podrían ser sus padres o algún amigo de su hermano.

Después, comenzó un sonido de rasguños en la puerta del sótano. Nos miramos como preguntándonos: "¿Soy solo yo o se escuchan rasguños?" (No tenían mascotas). Como yo era el mayor por dos meses, decidí ir a revisar. Abrí la puerta con cautela... pero no había nadie. Grité hacia arriba: “¡Jim, no nos asustas! ¡Para ya!”. No hubo respuesta. Volví a sentarme y seguimos jugando.

Momentos después, empezamos a escuchar rasguños en la ventana. En ese punto estábamos aterrorizados. Nos quedamos en nuestros asientos, uno mirando la puerta y el otro la ventana. Y de nuevo, los rasguños en la puerta. Esta vez tomé un bate de béisbol antes de abrirla... pero de nuevo, nada.

Decidimos atrincherarnos. Bloqueamos la puerta y apilamos cosas frente a la ventana. No volvimos a escuchar nada durante la siguiente media hora y, eventualmente, nos quedamos dormidos.

A la mañana siguiente, el padre de mi amigo bajó al sótano y tocó la puerta, tratando de entrar. Quitamos la barricada y él entró furioso.

—“¿Por qué demonios rasgaron la puerta mosquitera?”

Subimos con él y, efectivamente, la pantalla de la puerta principal estaba hecha trizas. Tratamos de convencerlo de que no fuimos nosotros y de que probablemente había sido el hermano intentando asustarnos. Pero lo que nos dijo a continuación nos dejó helados.

—“Jim no estuvo en casa en toda la noche. Lo dejamos en la ciudad con sus amigos.”

La casa de mi amigo estaba a media hora de la ciudad y ninguno de los amigos de su hermano tenía coche.

Nos miramos sin poder articular palabra. Sus padres nunca nos creyeron y nos hicieron pagar la mitad del costo para reemplazar la puerta del sótano (que también tenía muchas marcas de rasguños) y la puerta mosquitera.

Aún hoy, mi amigo y yo hablamos de esto cada vez que nos vemos.

---

Mi abuelo falleció hace varios años después de muchos años de diálisis. A medida que envejecía, nos dijeron que este tratamiento no duraría para siempre, que con el tiempo perdería efectividad y que eventualmente tendrían que suspenderlo. Tenía 83 años cuando falleció, siempre fue una persona en buena forma y saludable, y la diálisis lo mantuvo con vida unos años más.

Cuando enfermó, lo llevaron al hospital y le suspendieron la diálisis. Nos informaron que probablemente le quedarían entre 48 y 72 horas de vida. Así que toda la familia fue al hospital y nos turnamos para estar con él el mayor tiempo posible. Lo mantuvieron cómodo y le administraban medicamentos para asegurarse de que no sintiera dolor.

A medida que se acercaba el final, entraba y salía de un estado de lucidez, la mayor parte del tiempo en una especie de sueño en el que revivía recuerdos, murmurando y balbuceando. Cuando despertaba, se quedaba completamente absorto mirando un punto en el techo y hablaba con alguien de forma clara, aunque no sabíamos con quién, y luego volvía a dormirse. Esto ocurrió durante toda la noche.

Momentos antes de fallecer, se incorporó, miró fijamente a ese punto en el techo y empezó a hablar con más claridad de la que había tenido en todo ese tiempo. Sosteniendo la mano de mi abuela, se giró, la miró fijamente a los ojos y le preguntó si tenía algún mensaje que quisiera que él llevara a alguien. “¿Hay algo que quieras decirle a alguien?”, le preguntó. Cuando mi abuela le respondió que no, él se recostó, cerró los ojos y falleció pacíficamente.

La habitación entera quedó en silencio. Cada vello de mi cuerpo se erizó. No soy religioso, pero en ese momento sentí que debía ir directamente a una iglesia y empezar a rezar o algo por el estilo.

Mi madre, quien ha sido enfermera toda su vida, con muchos años de experiencia cuidando ancianos, me dijo que muchas personas, al morir, se concentran en un punto del techo y comienzan a hablar con "algo" que está ahí.

Que ella me dijera eso no me ayudó en lo absoluto. Bizarro.

---

Tengo dos historias que no puedo explicar en absoluto.

1: Mi mejor amigo vivía en una granja a unos 15 minutos del pueblo donde crecí. Para cuando tenía 18 años, ya conocía bien todas las carreteras alrededor de su casa. Una noche, volviendo de un ensayo con nuestra banda (tocábamos en un garaje), pasamos por una casa de campo y notamos que la luz del dormitorio de arriba estaba encendida. Esto era extremadamente raro... porque nadie había vivido allí desde que estábamos en la secundaria. La casa había quedado abandonada después de que un granjero se quitara la vida frente a su familia. Después de algo así, es difícil vender un lugar.

De todas formas, íbamos manejando cuando mi amigo me dijo que diera la vuelta. Así que lo hice y nos detuvimos en la entrada del camino. La luz del dormitorio seguía encendida, pero no había otras luces, ni vehículos, y la puerta seguía cerrada como si nadie la hubiera abierto en mucho tiempo. Lo más escalofriante… había alguien, o algo, allá arriba. La casa estaba tapiada y no vimos señales de que alguien hubiera entrado. Nos quedamos mirando por unos cinco minutos; lo que sea que estaba ahí adentro parecía estar paseando por la habitación. Luego, pareció girarse hacia la ventana, como si nos estuviera mirando. Eso fue suficiente para nosotros. Nos fuimos de inmediato.

Al día siguiente decidimos regresar y echar un vistazo más de cerca. Desde afuera, todo seguía tapiado. Así que, quién sabe qué era lo que habíamos visto.

Uno o dos años después, demolieron la casa. Un conocido mío trabajaba en la cuadrilla encargada de la demolición, así que le conté nuestra historia. Solo sacudió la cabeza y me dijo que no había forma de que esa luz hubiera estado encendida, ya que el servicio eléctrico de la casa había sido cortado hacía años.

2: Una noche, regresaba a casa de una fogata. Como había ido en mi propio auto, no había estado bebiendo. Estaba a unos pocos kilómetros del pueblo cuando, de repente, vi lo que parecía ser una mujer al costado de la carretera. Parecía que iba a correr hacia la carretera con las manos en alto, como si estuviera señalándome para que me detuviera. Por instinto, pisé los frenos con fuerza.

Cuando el auto se detuvo, no había nadie allí. Pero justo cuando arranqué de nuevo, una camioneta sin luces pasó volando por la intersección frente a mí sin detenerse. Si no hubiera frenado, me habría dado de costado con muchísima fuerza.

Llamé a la policía y reporté el vehículo por conducción peligrosa. A los días, me llamaron para decirme que habían atrapado a los tipos. Los tres estaban completamente borrachos y el conductor tenía la licencia suspendida.

Hasta el día de hoy juro que vi a una mujer en la carretera. No hay otra razón por la que habría frenado tan bruscamente. ¿Era un fantasma o un ángel? No lo sé, pero lo que fuera, posiblemente me salvó la vida.
---
Solía vivir en medio de la nada. El pueblo tenía menos de 200 habitantes.

Trabajaba de noche en una de las zonas metropolitanas, y el trayecto a casa era de unos 40 minutos, con aproximadamente 15 de ellos en un camino rural. A menudo pensaba que veía cosas en los campos (coyotes, ciervos, etc.), pero nunca les di demasiada importancia.

Pero… una madrugada, alrededor de las 3 AM, estaba camino a casa. Justo antes de llegar a mi calle, había un pequeño puente que tenía que cruzar. Cuando me acercaba, noté algo de un blanco perlado en medio de la carretera. Supuse que era un cisne y que se movería. Pero al acercarme más, me di cuenta de que los cisnes no son tan grandes.

Iba en una F-150 y lo tenía a la altura de los ojos. Cuando abrió las alas, cubrió ambos carriles de la carretera. Intenté esquivarlo, pero llegué a golpear parte de una de sus alas. Frené de golpe y di la vuelta. No había absolutamente nada. Se había esfumado sin dejar rastro. Nunca lo volví a ver.

Si era un pájaro, entonces era el maldito pájaro más grande que he visto en mi vida.
---
Estaba en la secundaria viendo televisión con mi mamá y mi papá. De la nada, mi papá me dice que cierre la puerta de entrada porque está sintiendo una sensación abrumadora de temor. Yo estaba acostado en el suelo frente al televisor, cerca de la puerta, y comencé a reírme incrédulo. Él se enojó conmigo. Al ver que hablaba en serio, me levanté y la cerré con llave. Seguimos viendo la televisión. Unos minutos después (quizás 10), el picaporte de la puerta empezó a girar lentamente. El sonido fue lo suficientemente fuerte como para que los tres nos volviéramos a mirar la puerta y viéramos cómo se movía. Nos miramos horrorizados. Mi papá preguntó: "¿Vieron eso?" Yo asentí. Poco a poco recuperamos la compostura y nos dimos cuenta de que debíamos levantarnos y mirar afuera. Pero no vimos nada porque estaba oscuro. Yo estaba aterrorizado, pero mi papá, por alguna razón, abrió la puerta para asegurarse de que no hubiera nadie. No tengo idea de por qué lo hizo, ya que eso nos exponía a cualquier persona que estuviera afuera. Pero no había nadie en el camino de entrada. Para cuando reaccionamos, la persona (o personas) ya se habían ido.

Unas dos o tres horas después, escucho gritos de ayuda y golpes en la puerta corrediza trasera. Era el hijo menor de nuestros vecinos (de unos 11 años). Eran gente increíblemente amable. El niño estaba aterrorizado, llorando, suplicando que llamáramos a la policía. Habían sido víctimas de un robo e invasión de hogar. Los tuvieron como rehenes todo el tiempo desde que nuestro picaporte giró. Si mal no recuerdo, fueron cuatro hombres (o quizás tres, no estoy seguro) quienes entraron por su puerta principal. La tenían abierta, solo con la puerta mosquitera cerrada. Pasaron cosas horribles, pero todos sobrevivieron.

Mi papá no era psíquico, pero esto es, sin duda, lo más extraño que he presenciado. Se lo he contado a compañeros de cuarto que me preguntan por qué siempre cierro la puerta con llave al entrar a casa, incluso en pleno día. Todavía me pone la piel de gallina. Este evento me convenció de que hay algo más allá de lo que podemos ver, algo espiritual. ¿Por qué mi papá sintió ese miedo? ¿Por qué lo tomó tan en serio como para hacerme cerrar la puerta? Y lo peor de todo: ¿por qué, a pesar de eso, no llamamos a la policía? Ojalá hubiéramos hecho algo que cambiara el destino de nuestros vecinos. Desde entonces, cuando alguien me dice que tiene un mal presentimiento, lo tomo en serio.

---
Han pasado casi 10 años y aún no tengo ninguna explicación que se acerque siquiera a lo que ocurrió esa noche.

Mi mejor amiga y yo estábamos teniendo una pijamada en casa de su abuela y disfrutando del ático recién renovado, que se suponía iba a convertirse en su pequeño apartamento de adolescente. Todo era nuevo: muebles, un enorme y cómodo sofá, estanterías blancas y rosas fijadas a la pared, todo perfectamente limpio y ordenado.

La noche transcurrió como cualquier pijamada entre dos chicas de 15 años: pintándonos las uñas, viendo DVDs y chismeando sobre lo que pasaba en la escuela. Ya eran como las 3 AM cuando decidimos dormir. Dejamos el ático y nos fuimos a la cama en la habitación contigua.

Solo unos minutos después, escuchamos un rasguño leve, seguido de un golpe ensordecedor. Venía claramente de la habitación que acabábamos de dejar.

Fuimos a ver y ahí estaba: una de las estanterías, que había estado firmemente atornillada a la pared, yacía en el suelo... pero no justo debajo de donde estaba antes. No se había caído simplemente. No.

Estaba a casi 4 metros de distancia de la pared.

Pero lo más aterrador fue cómo se veía la pared: los agujeros donde estaban los tornillos no parecían rotos por el peso. Parecía como si algo hubiera agarrado la estantería y la hubiera arrancado con fuerza, desgarrando la madera y el concreto al que estaba fijada.

El suelo tenía una abolladura de casi 2 centímetros de profundidad justo donde la estantería había aterrizado.

Todavía me da piel de gallina cada vez que lo recuerdo.
---

Trabajaba en una tienda minorista en una zona bastante peligrosa. Había una señora que, obviamente, era o había sido una consumidora habitual de drogas. Debía tener entre 50 y 60 años. Era bien conocida en la cuadra por estar "loca", pero me visitaba todo el tiempo y me decía que me encontraba lindo. Era realmente extraño porque parecía una adicta, pero se comportaba como una adolescente a mi alrededor. Trataba de ser amable con ella porque tenía fama de ser volátil.

De todos modos, en Nochebuena preparó una cena navideña completa para mí, que según ella era comida casera guyanesa, y también me regaló un set de colonia.

Cuando se estaba yendo, de repente se agachó en el suelo, levantó la mano y comenzó a soltar una carcajada. Sí, una carcajada, que luego se desvaneció en una risa más suave.

Nunca la volví a ver.

---

Solía vivir en una zona rural de Texas y una vez iba manejando por un camino FM (que es una carretera que conecta áreas rurales con la ciudad) en medio de una niebla espesa. Conducía una camioneta vieja y avanzaba a unos 30-40 km/h porque no podía ver muy lejos (y menos mal que iba tan lento).

Al dar una vuelta en el camino, vi a través de la niebla una figura enorme y encorvada cruzando la carretera. Reduje la velocidad, me acerqué un poco para pasar y vi lo que era el cerdo más grande que había visto en mi vida. Fácilmente pesaba unos 180 kilos. Estaba muerto (seguramente había destrozado el vehículo que lo golpeó) y, arrastrándolo hacia el lado de la carretera, había un perro absolutamente gigantesco y de pelaje blanco y desgreñado.

Ese perro… Iba en una camioneta y cuando levantó la cabeza, me miró directamente a los ojos, nivelado conmigo. Me quedé completamente paralizado, tan sorprendido que detuve la camioneta y solo observé. Después de unos segundos (que parecieron una eternidad), bajó la cabeza, arrancó un pedazo del cerdo y siguió arrastrándolo fuera del camino.

Analizando lo que vi: ese perro era lo suficientemente inteligente como para mover el animal que quería comer, lo suficientemente grande y fuerte como para arrastrar un cerdo de casi 180 kilos sobre el pavimento y lo suficientemente alto como para mirarme a los ojos mientras yo estaba en una camioneta. Nunca olvidaré esos ojos. Tenía el pelaje blanco pero manchado de lodo, una cabeza enorme y cuadrada, y una larga cola similar a la de un lobo. Se parecía un poco a un Gran Pirineo (que son comunes por allí), pero con la cabeza de un San Bernardo y el doble de su tamaño. Sus ojos brillaban en un tono amarillo intenso.

No tengo idea de si era un perro de granja mutante, un espíritu, un lobo o qué, pero espero no volver a verlo jamás.

---
Estaba en la secundaria y mi hermana en la preparatoria. Ella había salido con sus amigos. Bajé a la cocina a buscar un bocadillo y mis padres estaban en la sala. Comencé a llorar y a decir que estaba preocupada por mi hermana. Aún no tenía un teléfono celular, así que no podíamos hacer mucho. Resultó que había tenido un accidente. Estaba bien, pero fue aterrador.

Unos meses después, estaba en la escuela y de repente empecé a llorar. Llamé a mi madre y le dije que llamara a mi abuela. Mi abuela no respondió, así que llamaron a la vecina. La vecina fue a revisar y la encontró en la bañera con el pie roto. Había estado allí toda la noche.

Desde entonces, siempre confío en mi instinto.
---
Hace mucho tiempo, cuando estaba en la primaria, mi amigo y yo fuimos a la escuela un domingo para explorar. Llegamos en la madrugada y, al ser domingo, no había nadie.

Caminábamos por un pasillo en el primer piso cuando, de repente, escuchamos un estruendoso ruido arriba de nosotros. Era exactamente el sonido de arrastrar una silla o una mesa por el suelo, pero sonaba como si hubiera múltiples aulas llenas de mesas y sillas moviéndose al mismo tiempo. Era fuerte. Muy fuerte. Y totalmente repentino. No había razón alguna para que alguien estuviera en la escuela moviendo docenas de mesas y sillas solo a las 6 AM un domingo. Nos quedamos paralizados, nos miramos por un segundo y salimos corriendo.

Cuando salimos de la escuela, mi amigo me preguntó si había escuchado a una mujer gritar en el pasillo. Le dije que no.

Él tampoco había escuchado los sonidos de arrastrar muebles.
---

Estaba manejando de regreso a mi dormitorio en Florida. Soy de Carolina del Norte, así que era un viaje nocturno completo. Iba por la I-95 a unos 130 km por hora, simplemente conduciendo, cuando de repente comencé a derrapar y rápidamente perdí el control de mi camioneta.

Sentí cómo se estrellaba contra la base del puente y vi toda la parte delantera aplastarse contra la pared.

En ese mismo segundo, sentí que cada hueso de mi cuerpo se rompía y lo último que vi fue la bolsa de aire desplegándose mientras mi cara se estrellaba contra ella.

Inmediatamente después de eso, desperté lanzado fuera de mi cama y golpeé la baranda a los pies de esta.

Mi compañero de cuarto estaba ahí, me agarró y se aseguró de que estuviera bien. Me dijo que simplemente estaba durmiendo y, de la nada, me había incorporado de golpe y me había estrellado contra la baranda.

Estaba totalmente conmocionado, porque se sintió tan real que insistí en salir a revisar mi camioneta. Tenía que comprobar que todo estaba bien.

Salimos al estacionamiento, y la camioneta estaba perfectamente bien. Nada estaba mal.

Eran cerca de la medianoche, y mi compañero estaba preocupado por lo intenso que fue para mí. Me sugirió que fuera a hablar con un consejero en la mañana.

Acepté ir, y mientras caminábamos de regreso a la residencia, su teléfono comenzó a sonar.

Era su padre. Estaba llorando, apenas podía hablar sin romperse por completo. Le dijo a mi compañero, entre sollozos, que su hermano había sido encontrado sin vida dentro de su vehículo, debajo de un paso sobre nivel, cerca de su casa en Misuri.

Mi compañero, en shock, murmuró algo sobre que no podía creer que su hermano estuviera conduciendo rápido, porque siempre manejaba despacio. También mencionó que sus llantas estaban bien la semana pasada cuando las revisó.

El padre, todavía llorando, de repente se detuvo en seco y preguntó con voz entrecortada: "¿Cómo sabes que fue por las llantas? ¿Cómo sabes que estaba acelerando?"

Nunca le dijimos nada a su madre. Su padre no tomó bien la explicación cuando intentamos contarle.

---
Mi esposo y yo estábamos caminando por el centro de Seaside, Oregón. Era finales de diciembre, así que el lugar estaba bastante vacío y muchas tiendas estaban cerradas, ya que además era domingo por la mañana.

Entré en una tienda (Celtic Store) y estaba llena de gente, pero en cuanto crucé la puerta, todos se quedaron en silencio. Tan pronto como puse un pie dentro, sentí un peso en el cuerpo y como si todo a mi alrededor estuviera borroso. La mujer detrás del mostrador me dijo algo y trató de darme un colgante. En ese instante, todo se volvió oscuro y angustiante, sentí una opresión en el pecho, una sensación de negro absoluto. Nunca en mi vida había sentido tanta oscuridad. De alguna manera, logré salir corriendo, y tan pronto como pisé la acera, me sentí completamente normal, como si nada hubiera pasado.

Mi esposo quiso entrar porque le encantan ese tipo de lugares, y fue entonces cuando me di cuenta de que no tenía idea de por qué no había entrado conmigo en primer lugar. Estábamos recién casados y habíamos estado caminando con su brazo alrededor de mí, así que me pareció muy extraño. Solo le dije que no íbamos a entrar y lo arrastré lejos de ahí.

Desde entonces, he regresado a Seaside muchas veces, pero la tienda ya no está y no puedo encontrar el lugar donde recuerdo que estaba.
---

Hace aproximadamente un año, iba sola en el auto por la autopista. Era un día soleado y despejado. Manejaba a unos 20 metros detrás de un tráiler. Bajé la mirada por un segundo —literalmente un segundo— para ajustar el volumen del estéreo. Cuando volví a mirar hacia adelante, el cielo se había vuelto completamente gris y una neblina flotaba en el aire.

El tráiler frente a mí se había volcado de lado y estaba deslizándose rápidamente hacia atrás, directamente hacia mi auto.

No tenía tiempo para esquivarlo. Seguía a 105 km/h, había un auto detrás de mí y no podía frenar de golpe sin que me chocaran. Mi respiración se cortó, sentí el pánico subir y fui completamente consciente de que estaba a punto de morir.

En ese instante, vi el rostro de mi hija en mi mente y sentí el peso de saber que no la vería crecer. Fue la peor sensación que he experimentado en mi vida: terror, pánico, devastación, desesperación, remordimiento… 

Parecía que el tiempo se había ralentizado mientras veía el tráiler deslizarse hacia mí. Intenté respirar—creo que para gritar—y parpadeé.

De repente, el tráiler estaba de pie en su carril, a la misma distancia que antes, manejando con total normalidad.

El cielo estaba soleado. La neblina había desaparecido.

Era como si nada hubiera pasado.

Mis manos seguían apretando el volante con tanta fuerza que me dolían. Mi corazón latía descontroladamente. Empecé a temblar sin control y me orillé en la carretera, sintiéndome a punto de vomitar.

Llamé a mi esposo y le conté lo que había sucedido. Me sugirió que tal vez había alucinado o que había pasado por un banco de niebla y que la luz del sol se había reflejado de tal manera que creó un efecto óptico, haciéndome creer que vi algo que no estaba ahí.

Pero no había niebla en ninguna parte después de que parpadeé. No había nada en mi espejo retrovisor, solo el auto que había estado detrás de mí.

Puedo recordarlo con total claridad.

No estaba enferma. No estaba tomando medicamentos. Jamás he alucinado.

No tengo ninguna explicación lógica. Pero hay una parte de mí que cree que morí ese día en otra realidad, y que la experiencia fue tan intensa que la viví también en esta.

O que el universo me estaba enviando una advertencia.

Sé lo ridículo que suena, pero no sé cómo más reconciliar lo que viví.

Soy una persona lógica, escéptica, y esto me sacudió hasta la médula.

Nunca más he vuelto a manejar detrás de un tráiler, jamás.
---

Mi abuela falleció de leucemia hace dos años. Somos budistas, y parte de nuestra creencia es que el alma del difunto permanece en el mundo de los vivos durante 49 días antes de cruzar al más allá.

Una semana después de su funeral, mi familia se reunió para cenar en el restaurante de mis padres (tenemos un restaurante chino). Dejamos un asiento y un lugar en la mesa para mi abuela. Yo estaba sentado junto a su sitio, así que fui quien llenó su plato con los diferentes platillos. Me aseguré de ponerle un poco de cada comida para incluirla en nuestra cena familiar.

Esa noche tuve un sueño en el que estaba de vuelta en el restaurante. Todo era exactamente igual que en la cena de esa noche, excepto que esta vez vi a mi abuela.

Estaba sentada en el lugar que habíamos dejado vacío para ella y vestía la misma ropa con la que la habíamos preparado para el ataúd. Observaba a toda la familia y sonreía. Recuerdo con mucha claridad la expresión en su rostro: estaba feliz y orgullosa del legado que había dejado, pero detrás de esa sonrisa había un leve toque de tristeza.

Cuando la vi, traté de llamar la atención de mi familia, pero nadie podía oírme. Me giré de nuevo hacia mi abuela y ella me hizo una señal para que guardara silencio y me dijo que disfrutara la cena.

En ese momento desperté.

Fue una experiencia muy extraña, pero al mismo tiempo me dio cierto sentido de cierre. Todo pasó tan rápido una vez que el doctor comenzó la quimioterapia.
---
Salí a andar en bicicleta tarde en la noche. Era el momento justo en el que el sol se había puesto, pero las luces de las calles aún no se habían encendido.

Estaba pedaleando por una carretera que conozco bien.

Sabía que más adelante había una curva ciega. La gente normalmente va muy despacio en esa curva.

Mientras pedaleaba, la curva estaba aproximadamente a 300 metros de distancia.

De repente, en mi mente apareció una imagen de mí mismo tirado en el suelo, cubierto de sangre.

Me detuve en el costado del camino. Sentí como si la frase "AUTO ROJO" estuviera siendo gritada en mi cerebro.

Mi cabeza empezó a dolerme. Me sentí enfermo, con ganas de vomitar.

No sabía qué pensar. Estaba sorprendido por la imagen de mí mismo tirado en sangre.

Un segundo después, un Hyundai rojo pasó a toda velocidad por la curva ciega.

El camino detrás de él estaba vacío, así que debía ir a unos 70-80 kilómetros por hora.

Vi cómo las llantas chirriaban al tomar la curva. En ese momento lo entendí: si no me hubiera detenido, me habría golpeado a alta velocidad y habría quedado tirado en el suelo, tal como lo vi en mi cabeza.

Esto nunca me ha vuelto a pasar.

No tengo idea de qué fue esto. Es inexplicable.

---

Hace aproximadamente dos años, cuando tenía 16 y recién había comenzado a conducir, estaba regresando de un ensayo de banda alrededor de las 10 de la noche. No había nada inusual esa noche, el mismo recorrido de siempre con el mismo pueblo a mi alrededor. Los caminos que se bifurcaban ofrecían varias rutas para llegar a casa, pero normalmente usaba solo dos: un camino bien iluminado a través de los suburbios o un camino trasero más oscuro y rápido. Como ya era tarde, elegí el camino más rápido y oscuro.

A lo largo de este camino rodeado de bosque, hay una sola luz distintiva, un poste con una lámpara de calle brillante en una intersección de cuatro vías justo en medio de mi trayecto. Esta es la única, y repito, única lámpara, intersección o señal en todo el camino. Como de costumbre, aceleré al pasarla, leyendo en voz baja el nombre de la calle claramente iluminado por la lámpara: "Rogers Trail". Seguí mi camino, sabiendo que la próxima parada era mi casa… o eso creía.

Más adelante en el camino, vi otra luz de calle acercándose. Frené, pensando que había tomado un giro equivocado o algo así. Al acercarme, miré bien el nombre de la calle para orientarme. Mi mandíbula cayó al leerlo: "Rogers Trail".

Pasé lentamente por la intersección por segunda vez, mi mente corriendo, tratando de comprender lo que estaba sucediendo. Eran las 10:30 y solo quería llegar a casa. Sacudí la cabeza, lo ignoré y aceleré por la carretera… solo para encontrarme con otra luz de calle y, una vez más, el mismo letrero: "Rogers Trail".

La misma intersección, la misma calle, la misma señal que antes.

En este punto, me preguntaba si siquiera estaba despierto. Seguí conduciendo, viendo la misma intersección unas seis o siete veces más, antes de finalmente llegar a casa alrededor de las 11:15.

Le dije a mis padres que había salido a cenar con algunos amigos y me fui directo a la cama.

He pensado en compartir esta historia antes, pero para la mayoría de la gente sonaría como un montón de tonterías. No busco que me crean, pero puedo asegurarles que esto realmente sucedió, y hasta el día de hoy no tengo ninguna explicación.

---
Tenía una historia hace un minuto, ahora tengo dos.

La primera historia ocurrió hace unos diez años, cuando vivía con unos amigos y sus cuatro hijos. Una noche estaba cuidando a los niños mientras mis amigos tenían una cita. Era alrededor de las 9 PM, los niños ya estaban tranquilos y estábamos en la sala viendo televisión. Me levanté para ir a la habitación principal a buscar algo para uno de ellos. No estuve fuera más de 10 o 15 segundos, pero cuando regresé, el niño más pequeño, de solo 10 meses y apenas capaz de gatear, había desaparecido de la sala.

En ese momento, escuché su grito desesperado y seguí el sonido a través de la cocina y el comedor hasta una habitación trasera, donde estaba sentado en el suelo, en medio de la oscuridad total, gritando aterrorizado. Los otros niños, de 6, 4 y 2 años, aparentemente no se habían movido del lugar en los segundos que estuve ausente y no pudieron darme ninguna explicación. Como si el evento en sí no fuera lo suficientemente aterrador, todo se vuelve aún más escalofriante al recordar que el abuelo de los niños murió en esa misma habitación el año anterior.

Mi segunda historia es más corta, pero graciosa. Ocurrió justo antes de empezar a escribir esto. Estoy acostado en mi oficina, leyendo todas estas historias, y es seguro decir que ya tenía esa sensación de que algo no estaba bien. Después de leer una particularmente espeluznante, sentí la necesidad de echarle un buen vistazo a la habitación, solo para asegurarme de que nada estuviera acechando en las sombras.

Lo último que miré fue el monitor de bebé, a solo unos centímetros de mi cara, en la mesita de noche. En la pantalla, mi hijo de 6 meses estaba completamente despierto, mirando directamente a la cámara en completo silencio.
---
Cuando tenía 20 años, visité una ciudad en Italia que tiene varias torres medievales que se pueden escalar. Mi novia no quería subir ninguna, así que subí a una por mi cuenta y, en ese momento, era la única persona haciéndolo. Era un día soleado cuando entré a la torre. Había una escalera que rodeaba el borde de la estructura y no tenía ventanas.

Subir la torre me llevó, como mucho, cinco minutos. Al llegar a la cima de las escaleras, había una escalera de mano y una trampilla que conducía al techo de la torre. Cuando la abrí, descubrí que el clima había cambiado drásticamente: el cielo estaba nublado y amenazante. No recuerdo si había truenos, pero realmente me preocupaba la posibilidad de un rayo, estando en la cima de una torre tan alta con ese clima. Salí con cautela solo para echar un vistazo antes de bajar de inmediato.

El techo estaba rodeado por una especie de "jaula" de barras metálicas diseñadas claramente para evitar que alguien se cayera o saltara. Escuché un trueno y vi electricidad arqueando entre algunas de las barras. No fue un rayo cegador, sino más bien un arco eléctrico. En ese momento, pensé que la torre estaba a punto de ser alcanzada y descendí lo más rápido que pude.

Al llegar al fondo, me sorprendió encontrarme nuevamente con un clima soleado y un cielo completamente despejado. Mi novia notó que estaba conmocionado y se sorprendió aún más cuando le dije que había visto lo que creía que era un rayo. Para ella, el clima no había cambiado en absoluto mientras yo estaba en la torre.

He intentado contar esta historia un par de veces, pero es demasiado extraña como para esperar que alguien la crea. No tengo ninguna explicación lógica.

Soy una persona escéptica cuando se trata de lo paranormal, no soy religioso y nunca he tenido otras experiencias "extrañas" como esta. En resumen, no soy el tipo de persona a la que "le pasan cosas espeluznantes". Y, sin embargo…
---
Hace varios años, estaba usando un sitio de chat en línea y comencé a hablar con una mujer que decía vivir a unos 80 kilómetros de mí. Estuvimos conversando de manera amena durante un par de días, pero en el tercer día, un sábado por la noche, noté que algo en ella parecía diferente. Había algo que no estaba bien, pero no podía identificar qué era exactamente. Me explicó que estaba bebiendo, y asumí que ese era el motivo de su melancolía.

Seguimos hablando y encendió su cámara para que pudiera verla bebiendo mientras charlábamos. Con el paso de un par de horas, su estado de ánimo parecía oscurecerse cada vez más y se mostraba angustiada, aunque dudaba en darme detalles. Se ausentó por unos 30 minutos y, cuando regresó, parecía más ebria y aún más angustiada. Esta vez, tenía un montón de pastillas en la mesa frente a ella. Me dijo que no podía seguir adelante y comenzó a tomarlas una tras otra. No tenía idea de qué medicamento era.

Seguía ingiriendo más y más pastillas, y su habla se volvía cada vez más arrastrada. De repente, me vi en una posición terrible. ¿Estaba viendo a alguien quitarse la vida en una transmisión en vivo sin poder hacer nada? Solo tenía un nombre y una ciudad, datos que fácilmente podrían ser falsos.

Hice la excusa de que necesitaba ir al baño y, aprovechando la oportunidad, llamé a la Policía local y les expliqué la situación. Tomaron los detalles que tenía y me pidieron que volviera a la conversación para intentar mantenerla hablando y obtener más información.

Un oficial de civil llegó a mi casa y, mientras yo seguía en el chat con ella, revisó los registros de nuestras conversaciones en su computadora portátil. Para entonces, su voz ya era prácticamente incomprensible y, en algún momento, la cámara se movió, haciendo imposible ver lo que estaba pasando. Poco después, la conexión se perdió.

No tenía idea si todo esto era real o un engaño. El oficial permaneció en contacto con su estación de policía mientras daba la información que pudo recopilar, y luego se retiró, dejándome sumido en mis pensamientos.

A la noche siguiente, recibí una llamada de la estación de Policía local para agradecerme. Habían logrado rastrear su ubicación a través de su dirección IP y pudieron asistirla a tiempo. Resultó ser un intento genuino de querer quitarse la vida. Fue trasladada al hospital y, posteriormente, ingresada para recibir tratamiento.

---
Cuando mi hija era muy pequeña (3-4 años), estábamos de vacaciones en familia en un albergue dentro de un parque estatal. Nuestra habitación tenía vigas de madera expuestas en el techo para combinar con la decoración (dato importante más adelante). Se suponía que era la hora de la siesta para mi hija, pero estaba jugando tranquilamente sola y charlando mientras mi esposa y yo leíamos en la otra cama.

De repente, mi hija se volteó hacia mí y me pidió un pedazo de cuerda. Le pregunté por qué lo necesitaba y, con total naturalidad, respondió: "Es para mi amiga, la niña morada en el techo".

Mi esposa preguntó: "¿Qué amiga?" y mi hija contestó: "He estado hablando con la niña morada que está colgada de esa madera allá arriba" <señalando la viga del techo>. "Ella me pidió otro pedazo de cuerda".

Basta decir que la hora de la siesta se terminó de inmediato y salimos rápidamente de la habitación.

---
Mi suegra falleció a los 92 años. Durante los preparativos del funeral, mi esposo mencionó que su madre había expresado el deseo, poco antes de morir, de que dos antiguos vecinos (de un lugar donde había vivido hacía más de 50 años) asistieran a su funeral. Mi esposo le dijo que haría lo posible, pero era poco probable que aún vivieran allí y no estaba seguro de cómo encontrarlos, ya que tenían nombres hispanos muy comunes.

Al día siguiente de su fallecimiento, mi esposo viajó al antiguo vecindario de su madre, pero, como era de esperarse, los vecinos se habían mudado hacía mucho tiempo y nadie sabía dónde encontrarlos.

El domingo antes del funeral, mi esposo y yo asistimos a misa en la iglesia de su infancia, la misma iglesia desde la que su madre había pedido ser enterrada. Ninguno de los dos había ido a esa iglesia en décadas. Nos sentamos cerca de la parte trasera.

Después de que comenzó la misa, un hombre entró y se sentó en la banca justo frente a nosotros. En ese momento, mi esposo hizo una oración a su madre, pidiéndole perdón por no haber podido encontrar a los vecinos.

Durante la misa, hay un momento en el que los feligreses se dan la mano en señal de paz. Cuando el hombre de enfrente se giró para saludarnos, se quedó sorprendido y llamó a mi esposo por su nombre. Era el hijo de los vecinos que mi esposo había estado buscando. Mi esposo ni siquiera lo reconoció, pero él sí lo reconoció a él. Resulta que había estado visitando a sus padres en su nueva casa ese fin de semana y, en el último momento, decidió ir a misa antes de regresar.

Intercambiamos información y, tal como su madre había pedido, sus vecinos estuvieron presentes en su funeral dos días después. Si no hubiera estado allí, no lo habría creído.
---
Cuando tenía alrededor de ocho años, mi familia fue a un campamento cerca de un lago. Fuimos con varias otras familias y ellos también llevaron a sus hijos. Una de las cosas que yo hacía con otro niño era buscar cangrejos de río en las áreas poco profundas. Mientras buscaba, empecé a aventurarme un poco más lejos hasta que el agua me llegaba a la cintura. El agua no era completamente clara, pero tampoco estaba turbia. Podía ver el área más pálida de la orilla y la zona más oscura donde el agua se volvía más profunda, aunque en ese momento no sabía que significaba eso.

Di un paso en el área más oscura y profunda y comencé a caer. Justo antes de hundirme, un brazo pálido y delgado agarró mi pierna y me empujó de vuelta a la parte poco profunda. Solo vi el brazo mientras se hundía nuevamente en el agua antes de salir corriendo de regreso a la orilla. Lo recuerdo con total claridad, pero nunca se ha encontrado nada en ese lago, ni cuerpos, ni ahogamientos, nada. Mis padres siguen pensando que me lo inventé.
---
Solía vivir en una casa con dos compañeras de cuarto, a las que llamaremos Anna y Erica. Yo vivía en el segundo piso, mientras que Anna y Erica vivían abajo. Todas las noches escuchaba un "thud, thud" proveniente del piso de abajo. Siempre que investigaba, el ruido venía de la habitación de Anna. Pensé que estaba haciendo burpees o ejercitándose por la noche (lo cual me parece una suposición tonta ahora que lo pienso). Nunca hablé con Erica sobre eso porque creía que era cosa mía y, al estar en el segundo piso, realmente no me molestaba.

Dos años después, nos mudamos a otra casa con otra compañera más. Esta vez, Anna, Erica y yo compartíamos el mismo piso en la parte de arriba. Ahora escuchaba el "thud, thud" aún más fuerte. Me acerqué a la puerta de Anna y sonaba como si se estuviera golpeando contra la pared, murmurando y llorando o riéndose. También noté que cuando salía de su habitación, dejaba las sábanas esparcidas por el suelo.

Le pregunté a Erica al respecto y me dijo que ella también lo escuchaba. Con el tiempo, Anna empezó a quedarse más en la casa de sus padres, pero cada vez que regresaba, volvíamos a escuchar el mismo ruido. Cuando comenzamos a preguntarle más seguido al respecto, daba excusas como "estaba moviendo muebles" o "la puerta de mi balcón se estaba abriendo con el viento".

Después de que la cuestionamos varias veces, prácticamente dejó de vivir con nosotras y solo pasaba por la casa una vez al mes para recoger ropa. Fue algo muy extraño. No creo que alguna vez obtengamos una explicación.
---
Cuando tenía cinco años, mi hermana gemela idéntica y yo contrajimos fiebre escarlatina. Somos de Estados Unidos, pero el trabajo de mi padre nos había trasladado temporalmente a la India, y no estábamos acostumbradas al agua y la comida de allí. Hacia el final de la fiebre, ambas caímos en coma.

Un día desperté con los gritos y llantos de mi madre y mi tía, que sostenían a mi hermana en brazos porque no respondía ni respiraba. Intentaban reanimarla con compresiones en el pecho, RCP, todo lo que podían, pero nada estaba funcionando. Yo intentaba desesperadamente llamar su atención porque, siendo tan pequeña, no entendía lo que estaba ocurriendo.

Volví a mi habitación para dormir, pero en la esquina donde estaba la cama de mi hermana, la vi acostada, respirando con normalidad. Salí de nuevo a la sala y me di cuenta de que en realidad estaba viendo a mi propio cuerpo en los brazos de mi madre, mientras intentaban revivirme. Luego, vi cómo mis ojos se abrían levemente y, de repente, todo se volvió oscuro.

Desperté unas semanas después en el hospital, junto a mi hermana y mi madre (quien también terminó contagiándose por cuidarnos). Mi madre me dijo que casi no sobrevivo y que estaban intentando despertarme, pero no reaccionaba, por lo que una ambulancia nos llevó a las tres a la unidad de cuidados intensivos. Hasta el día de hoy, sigo sin entender cómo fui testigo de mi propia muerte inminente.

---
Cuando era joven y las cámaras digitales eran algo nuevo, me obsesioné con ellas. Mi mamá me compraba una, la probábamos y, si no nos gustaba o era mala, la devolvíamos. Compramos una barata que hacía que las fotos en interiores tuvieran un tono rojo y amarillo. Además, tenía una exposición larga, lo que hacía que muchas fotos tuvieran estelas de luz y cosas raras.

Un día tomé una foto de mi habitación y la conecté a la computadora para verla. En la imagen había un hombre completamente definido, vestido con pantalones deportivos, una sudadera y un sombrero. También había estelas de luz en la foto, pero él se veía diferente de las imperfecciones causadas por la cámara, como si realmente estuviera allí, capturado en pleno movimiento mientras caminaba.

Llamé a mi mamá justo antes de escribir esto para preguntarle si lo recordaba. Dijo que no mucho (pero no le creo, porque la cámara desapareció inmediatamente después de ese evento y nunca más me compró otra).

Ahora, en mis veintitantos, todavía me dan ganas de llorar cuando lo recuerdo, porque la casa en la que crecí era aterradora y extraña. Nunca he sentido algo así en ningún otro lugar. Había algo que simplemente no estaba bien.



 """
    )
    

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
                transition_clip = VideoFileClip("video/transicion_7.mp4").resized(res).with_start(current_time)

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
        if file.endswith(".mp3"):
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