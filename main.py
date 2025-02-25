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
    os.makedirs("audio_esp", exist_ok=True)
    
    for i, sentence in enumerate(sentences):
        file_path = f"audio_esp/seg{seg_index}_sentence_{i}.mp3"
        await generate_audio_for_sentence(sentence, file_path)
        await asyncio.sleep(0.5)  # Esperar entre solicitudes
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
    text="Personas que han visto a alguien amable finalmente explotar, ¿qué pasó?",
    resolution=res
    )
    


    texto = (
       """ 

Esta mujer, "Mary", con la que trabajé, siempre era amable y alegre, saludaba en la cafetería y, en general, era querida. Trabajaba en Finanzas en proyectos especiales. Decía que quería jubilarse "en unos años" y llevaba 15 años trabajando allí.

Su jefe comenzó a presionarla para que completara el informe anual del presupuesto más rápido, pero ese informe es enorme, detallado y una verdadera pesadilla. "Mary" le dijo al jefe que estaría listo en un par de semanas, según el cronograma habitual.

El jefe dijo que debía completarse en una semana para entregarlo a los superiores. "Mary" respondió que no era posible. El jefe le envió un correo a "Mary" con copia a varios compañeros de trabajo y a los subgerentes, acusándola de tener una mala ética de trabajo y de hacer quedar mal al departamento.

"Mary" insistió en que no era posible y dijo que no le gustaba que la acosaran. Presentó su aviso de jubilación para el final de la semana, dejando a su jefe en la peor situación posible. Ella era la única que podía completar el informe del presupuesto a tiempo, así que el departamento quedó doblemente jodido.

Bien por ella.

---
En quinto grado, tuve la gran suerte de tener a la maestra favorita de la escuela primaria. Todos los estudiantes la amaban.

Mi clase siempre era muy ruidosa y molesta. Estábamos trabajando en una tarea antes de la clase de educación física, y todos la estaban sacando de quicio. Solo dejaba salir a los estudiantes si terminaban la tarea. Yo, que era súper lento, desafortunadamente fui uno de los últimos en la sala. Había un estudiante en particular, un mocoso insoportable y fastidioso, que estaba siendo exageradamente molesto.

Mi maestra se levantó, se tapó los oídos con las manos y empezó a gritar: "¡CÁLLENSE DE UNA MALDITA VEZ! ¡CÁLLENSE! ¡CÁLLENSE! ¡CÁLLENSE!". Luego salió de la sala dando pisotones, todavía gritando e insultando con las manos en los oídos. Todos nos quedamos sentados en completo horror. Algunos niños simplemente se fueron a educación física, y yo me quedé ahí tratando de terminar la tarea.

Unos minutos después, nuestra directora entró al aula y nos dijo al resto que fuéramos a educación física, pero hizo que el mocoso insoportable se quedara con ella. Después de eso, lo trasladaron al aula del otro maestro de quinto grado.

Cuando la maestra regresó, estaba completamente normal y todo siguió bien el resto del año. Trabajó muy duro y logró que todos la amáramos por su alma bondadosa y todas esas cosas lindas. Pero ese momento me dejó completamente traumatizado.

---

Hace mucho tiempo, trabajé en un centro de llamadas haciendo soporte técnico para problemas bastante complejos. Un tipo muy amable y callado pasó por la misma capacitación que yo. Hablaba si le hablaban, pero nunca se esforzaba por iniciar una conversación.

Justo después de la capacitación, el centro de llamadas cambió muchas cosas: empezaron a limitarnos el tiempo para documentar casos, el tiempo de investigación y, en general, nos apretaron con métricas absurdas. Era una completa basura, porque los favoritos podían salir a fumar tantas veces como quisieran con los gerentes, y nosotros terminábamos castigados porque teníamos que mantener nuestros números dentro de cierto rango. Él hizo todo correctamente: habló con su supervisor, luego con el gerente, después con recursos humanos. Todo siguió empeorando, además de que nos impusieron horas extras obligatorias.

Un día recibió una llamada larguísima (al menos dos horas) sobre un problema complicado. El cliente lo estaba abusando verbalmente sin piedad, pero tenía que aguantar porque los gerentes no le daban permiso para colgar. De hecho, le gritaban para que resolviera el problema rápido y pasara a la siguiente llamada, pero no podíamos colgar, el cliente tenía que hacerlo.

Un día simplemente se levantó, subió a su silla, luego a su escritorio, tiró su auricular sobre el escritorio y gruñó algo como "a la mierda", en voz baja. Miró a su alrededor, fijando la vista en la gente, especialmente en los que se tomaban esos largos descansos y en los gerentes.

Luego se fue caminando y nadie lo volvió a ver. Todos se quedaron en silencio, con miedo de moverse o decir algo.
---
Solía administrar un pub en un pequeño pueblo rural de Australia, con una población de alrededor de 300 personas. Manejar el pub consistía principalmente en mantener la paz entre los trabajadores itinerantes del petróleo y el gas y las familias locales de la industria ganadera, que resentían su presencia. El punto de conflicto más frecuente era la rocola del bar. Los tipos del petróleo y el gas solían ser citadinos que venían en rotaciones de trabajo, así que sus gustos musicales diferían bastante de los de los locales.

Había un tipo, llamémoslo Brian, que era el heredero de uno de los imperios ganaderos más grandes del distrito. Un tipo genial, querido por todos, de esos que te darían la camisa si la necesitaras. Brian tenía una hija que se había casado recientemente y estaba embarazada de su primer hijo. Durante el embarazo, notó una mancha sospechosa en su trasero, pero decidió esperar hasta después del parto para revisarla. Meses después, ya con su bebé en brazos, fue a que se la revisaran. Cáncer de piel, metastásico, sin esperanzas. Semanas de vida.

Hubo un funeral enorme. Brian quedó destrozado. Al final del servicio en la iglesia, se organizó una procesión de vehículos hasta el cementerio. Un camión de Halliburton, impaciente por estar atrapado detrás del cortejo, se salió del camino y pasó levantando una nube de polvo sobre todos.

Desde entonces, Brian comenzó a ir al pub casi todas las noches. Se emborrachaba a medias y ponía en la rocola esa maldita canción If I Die Young, que fue popular hace como quince años. El hombre estaba tocando fondo, pero nadie sabía realmente qué hacer.

Una noche, Brian estaba en la barra y la canción sonaba en la rocola. Unos tipos con chalecos de alta visibilidad de Halliburton empezaron a quejarse de la canción. Les dije que lo dejaran pasar, pero uno se levantó y desconectó la rocola. Brian la volvió a enchufar y puso la canción otra vez. Uno de los trabajadores de Halliburton lo llamó un viejo deprimente de mierda, Brian le dijo que se fuera a la mierda y… bueno, no recuerdo quién lanzó el primer golpe.

Pero entre que comenzó la pelea y los pocos segundos que tardé en intervenir, Brian ya le había dado suficiente paliza como para que el tipo terminara en una ambulancia.

Para quienes preguntan qué pasó con Brian, no hubo problemas con la policía porque en ese momento el pueblo ni siquiera tenía un oficial, y el trabajador del gas no podía dejar que su jefe supiera que se había estado peleando con los locales en el pub. 

---
Un conocido mío, "Darrel", siempre fue un chico callado que no molestaba a nadie. Como medía 1.95 metros y pesaba 113 kilogramos, jugaba fútbol americano y, en general, era respetado y querido.

Un día en la clase de español, el payaso de la clase estaba haciendo lo de siempre, fastidiando a los demás, hasta que llegó a una chica, "Nelly". Él nunca solía burlarse de personas del otro sexo, así que todos en el salón le estaban diciendo que se fuera a la mierda, pero siguió insistiendo hasta que llegó a la marca de nacimiento en su cuello, que era bastante grande y de un rojo oscuro. Le dijo que eso "le bajaba unos cuantos puntos". En ese momento, casi todo el mundo en la clase estaba a punto de abalanzarse sobre él (excepto "Darrel" y unos pocos más), hasta que Darrel se levantó, caminó tranquilamente hacia el payaso de la clase, lo levantó POR EL PELO y le dijo, y cito: "Si no te callas la maldita boca ahora mismo, te voy a atravesar esa maldita pared" señalando la pared más cercana. Luego lo soltó y se alejó.

Unos segundos después, el payaso de la clase, con su grupo de amigos detrás de él, intentó saltarle encima a Darrel en medio del aula. Darrel le metió un codazo que lo mandó al otro lado del salón, corrió hacia él, lo levantó por el hombro y metió su mano a través del yeso de la pared, justo al lado de la cabeza del payaso.

En ese momento llamaron a seguridad y tanto Darrel como el payaso fueron arrestados, aunque ambos solo terminaron con multas por los daños. Todos los días, el parche de yeso donde estaba el agujero me recuerda lo que pasó.
---
Uno de mis amigos de la secundaria, a quien llamaremos Bob, medía aproximadamente 15 centímetros menos que todos los demás. La mayoría rondaba 1.55 metros. Era un tipo interesante (en el buen sentido), le gustaba aprender, jugaba videojuegos y era genial para pasar el rato. Pero se veía escuálido, como si no pudiera lastimar a nadie, siendo honesto.

Para dar un poco de contexto, nuestro profesor de educación física era un imbécil. Le ponía apodos a todos, algunos buenos, otros malos. Siempre era sarcástico, siempre menospreciaba a los alumnos en lugar de motivarlos.

Un día, el profesor hizo un comentario sobre la mamá de Bob. Su madre tenía fibromialgia y otras condiciones que la hacían débil y enfermiza, no por elección. Algo en Bob se rompió. En cuestión de segundos, Bob derribó por completo a ese monstruo de 1.95 metros que era nuestro profesor de educación física. En ese momento, el tipo no tuvo la menor oportunidad.

Los separaron rápidamente y Bob fue expulsado y tuvo que cambiar de escuela, mientras que el profesor fue despedido por pelear con un estudiante y, en general, por ser un imbécil.
---
Cuando estaba en la secundaria, mi grupo de unos seis amigos estábamos sentados en una mesa redonda en la cafetería durante el desayuno. En la mesa de al lado, unas chicas habían estado lanzándonos pequeños trozos de su comida.

Mi amiga (M) llevaba el cabello con un estilo inusual, levantado en picos, y al parecer, las chicas de la otra mesa intentaban lanzar comida en su cabello mientras se reían entre ellas.

Entonces, mi tranquila, dulce e introvertida amiga (K) se enojó tanto que juro que parecía que le salía vapor de las orejas. Una de las chicas nos lanzó un pedazo bastante grande de su torta de huevo y cayó cerca del pie de K. K pisó la torta de huevo, la recogió del suelo, caminó hasta la mesa de las bullies y se la metió DIRECTAMENTE EN LA BOCA a la que la había lanzado.

Este fue uno de los mejores momentos que recuerdo de la secundaria. No podía creer lo que estaba viendo, porque K era la última persona que hubiera esperado que hiciera algo así. Por supuesto, se metió en problemas, pero no se arrepintió ni un poco.

---
Un tipo con el que trabajé durante unos 10 años nunca logró avanzar en el trabajo. No era "malo", pero tampoco destacaba. Siempre fue amable, siempre dispuesto a reírse y hacer una broma. Nunca lo vi ni escuché ser cruel, aunque al parecer estaba teniendo problemas con su esposa, aunque casi nunca hablaba de eso. Pero un día, mientras su hijo menor estaba en la iglesia con un familiar, perdió la cabeza y le disparó a su esposa antes de quitarse la vida.

Otra mujer con la que trabajé incluso antes que él, en el mismo lugar, era súper dulce y siempre estaba sonriendo. Estaba en medio de un divorcio y ahogó a su hija de 3 años en la bañera de la casa de su padre (el abuelo de la niña) porque no quería "compartirla" con su ex después del divorcio. Hasta donde sé, todavía está en prisión.

Ambos casos son bastante jodidos.

---
Un tipo que conocí en primer año era súper relajado, lo llamaremos James. Era el tipo de persona que, si no te caía bien o lo molestabas, automáticamente todos te odiaban.

Un día, un imbécil de tercer año, que se creía muy rudo solo por ser mayor, estaba molestando a un grupo de estudiantes de primer año sin ninguna razón. James hizo lo correcto y se metió para decirle que dejara de joder. Ahora, James no era muy grande, tal vez medía 1.67 metros y pesaba unos 54 kilogramos, más o menos. Mientras que el junior era de unos 1.80 metros y 86 kilogramos. Una diferencia bastante grande.

El tipo mayor, como de costumbre, siguió actuando como un imbécil, haciéndose el duro, hasta que James le metió un puñetazo directo al estómago y procedió a darle una paliza brutal. El junior terminó en el hospital con un brazo roto y la cara bastante destrozada.

Nadie se preocupó demasiado por preguntar cómo demonios James fue capaz de hacerle tanto daño, pero lo que sí quedó claro es que, desde ese día, todos le tuvimos mucho miedo.
---
Un amigo mío tenía el apodo de "Rat" porque era delgado y tenía una nariz grande. Un tipo súper amable, con muchos amigos, pero nunca una novia. En el último año de secundaria, consiguió una novia que también iba en el mismo autobús que nosotros.

Un tipo que se creía muy cool empezó a preguntarle a la chica cómo podía salir con Rat, diciendo que era feo. Había estado molestándolo durante años, pero Rat siempre parecía ignorarlo. Luego, el imbécil le preguntó a la novia si se sentía gorda estando al lado de Rat. Podría haber dicho cualquier cosa sobre él y no habría pasado nada, pero cuando empezó a burlarse de su novia, cruzó la línea.

Rat y el otro empezaron a empujarse en el autobús hasta que el tipo lo desafió a una pelea. En la siguiente parada, ambos bajaron. Todos los demás nos pegamos contra las ventanas traseras del autobús para ver qué pasaba.

El matón levantó los puños y empezó a moverse como si fuera boxeador. Rat lanzó un solo golpe y el imbécil cayó al suelo. Le rompió la nariz y el pómulo. Necesitó cirugía y cuando regresó a la escuela tuvo que usar una especie de jaula alrededor de su cara.

Durante todo ese tiempo, el tipo siguió insultando a la novia de Rat, sabiendo que mientras tuviera la jaula puesta, nadie le haría nada. Después de meses de recuperación y entrenamiento, decidió desafiar a Rat a otra pelea. Bajaron juntos del autobús de nuevo, el tipo levantó los puños y se puso a moverse otra vez. Rat le dio otro golpe directo a la nariz y el tipo cayó al suelo otra vez.

Todos en el autobús gritaron y el conductor tuvo que detenerse para pedir ayuda por radio. Pensamos que lo había matado, pero solo le rompió la nariz otra vez. Seguro que el tipo creyó que la primera vez fue un golpe de suerte y que no había forma de que un flacucho lo golpeara dos veces. Ahora tiene la nariz aplastada como un boxeador.

Perdí el rastro de Rat unos años después de la universidad. Seguía siendo delgado, seguía usando su apodo y seguía siendo un buen tipo. Parecía que la vida le iba bien.

Esto fue en los años 70. Hoy en día, habrían llamado a la policía y habrían presentado demandas.

---
Llevo a mi gato a una veterinaria que también tiene 100 gatos viviendo en la clínica. Algunos simplemente no son sociables, otros son ciegos o tienen discapacidades graves, y la clínica básicamente funciona como un hospicio para otros que están en sus últimos días. En resumen, la doctora, su equipo y los voluntarios son unos santos.

Desafortunadamente, la gente se ha enterado y ahora algunos creen que la clínica es "el lugar donde puedes abandonar gatos no deseados". Pero no lo es. Ya están al límite de su capacidad.

Un día estaba esperando para un chequeo de rutina cuando entra una mujer que parece una Kardashian, cubierta de joyas y ropa cara, con un gato perfectamente sano en sus brazos. Le dice a la recepcionista: "Me voy de la ciudad, no puedo llevarme al gato, así que lo estoy donando a ustedes". La empleada le explica que no, que no es un suéter lo que tiene en las manos y que esto no es caridad. No funciona así.

Sin darse cuenta de su entorno—había al menos una docena de personas entre clientes y personal—la mujer ni siquiera intenta hablar en voz baja.

Después de que le dicen que no, responde: "Está bien, si no lo toman, lo voy a abandonar en la calle". Se queda mirando fijamente a la recepcionista, probablemente esperando que la clínica se sienta culpable y acepte al gato, pero luego se da la vuelta y se dispone a irse.

Antes de que llegue a la puerta, otro cliente—un tipo grande y corpulento—se interpone en su camino. Y procede a soltarle algo tan brutal que desearía poder repetirlo palabra por palabra, pero lo resumiré con lo más destacado:

"Señora, ¿quiere abandonar al gato? Bien. Le voy a dar lo que quiere. Yo me llevaré a su gato."

"Pero el precio es que voy a humillarla delante de todos aquí, inútil pedazo de mierda. ¿Tan jodidamente egoísta que no puedes gastar 69 centavos al día en una lata de comida para gatos? Que te jodan. No mereces la generosidad de la gente que trabaja aquí. ¿Quieres chantajearlos emocionalmente para evitar el asesinato de un gato? Me das asco."

Esto fue digno de un discurso de Lee Ermey.

Para ese momento, la doctora había salido de su oficina. No sabía exactamente lo que estaba pasando, pero la cosa se había puesto bastante ruidosa. Obviamente, no le gusta que la gente grite palabrotas en su sala de espera, porque no es bueno para el negocio.

El tipo se gira hacia ella y dice: "Mire, probablemente ya esté acostumbrada a esto, pero yo me enojo cuando veo a gente que maltrata animales."

---
Durante los años de primer y segundo curso, el mismo tipo me jodió en la parada del autobús y durante todo el camino a casa. Todos los días, sin parar, siempre fastidiándome, metiéndose conmigo constantemente. Mucha gente me preguntaba por qué lo aguantaba, pero en ese momento era muy tímido y pasivo, simplemente me quedaba callado y no reaccionaba.

Un día, el tipo intentó empujarme a unos arbustos, pensando que sería gracioso. Nunca antes había sido físico. Agarré su muñeca y lo puse de culo en el suelo. Cayó de espaldas y, cuando intentó levantarse, metí en un solo golpe los dos años de mierda que me había hecho pasar. Cayó otra vez.

Al día siguiente en la escuela, tenía el ojo morado más oscuro que había visto en mi vida. No apareció en la parada del autobús durante unos días y, cuando volvió a tomarlo, nunca volvió a decir una sola palabra.

Sorprendí a mucha gente, pero resultó que muchos otros también odiaban a ese tipo y estaban celosos de que yo le hubiera dado su merecido. Me hizo mucho bien, y la reacción positiva de los demás me ayudó a salir de mi caparazón.

10 de 10, lo volvería a golpear.

---
Había un chico en mi escuela cuando estaba en séptimo grado. Se llamaba Fredrick. Todo el mundo lo quería, era amable, donaba regularmente a la caridad, todos lo conocían y lo respetaban.

Un día llegó un chico nuevo a la escuela, lo llamaremos Josh.

Josh era un idiota. Golpeaba a la gente, los empujaba, les tiraba comida en el almuerzo, en general, un grandísimo tonto. Un día decidió meterse con Fred, haciéndole lo mismo de siempre, pero Fredrick explotó. Se volvió loco, golpeando, gritando y pateando. Ambos fueron suspendidos por 2 o 3 días.

Cuando volvieron, Josh tenía un ojo morado, moretones en los brazos y la pierna izquierda, y se veía terrible. Pensó que después de lo que le hizo Fred, todos lo empezarían a odiar. Pero no. Todos estaban hartos de él y comenzaron a burlarse de lo mal que se veía.

Fred solo se ganó aún más cariño después de lo ocurrido. Aunque me contó que lo castigaron una semana en casa.

---
Me considero una persona amable y tranquila. Estaba saliendo con una chica y resultó que el novio de mi amiga, a quien considero aún más amigable que yo, también había salido con ella antes. Mi amiga me advirtió que era una persona realmente tóxica. No le di mucha importancia, ya que no me gusta juzgar a la gente por lo que otros dicen.

Pero después de un mes o dos en la relación, empecé a notar lo que mi amiga me había dicho. Unos días después, terminé con ella. En los días siguientes, empezó a hablar mal de mí y a difundir rumores sobre mí y sobre mi amiga. El novio de mi amiga escuchó esos rumores y también rompió con ella. Ambos estábamos bastante molestos con la situación.

Tres días después, mi amiga encontró a su ex besándose con mi ex y los confrontó. Estaba bastante tranquila al respecto, no es como si él le hubiera sido infiel, pero igual le dolió. Estaba a punto de irse cuando mi ex le soltó: "Seguro te duele más saber que estaba conmigo mientras tú andabas con él."

Mi amiga se giró lentamente y le pidió que repitiera lo que había dicho. Mi ex, con una sonrisa, lo repitió.

El peor error de su vida.

Mi amiga se le lanzó encima y le dio una paliza monumental, incluso arrancándole mechones de cabello. Cuando terminó con ella, se giró hacia su ex y le dijo: "¿Quieres engañarme? Está bien. Pero puedes llevarte una tunda con ella también."

Le dio una bofetada y lo remató con una patada.

Todavía hablamos de esto hasta el día de hoy.

---
Solía ser muy tímida y callada. Como hija única de una madre soltera que trabajaba todo el tiempo, me costaba socializar con personas de mi edad, ya que la mayoría de las personas a mi alrededor eran entre 6 y 10 años mayores que yo. (Esto pasó entre 1997 y 1998.)

Mi mamá decidió meterme a una escuela privada, y fue el cambio más grande de mi vida. Esos niños sabían de computadoras, música e inglés (soy de México), y yo apenas conocía lo esencial de todo, ya que venía de escuelas públicas. Las primeras semanas fueron una pesadilla, porque una niña decidió burlarse de mí por mi piel (yo era más morena, y ella era blanca) y por mi acento (estos niños no tenían el acento de la región... por alguna razón).

Las cosas siguieron así, y cada día me sentía más triste y sola, hasta que un día simplemente exploté.

Empecé a hacerme amiga de una niña a la que le gustaban las mismas caricaturas que a mí (Dragon Ball, Pokémon, etc.), y a mi bully no le gustó que ya no me dejara molestar. Un día, mientras estábamos en clase, decidió empezar a picarme con su lápiz. Yo era demasiado tímida para decir algo delante del maestro. Siguió picándome hasta que el maestro salió un momento, así que simplemente agarré su lápiz y lo lancé lejos.

Ahí empezó la pelea en medio del salón. Algunos niños estaban animando, otros intentaban separarnos y otros salieron corriendo a buscar al maestro. Me pellizcó, me arañó y me golpeó, pero jamás pensó que yo le iba a responder... y de manera sucia. Le jalé el cabello, le di un puñetazo en el estómago y la mordí.

No recuerdo bien qué pasó después ni cómo evité que me expulsaran, pero dos semanas después, estaba en el recreo, comiendo mi almuerzo y platicando feliz con mi mejor amiga, cuando de repente ella se acercó, me dio una bolsa de Cheetos (sabor pizza) y nunca volvimos a hablar del tema.
---
Mi hermano era un niño muy dulce (énfasis en dulce) en la primaria. Esto fue a principios de los 2000, probablemente tenía unos 8 años en ese entonces. Hacía lucha y jugaba béisbol para pasar el tiempo, pero en general era un niño bastante normal. Era inteligente y tenía una buena cantidad de amigos gracias a los deportes que practicaba. Nada fuera de lo común.

Sin embargo, había un niño que lo molestaba mucho sin razón alguna. Se llamaba Garrett. Le ponía apodos, le escondía lápices y plumas para que lo regañaran en clase.

Un día, por alguna razón estúpida, Garrett decidió abofetear a mi hermano con el almuerzo escolar. Tal vez fue un pedazo de pizza, quizás un bistec empanizado.

Mi hermano se levantó, lo agarró por la camisa y lo estampó contra el suelo. Le rompió la nariz y la maxila (la parte superior de la mandíbula, debajo de la nariz).

Después de eso, todos empezaron a llamarlo Garrett el Hurón porque tuvo que andar con la boca cerrada con alambres.

Unos años después, yo estaba siendo acosado y, curiosamente, Garrett se puso de mi lado y me defendió. No sé si realmente maduró o si simplemente tenía miedo de que alguien me molestara sabiendo cómo mi hermano resolvía las cosas.
---
Esta es mi historia, que ya he contado en partes antes.

En la secundaria, este tipo y yo éramos amigos, pero nos volvimos prácticamente inseparables desde el final del penúltimo año hasta la graduación. Pasábamos mucho tiempo juntos hasta que me mudé a cuatro horas de distancia para la universidad. Él empezó a fumar marihuana en la secundaria, yo la probé pero no le vi el atractivo.

Poco a poco, comenzó a hacer cosas cada vez más turbias. Teníamos un código entre amigos bien establecido y todos acordamos las reglas al crearlo. Una de esas reglas era: "No salgas con la ex de un amigo sin su permiso."

Tuve una ex bastante problemática con la que él quería salir. Le advertí sobre ella, pero al final, su vida era su decisión. Como era de esperarse, terminaron rompiendo.

Con el tiempo, se volvió increíblemente egocéntrico porque consiguió una beca universitaria y no dejaba de restregárnoslo en la cara. Básicamente, le pagaban la universidad y, además, le daban 1500 dólares al mes mientras estuviera en clases para gastar en lo que quisiera.

Mientras todo esto pasaba, yo estaba lidiando con mis propios problemas, pero prefería guardármelos. Hasta que todo empezó a desbordarse y decidí hablar con él.

Odiaba mi trabajo y estaba preocupado porque pensaba que había embarazado a mi novia de ese entonces (afortunadamente, no fue así). En medio de un ataque de ansiedad, su respuesta fue llamarme "perra histérica". Definitivamente, no estaba en la lista de cosas reconfortantes que esperaba escuchar.

Un par de meses después, mi ex, la que me destrozó cuando tuve que mudarme, publicó en su historia: "Hackeado, te amo, bebé lol."

Yo estaba furioso.

Le reclamé y él simplemente se encogió de hombros y dijo: "Tú no la querías, ¿por qué te molesta?"

Pues porque TODOS prometimos que no haríamos eso. Era una cuestión de principios.

Pasaron un par de meses y me hundí aún más en la depresión. Mi novia me dejó, seguía atrapado en el mismo trabajo, estaba en los antidepresivos equivocados y no tenía amigos en mi nueva ciudad.

Un día, a las 11 PM, me llama y dice: "Oye, (otro amigo) y yo estamos en línea, entra."

Le respondí con calma: "Nah, estoy cansado. Me voy a dormir."

Su respuesta: "Ugh. Siempre haces esto. Siempre te pones a ti mismo antes que a tus amigos."

Me detuve un momento. Y le solté: "Eso es mucho decir para alguien que ha venido a visitarme UNA vez en tres años."

Yo había manejado cuatro horas solo para verlos CUATRO veces en ese tiempo, y estaba completamente jodido de dinero. Él, en cambio, no tenía problemas económicos ni trabajo.

Por supuesto, la conversación se convirtió en una pelea que fue escalando. Eran párrafos enteros de él diciéndome que era un mal amigo por no ponerlo en primer lugar y yo dándole pruebas legítimas de por qué estaba harto de su mierda.

Finalmente, volvió a llamarme "perra histérica" y ahí dije: "A la mierda, si quieres pelea, va en serio. Aquí tienes todo lo que me has hecho y nunca has pedido disculpas, y todo lo que he hecho por ti sin que me hayas dado ni un gracias."

La lista era larga.

Su respuesta: "No vas a conservar amigos si los tratas así."

Mi respuesta fue simple: "Bien. Ese es el punto."

No he hablado con él en dos años y no tengo intenciones de hacerlo. No pienso disculparme porque no tengo nada de qué disculparme.
---
Para resumir la historia, fui a una secundaria que estaba muy evidentemente dividida en distritos de manera cuestionable: alrededor del 60% de los estudiantes venían de vecindarios de clase media-alta, mientras que el otro 40% vivía en un entorno sacado de una película de John Singleton de los 90. Eso hacía que hubiera una mezcla de estudiantes bastante interesante y muchas situaciones graciosas.

En octavo grado decidí tomar español como lengua extranjera. Aunque yo me lo tomaba en serio y quería aprender lo más posible, la otra mitad de la clase se la pasaba intercambiando insultos, haciendo beatboxing y, en general, convirtiendo el aula en un caos con buen humor.

Aquí entra nuestra profesora de español. Tendría, como mucho, unos 23 años. Era hermosa, dulce y muy ingenua. Desde el momento en que entró al salón, parecía convencida de que estaba allí para cambiar vidas, una tarea cuya imposibilidad se hizo evidente bastante rápido.

Con el tiempo, el desorden en la clase se fue haciendo cada vez más grande. Hasta que un día explotó.

Caminó hasta la esquina del salón donde unos compañeros literalmente estaban jugando a los dados (apostando en medio de la clase), agarró el cartón y los dados y los lanzó al otro lado del aula antes de perder por completo el control. Nunca había visto algo así. Pasó de ser dulce y de voz suave a gritar a todo pulmón y perder completamente los estribos.

En una sola clase suspendió a 9 estudiantes, amenazó con suspender a cualquiera que dijera una sola palabra por el resto del año y hasta llamó a los guardias de seguridad para sacar a la fuerza a algunos de los más problemáticos.

Una semana después, desapareció y nunca más la volvimos a ver en la escuela.
---
No era un amigo, pero fui yo.

En la secundaria, había un programa para estudiantes con discapacidades mentales que abarcaba distintos tipos de condiciones.

Un día, estaba con mis amigos en la hora del almuerzo y vimos un gran círculo de estudiantes. Nos dio curiosidad y nos acercamos para ver qué estaba pasando.

Solo para encontrarnos con un bully empujando y burlándose de un chico con discapacidad.

Se notaba que el chico estaba asustado y confundido por lo que estaba pasando. Nadie hizo nada. Todos solo miraban.

Antes de que pudiera intervenir, los supervisores llegaron y separaron todo, pero yo seguía furioso.

Después de la escuela, busqué al tipo y le pregunté por qué carajo le pareció gracioso lo que hizo.

Estaba con sus amigos y trató de hacerse el duro diciendo: "Solo era una broma, estaba jugando."

Ahí fue cuando exploté y le di la paliza de su vida frente a sus amigos.

Intentaron detenerme, pero yo ya estaba demasiado encabronado.

Cuando terminé, miré a sus amigos y pregunté: "¿Alguien más quiere una ronda conmigo?"

No dijeron ni una palabra. Solo se llevaron a su amigo y se largaron.

¿Quién en su sano juicio cree que está bien burlarse de un chico con discapacidad? En serio. Que se vayan al carajo.
---
Un amigo mío, que era increíblemente tranquilo, era molestado todos los días por un tipo de nuestra clase.

No sé si llamarlo acoso, pero era una joda constante, todos los días, con pequeñas cosas molestas, y el imbécil no lo dejaba en paz durante meses.

Con el tiempo, el tipo empezó a subir de nivel. Primero, le lanzaba bolitas de papel durante horas en clase. Página tras página. Luego pasó a las bolitas de papel con saliva, disparadas con un tubo improvisado hecho con un bolígrafo.

Un día, como siempre, seguía con lo mismo. Hacía calor, no teníamos ventilación, todos sudaban y estaban incómodos. Además, era un día escolar largo y agotador.

El bully empezó a hacer bolas de papel del tamaño de la palma de su mano y a lanzárselas a la cabeza cada vez que el maestro no estaba mirando.

Después de varias de esas, mi amigo, sin siquiera mirarlo, le dijo en tono frío:

"Te reto a que tires otra."

Eso nos pareció raro a todos. No era común escucharlo hablar así.

El tipo esperó unos cinco segundos, arrancó otra hoja, la hizo bola y, justo en el momento en que estaba en posición de lanzamiento...

Mi amigo se levantó, agarró su silla y la levantó por encima de su cabeza.

Y le reventó la maldita silla encima.

El bully ni siquiera tuvo tiempo de reaccionar. Instintivamente levantó el brazo para protegerse y la silla cayó con toda la fuerza sobre él.

Nunca había escuchado un hueso romperse, pero la mano del bully literalmente se hizo trizas y produjo el sonido corporal más raro que he escuchado en mi vida.

El imbécil cayó de espaldas, con su ahora deformada mano protegiéndolo, mirándolo en completo shock.

Mi amigo, con toda calma, se levantó y salió del aula, porque sabía perfectamente que lo iban a mandar con el director en cuanto apareciera un adulto.

Lo suspendieron por una semana, creo.

Lo único que puedo decir después de eso es que el bully jamás volvió a meterse con él. Ni con nadie más.

Fue una de las cosas más badass que he visto en mi vida. Y honestamente, me sorprende que solo le haya dado un golpe. Ese imbécil se lo tenía más que merecido.

---
Un poco diferente, pero me recordó a esto:

Este era un tipo con el que era amiga/tal vez estaba saliendo. Era extrañamente desapegado, pero extremadamente, extremadamente amable conmigo. Parecía que yo era la única persona que le gustaba, aparte de su mamá.

Nunca hizo otra cosa más que ser dulce y hacer cosas increíblemente lindas por mí. Encontró mi álbum favorito en vinilo y lo tenía listo para reproducirlo cada vez que iba a su casa. Cuando llegué agotada del trabajo, me dejó tomar una siesta en su cama y me arropó. Aprendió a hacer chocolate caliente desde cero solo para tomarlo conmigo y fingía que le gustaba el café porque yo lo amaba.

Una vez, estábamos sentados en su sala, en el banco de su piano horizontal que tenía. Soy cantante, y siempre me pedía que cantara para él. No importaba dónde estuviéramos: mientras escuchábamos vinilos en su cuarto, almorzábamos o ponía pistas de karaoke en YouTube solo para escucharme cantar. Decía que mi voz le traía paz.

Sabía un poco de piano, lo suficiente de sus clases de infancia como para arreglárselas, así que los dos compartíamos el banco mientras él improvisaba en las teclas y yo intentaba hacer una melodía sobre eso.

De repente, su hermano menor subió las escaleras, completamente de manera inofensiva, y entró en la cocina abierta mientras hablaba con su mamá.

El chico con el que estaba se giró inmediatamente y le gritó, como hacen los hermanos:

"¿Puedes callarte? No la puedo escuchar."

Su hermano le respondió sin pensarlo:

"Cállate, solo estoy hablando con mamá."

Claramente, lo estaba provocando.

Y entonces pasó.

El chico se levantó del banco, saltó limpiamente por encima de la mesa de centro y le metió un derechazo con toda su fuerza en la mandíbula.

Solo porque estaba hablando mientras yo cantaba.

Hubo un poco de sangre.

Me quedé horrorizada... pero sobre todo impactada.

Pasó tan rápido que ni siquiera tuve tiempo de parpadear.

Con el tiempo, me di cuenta de que tenía un temperamento extremadamente violento y que probablemente, de verdad, era un sociópata. No parecía sentir empatía por nada.

Así que simplemente me hice desaparecer y nunca lo volví a ver.

Pero lo más extraño de todo es que conmigo solo fue amable. Siempre.

Fue raro.

En fin, esa es la historia.
---
Alguien se metió con mi hermano. 

Pasó en la escuela secundaria. Yo estaba en octavo grado, mi hermano en séptimo. Nunca había peleado con nadie en mi vida, nunca fui de ser cruel y odiaba la confrontación... hasta ese día.

Salí de la escuela hacia el área donde nos recogían y vi a unos chicos empujando a mi hermano, tirándole nieve y golpeándolo con sus carpetas. Le estaban diciendo un montón de cosas horribles que ni quiero recordar.

Perdí la cabeza. Absolutamente.

Lo saqué de ahí y empecé a gritar y a repartir golpes.

Él estaba llorando, yo estaba gritando tan fuerte que me dolió la voz durante una semana. Les dije que se largaran, que se fueran a la mierda, mientras todos nos rodeaban, sorprendidos porque nadie jamás me había escuchado maldecir o alzar la voz contra alguien.

No recuerdo mucho de lo que pasó después, pero sé que los tontos esos fueron suspendidos por una semana y los castigaron con tareas en la escuela.

Nunca volvieron a meterse con él.

Puedes meterte conmigo o intentar molestarme todo lo que quieras, pero no toques a mi familia.

Desde entonces, no he peleado ni he explotado contra nadie. Mi hermano y yo seguimos peleándonos entre nosotros, porque somos hermanos y así es la vida, pero él sabe que siempre voy a estar ahí para él.


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
                transition_clip = VideoFileClip("video/transicion_3.mp4").resized(res).with_start(current_time)

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