import asyncio
import re
import os
import numpy as np
import textwrap
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy import concatenate_audioclips
import edge_tts
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


async def generate_audio_for_sentence(sentence, output_file, voz="en-US-ChristopherNeural"):
    """
    Genera el audio TTS para una oración y lo guarda en output_file.
    Opciones de voz: es-US-AlonsoNeural, en-US-ChristopherNeural, etc.
    También se añade un ajuste de velocidad (rate).
    """
    # En este ejemplo se añade rate="+7%" para aumentar la velocidad
    comunicador = edge_tts.Communicate(text=sentence, voice=voz)
    await comunicador.save(output_file)
    print(f"Audio guardado: {output_file}")

async def generate_all_audios(sentences, seg_index):
    """
    Genera un audio para cada oración y devuelve una lista de rutas a los archivos generados.
    Se nombran de forma que se distingan por segmento.
    """
    audio_files = []
    os.makedirs("audio_eng", exist_ok=True)
    
    for i, sentence in enumerate(sentences):
        file_path = f"audio_eng/seg{seg_index}_sentence_{i}.mp3"
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
        new_duration = clip.duration - 0.8 if clip.duration > 0.8 else clip.duration
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
    #AQUI VA EL TÍTULO. PUEDES CAMBIARLO A TU GUSTO
    await generate_title_video(
    text="People who have seen nice people finally snap, what happened?",
    resolution=res
    )
    
    # Abrir el video de fondo de forma continua (gameplay1.mp4)
    #main_bg = VideoFileClip("video/gameplay1.mp4")
    #res = (main_bg.w, main_bg.h)
    
    # Texto completo con separadores de segmento (líneas con '---')
    texto = (
       """ 


This woman, "Mary," I worked with was always pleasant and cheerful, said hello in the lunchroom, and was generally liked. She worked in Finance on special projects. She said she wanted to retire "in a few years," and she had been working there for 15 years.

Her boss started pressuring her to complete our annual budget report faster, but this thing was huge, comprehensive, and a figurative beast. "Mary" told the boss it would be ready in a couple of weeks, per the usual schedule.

The boss said it needed to be completed within one week to give to the higher-ups. "Mary" said it was not possible. The boss emailed "Mary," cc'ing a bunch of coworkers and the Assistant Managers, calling her out for a poor work ethic and for making the department look bad.

"Mary" said it was not possible and that she did not appreciate being bullied. She put in her notice to retire by the end of the week, leaving her boss high and dry. She was the only one who could do the budget report in a timely manner, so the department was double screwed.

Good for her.
---
Back in 5th grade, I was super lucky to have the elementary school’s favorite teacher. Every single student loved her.

My class was always super loud and annoying. We were working on some assignment before PE, and everyone was pissing her off. She was only allowing students to go out if they finished the assignment. My slow ass was unfortunately one of the last kids in the room. This one student, who was a godawful and annoying little shit, was being way over the top.

My teacher got up, put her hands over her ears, and just started screaming, "Shut the fuck up! Just shut up. Shut up. Shut up." She stomped out of the room, still screaming with her hands covering her ears. All of us just sat there in horror. A couple of kids just left to go to PE, and I sat there just trying to finish the assignment.

Our principal came into the room a few minutes later, just telling the rest of us to go out to PE, but she made the little shit stay in the room with her. He was moved into the other 5th grade teacher's room after that.

She was completely normal and fine after coming back, and nothing else went wrong for the rest of the year. She just worked her ass off and made all of us love her with her caring soul and all that fun stuff. But that moment completely traumatized me.
---
A long time ago, I used to do call center tech support for fairly complex issues. A really nice, quiet guy went through the same training class. He talked if you talked to him but never went out of his way to chat.

Right after training, the call center changed a ton of stuff—we started getting squeezed on the amount of time we could do documentation, how much research time we had, just metrics in general. It was utter bullshit because the favorites got to go on smoke breaks as often as they wanted with the managers. We would essentially be punished for that because we had to keep the average numbers in a certain area. He did all the right things—talked to his manager, talked to their manager, then to HR. It kept getting worse, plus enforced overtime.

Then he got a super long call (he was on it for at least two hours) about a complex issue, and the customer was just straight-up abusing him, but he had to take it because the managers would not give permission for him to hang up. And they were basically screaming at him to resolve the issue and get to his next call, but we could not end calls—the customer had to.

One day, he just stood up, stepped onto his chair, then onto his desk, threw his headset on the desk, and sort of growled something like, "Fuck this," quietly. He looked around, staring people in the face, especially the ones who took those long breaks and the managers.

Then he walked out, and no one ever saw him again. Everyone was super quiet and afraid to move or say much of anything.
---
I used to manage a pub in a small rural town (population around 300) in Australia. Running the pub was mostly about maintaining the peace between the itinerant oil and gas workers and the local cattle industry families who resented their presence. The flashpoint for this conflict was frequently the jukebox in the bar. The oil and gas guys were usually city folks on fly-in, fly-out rotations, so their musical tastes somewhat differed from the locals'.

Anyway, there was a guy we will call Brian, who was the heir apparent to one of the larger cattle empires in the district. Super cool guy, everyone liked him, would give you the shirt off his back type. Brian had a daughter who had just married and was pregnant with her first kid. Sometime during the pregnancy, she noticed a dodgy-looking blemish on her butt, though she figured she would wait until she had the kid to get it looked at. Months later, she had the kid, went to get it checked—skin cancer, metastasized everywhere. Weeks to live.

There was a huge funeral. Brian was destroyed. At the end of the church service, there was a procession of vehicles out to the cemetery. Some Halliburton truck, impatient to be caught behind it, plowed down the side of the road and spewed dust over the whole thing.

From then on, Brian would be down at the pub every other night. He would get half-smashed and then put that fucking If I Die Young song on the jukebox—the one that was popular like ten years back. The man was circling the drain, but nobody really knew what to do about it.

Anyway, one night, Brian was at the bar, and the song was on the jukebox. Some guys in Halliburton-patched Hi-Vis started bitching about the song choice. I told them to just leave it be, but one of them got up and unplugged the jukebox. Brian plugged it back in and put the song on again. One of the Halliburton guys called Brian a depressing old cunt. Brian told him to get fucked and... well, I do not remember who threw the first punch.

But between the fight starting and the couple of seconds it took me to break it up, Brian did enough damage to put the guy in an ambulance.

---
An acquaintance of mine, “Darrel,” was always a quiet kid who bothered nobody. Given that he was 6’5” and 250 lb, he played football and was generally respected and liked.

One day in Spanish class, the class clown was making his usual rounds talking shit until he got to this one girl, “Nelly.” He never really made fun of people of the other sex, so everyone around him was telling him to fuck off, but he kept going and finally got to the birthmark on her neck, which was very large and dark red. He told her that it “dropped her a few numbers down.”

At this point, just about everyone and their grandma in the class was standing up, about to rush him (except for Darrel and a few others), until Darrel got up, waltzed over to the class clown, picked him up by his hair, and said, and I quote, “If you don’t shut the fuck up right now, I am going to put you through that fucking wall.” Points to the nearest wall.

He dropped the clown and walked away. A few seconds later, with his band of merry men behind him, the clown tried to jump Darrel in the middle of the class. Darrel then proceeded to elbow him across the room, run over, pick him up by the shoulder, and put his hand through the drywall right next to the clown’s head.

By this point, security had been called, and both Darrel and the clown were arrested, with both only getting off with fines for damages. Every day, the spackle patch where the hole used to be humbles me.

---
One of my middle school friends, whom we will call Bob, was about half a foot shorter than everyone else. Everyone was around 5 ft. He was an interesting (in a good way) dude—interested in learning, played video games, great to hang out with. But he looked scrawny. Honestly, he did not look like he could hurt anything.

For some context, our gym teacher was an asshole. He gave everyone nicknames—some good, some bad. He was always sarcastic, always berating everyone, speaking down to us instead of encouraging us.

One day, the gym teacher said something about Bob’s mom. Bob’s mom had fibromyalgia and some other conditions that made her weak and unhealthy not by choice. And something in Bob snapped.

Bob completely took down this 6'5" monster of a gym teacher. The gym teacher looked like he stood no chance at that moment. They were quickly pulled apart, and Bob got expelled and had to move schools, while the gym teacher was fired for fighting a student and being an overall asshole.

---
When I was in high school, my group of about six friends was sitting at a round table in the cafeteria for breakfast. A table over, some girls had been tossing small chunks of their food in our direction. My one friend (M) wore her hair in an unusual, spiked-up style, and I guess the girls at the table were trying to land food in her hair while cackling to themselves.

Cue my quiet, sweet, introverted friend (K) getting so angry I swear steam was coming out of her ears. One of the girls had thrown a decent-sized piece of her egg patty at us, and it landed on the floor near K’s foot. K proceeded to step on the egg patty, pick it up off the ground, walk over to the table of bullies, and shove the egg directly into the mouth of the one who had thrown it!

This was such an amazing moment in my high school memory. I could not believe what I was seeing, as K was the last person I would have expected to do that. Of course, she did get in trouble, but she did not regret it one bit.

---
A guy I had worked with for about 10 years never could get ahead at work. He was not "bad," but he just did not really excel. He was always kind, always ready to laugh and crack a joke. Never saw or heard him be mean, but apparently, he and his wife were having some trouble, though I had not heard him talk about it much. One day, while his youngest was out at church with a family member, he flipped out and shot his wife, then himself.

Another woman I had worked with even before that, but at the same place, was super sweet and always smiling. She was in the middle of a divorce and drowned her 3-year-old daughter in a bathtub at her dad's (the kid's grandpa’s) house because she did not want to "share" her with her ex after the divorce. She is still in prison as far as I know.

Both are kinda fucked up.

---
A guy I knew freshman year was super chill—we will call him James. He was the kind of guy that if you did not like him or picked on him, everyone just hated you.

One day, this absolute douche of a junior, who thought he was so tough just because he was older, was picking on a group of freshmen for literally nothing. So James did the appropriate thing—stepped in and told the junior to knock it off.

Now, James was not a very big dude. Maybe 5'6" and 120 lb, give or take. The junior, on the other hand, was about 5'11" and 190 lb—a fairly large difference. So this junior dude starts acting all tough and being a douche like usual, and James just sucker punches this dude in the stomach and proceeds to rock his shit.

The junior ended up in the hospital with a broken arm and a pretty messed-up face. Nobody really bothered to ask James how he was able to beat this dude up so badly, but bottom line is—we all became very scared of James.

---
A friend of mine was nicknamed Rat because he was skinny with a big nose. Super nice guy who had a lot of friends but never a girlfriend. Senior year of high school, he finally had one, and she also rode the same bus as us.

There was this guy who thought he was so cool, and he started asking her how she could date Rat because he was so ugly. He had bullied Rat for years, and Rat always seemed to ignore it. But then the guy asked the girlfriend if she felt fat standing next to Rat. He could have said anything about Rat and probably gotten away with it, but once he started making fun of his girlfriend, that was the last straw.

They started pushing and shoving on the bus, and the guy challenged Rat to a fight. They all got off at the next stop. I still remember everyone plastered against the back windows of the bus, watching. The bully had his fists up, dancing around like he was a boxer. Rat threw one punch, and down he went. Broke his nose and cheekbone—pushed part of his nose into his brain. He needed surgery and had to wear a cage around his face when he returned to school.

The whole time he was recovering, he kept calling Rat’s girlfriend names, knowing that as long as he had the cage on, nothing would be done to him. After months of rehab and training, he decided to challenge Rat to another fight. They got off the bus together again, and once more, he put up his fists and started dancing around. And again, Rat hit him right in the nose—down goes Frasier.

Everyone yelled, and the bus driver pulled over to radio for help. We honestly thought he killed him. Just broke his nose again. I am sure he thought the first time was a lucky punch and that there was no way a skinny kid would get him twice. Now, thanks to Rat, he had a permanently flattened boxer’s nose.

I lost track of Rat a few years after college. He was still skinny, still going by Rat, and still a nice guy. Life seemed good for him.

This was in the '70s. Today, the police would have been called, and lawsuits would have been filed.

---
I take my cat to a vet who also has 100 cats living at the clinic. Some of them are just unsociable, some are blind or have other horrible handicaps, and the clinic is basically hospice care for still others. Long story short, the doctor, her staff, and the volunteers are all saints.

Unfortunately, word has gotten out, and some people now think of the clinic as the place where you can dump unwanted cats. Which they really cannot. It is already at capacity.

Anyhow, I am waiting there one day for a routine checkup, and this Kardashian-looking woman, covered in jewelry and expensive clothes, walks in with a perfectly healthy-looking cat. She tells the woman behind the counter, "I'm leaving town, I can't take the cat, so I'm donating it to you guys."

The employee explains that no, that is not a sweater in her hands, and this is not Goodwill—it does not work that way. Oblivious to her surroundings—there are maybe a dozen people there, between patient parents and staff—she is not even making an effort to talk discreetly.

After being refused, she says, "Fine, if you don't take the cat, I'm just going to dump it on the street." She has a brief staredown with the woman behind the counter, maybe assuming she can guilt the clinic into taking her cat, then walks away.

Another customer—a big, beefy guy—who has been watching this, intercepts her before she can get to the door. And proceeds to say something so vivid, I wish I could repeat it verbatim, but I can paraphrase it with some highlights.

"Lady, you want to dump the cat? Fine. I'm going to give you what you want. I'll take your cat."

"But the price is that I'm going to berate you in front of everyone here, you useless fucking cunt. You're so goddamned selfish you won't even cough up 69 cents a day for a can of Friskies? You don't fucking deserve the generosity of the people who work here. You want to fucking blackmail them into preventing a cat murder? You disgust me."

This was R. Lee Ermey-level shit.

By now, the doctor herself has shown up. She does not know exactly what is happening, but it has gotten pretty loud. Obviously, she does not like people swearing at others in her waiting room—it is bad for business. The guy turns to her and says, "Look, you're probably used to it, but I get angry when I see people who mistreat animals."

---
Freshman and sophomore year, the same kid gave me shit at the bus stop and the whole walk home. Every single day, nonstop harassment—just kept needling me constantly. So many people asked me why I took it, but I was just really shy and passive at that age. I stayed quiet and did not react.

One day, the kid tried to push me into some bushes, thinking it would be funny. He had never gotten physical before. I grabbed his wrist and put him on his ass. He went down on his back, and when he tried to get up, I put the past two years into a single punch that put him right back down.

The next day at school, the kid had the darkest black eye I had ever seen. He was not at the bus stop for the next few days, and when he started taking it again, he never said another word.

I shocked a bunch of people, but it turns out lots of other kids hated this guy and were jealous I gave him what he had coming. It did a lot of good for me, and the positive reaction kind of helped me come out of my shell.

10/10 would punch again.

---
There was a kid at my school in about 7th grade named Fredrick. He was loved by everyone—super nice, donated to charity regularly, and was well-respected.

One day, a new kid came to our school—we will call him Josh.

Josh was a big douche. He hit people, pushed them around, threw food at people during lunch—just honestly a big ass. One day, he decided to pick on Fred by doing his usual shit, and Fredrick just went ballistic—punching, screaming, kicking. They were both suspended for 2 or 3 days.

After their suspension, they both came back, and Josh had a black eye, bruises on his arms and left leg—he looked awful. He thought everyone would start to hate Fred after what he did to him.

But nope. Everyone was tired of his shit and started picking on him for how bad he looked.

Fred was just loved even more after that. Though he told me he got grounded for a week.

---
I consider myself a nice, friendly guy, and I am pretty quiet. I was dating this girl, and it turned out my friend—who I consider even friendlier than I am—had dated her as well. My friend told me she was a really toxic person. It did not bother me too much since I am one of those people who does not like to judge others based on someone else’s opinion.

But about a month or two into the relationship, I started to see exactly what my friend was talking about. A few days later, I broke up with her. In the following days, she started shit-talking me and spreading rumors about both me and my friend. My friend’s boyfriend heard these rumors and broke up with her too. So we were both pretty pissed about the situation.

Three days later, my friend caught her ex kissing my ex and confronted them. She was relatively chill about it—it is not like he was really cheating—but it still hurt either way. She was about to leave when my ex said, "It probably hurts you more to know I was doing him while you were dating."

My friend slowly turned around and asked her to repeat herself. My ex happily obliged.

Worst mistake of her life.

My friend jumped on her and started beating the shit out of her, even ripping out some of her hair. When she was done with her, she walked up to her ex and said, "You want to cheat on me, that is fine. But you can get your shit beat with her," then slapped him and kicked him in the nuts.

We still talk about this today.

---
I used to be really shy and quiet. As the only daughter of a single working mother, it was hard to socialize with kids my age when everyone around me was 6-10 years older. This happened around '97-'98.

My mom decided to put me in a private school, and it was the biggest change of my life. These kids knew about computers, music, and English (I am from Mexico), while I only knew the essentials since I had come from public schools. The first few weeks were a nightmare because this girl decided to make fun of me—my skin (I was a lot darker, and she was white) and my accent (these kids did not have the regional accent for whatever reason).

Things continued like that, and every day I felt sadder and lonelier until one day, I just snapped.

I had started becoming friends with a girl who liked the same cartoons as I did (Dragon Ball, Pokémon, etc.), and my bully did not like that I was not letting her push me around anymore. One day, she decided to poke me with her pencil while we were in class, knowing I was too shy to say anything in front of the teacher. She kept poking me until the teacher had to step out for something, so I just grabbed her pencil and threw it away.

We started fighting in the middle of the classroom while everyone was either cheering, trying to stop us, or running out to get the teacher. She ended up pinching, scratching, and hitting me, but she never expected me to actually fight back—and fight back dirty. I grabbed her hair, punched her in the stomach, and bit her.

I do not remember what happened next or how I avoided getting expelled, but two weeks later, I was at recess, eating my lunch and happily talking with my best friend, when out of nowhere, the bully walked up to us, handed me a bag of pizza-flavored Cheetos, and we never spoke about it again.
---
My brother was a sweet kid (emphasis on sweet) in elementary school. This was the early 2000s—he was probably 8 at the time. Anyway, he did wrestling and baseball to pass the time but was generally just a pretty average kid. He was smart and had a good number of friends from the sports he played. Nothing special.

But there was one kid who bullied him a lot. For no real reason. The bully’s name was Garrett, and he would call my brother names and hide his pencils and pens to get him yelled at in class.

Well, one day, Garrett, for some odd reason, decided to literally slap my brother in the face with a school lunch. A piece of pizza or something—maybe chicken-fried steak.

My brother got up, grabbed him by his shirt, and slammed him to the floor, breaking the kid’s nose and maxilla (upper jaw below the nose). After that, everyone started calling him Garrett the Ferret because he had to have his mouth wired shut.

Fast forward a few years, and I was being bullied. And surprisingly, Garrett actually stood up for me. I do not know if he got his shit together or was just afraid of someone bullying me, knowing how my brother handles things.
---
This is actually my story, which I have told in parts before.

So, me and this guy were friends in high school but became basically inseparable from the end of junior year to graduation. We hung out a lot until I moved four hours away for college. He started doing pot in high school, and I tried it but never saw the hype.

Gradually, he started doing more and more shady things. We had a well-established bro code in our friend group and all agreed on the rules when setting it up. One of the rules was "Don't date a bro's ex without his permission." I had a sketchy ex that he wanted to date, so I warned him about her but recognized that his life was his choice.

Then, he broke up with her—which I kinda saw coming. After a while, he became really self-absorbed because he got a college grant and started shoving it in everyone's face. Basically, he got free college and $1,500 a month while he was in class to spend on whatever.

While this was all happening, I was going through my own troubles but kept them to myself. Once those started to boil over, I talked with him about them.

I hated my job and was worried that I had gotten my then-girlfriend pregnant (I didn’t, thankfully). I was having an anxiety attack over it, and he called me a "little bitch." Definitely not high on the list of comforting things to say.

A couple of months later, the ex that I was heartbroken to leave when I moved posted on his story, "hacked, love you babe lol."

I Was Livid.

He basically shrugged it off and said, "You didn’t want her, so why are you upset?" Well, when we all promised not to do that, I held you to it. That shouldn’t be a surprise.

Finally, a couple of months later, I was even more depressed. My girlfriend broke up with me, I was still at that job, on the wrong antidepressants, and had no friends where I lived.

One day, he calls me at 11 PM and says, "Hey, me and (other friend) are online, get on."

I calmly say, "Nah man, I’m tired. I’m going to bed."

He says, "Ugh. You always do this! Putting yourself before your friends!"

I stopped.

I retaliated, "That’s some big talk for someone who’s come to visit me once in three years."

I had driven four hours one way to spend time with them four times in that span, and I was fucking broke. This motherfucker had no money problems or job.

This, of course, started a fight, which escalated the more we talked. Whole paragraphs of him saying I’m a bad friend for not putting him first, and me providing legitimate evidence as to why I was sick of his shit.

Finally, he called me a little bitch again, and I said, "Fuck it, gloves are off. Here’s all the shit you’ve done to me."

I listed everything he had done and never apologized for, and everything I had done for him without a single thank you—and there was a lot.

To this, he said, "You’re not gonna keep any friends like me if you treat them like this."

And I simply said, "Good. That’s the point."

I have not spoken to him in two years and have no intention to. I will not apologize because I have nothing to apologize for.
---
To make a long story short, I went to a middle school that was very conspicuously gerrymandered—about 60% of the students came from upper-middle-class neighborhoods, while the remaining 40% lived in what felt like the backdrop of a 90s John Singleton film. That being said, it was an interesting mix of students and always a great laugh.

In 8th grade, I decided to take Spanish as a foreign language. While I was serious about learning as much as I could, the other half of the class spent most of our periods roasting each other, beatboxing, and generally turning the room into pure chaos and good humor.

Enter my Spanish teacher. She was at most twenty-three, beautiful, sweet, and very naive. From the moment she walked into the class, she truly believed she was there to change lives—a task whose impossibility would quickly become apparent.

As time went on and the absolute madness in the classroom became more and more apparent, one day she just snapped. She walked over to the corner where some of my classmates were literally playing dice—gambling in the middle of class—grabbed their cardboard and dice, threw them across the room, and just exploded. I have never seen anything like it. She went from sweet and soft-spoken to screaming at the top of her lungs, completely losing it.

In a single class period, she suspended nine students, threatened suspensions for anyone who so much as spoke a single word for the rest of the year, and even flagged down security guards to physically remove some of the more intense problem students from their desks.

About a week later, she disappeared and was never seen at school again.

---
Wasn’t a friend, but it was me.

In high school, we had a program for mentally challenged kids, and it included students with a range of different disabilities.

One day, I was with my friends during lunch when we noticed a big circle of kids. Curious, we walked up to see what was going on—only to find some complete jerk shoving and making fun of a disabled kid.

You could tell the kid was scared and confused, not understanding what was happening. Nobody stepped in to help. Everyone just watched. Before I could do anything, the supervisors came and broke it all up, but I was still pissed.

After school, I found that guy and asked him why he thought that was funny. He was with his friends, and he tried to act tough, saying, "It was just a joke, I was just messing around."

I snapped and beat the crap out of him right there in front of his friends. They tried to stop me, but I was already too pissed.

When I was done, I looked at the rest of them and asked, "Anyone else want to go a round with me?"

They didn’t say a word and just walked away with their friend.

Who in their right mind thinks it is okay to bully and pick on a disabled kid? Seriously. Some people have no decency.

---
A really calm friend of mine got annoyed every single day by this other dude in our class.

I do not know if I would call it bullying, but it was just nonstop stupid little things every single day, and he would not leave him alone for months. He kept pushing it further and further—up to a point where he would literally spend hours in class tossing paper balls at him, page after page. Then, he switched to those spitball things, shooting them out of a blowgun made from a pen.

One day, as usual, he kept doing it over and over. It was hot in school, we had no ventilation, everyone was sweating and feeling itchy, and it was a long school day.

Then it happened.

The dude started crumpling up full notebook pages into hand-sized balls and throwing them at my friend's head whenever the teacher was not looking. After a few of those, my friend, without even turning around, said just one thing:

"I dare you to throw another one."

It was odd—especially the cold tone he spoke in.

The guy hesitated for about five seconds, then ripped off another notebook page and formed it into a ball again.

The second he was mid-throw, my friend stood up, grabbed his chair from beneath him, swung it over his head, and hammered that chair down on the bully.

The dude barely had time to react—he instinctively put his throwing arm up as protection against the impending doom about to hit him.

I have never heard a bone break before, but that guy's hand literally shattered. It made the weirdest sound I have ever heard a body make.

The bully fell back, still cradling his now deformed hand, just staring at my friend in shock.

My friend just calmly stood up and left the classroom because he knew he was heading straight to the principal's office.

I think he was suspended for a week.

The only thing I can say after that is—that guy never messed with him again.

No one did.

That was probably one of the most badass things I have ever seen, but honestly, that bully had it coming. I am honestly surprised my friend only hit him once.
---
Bit of a different story, but it made me think of it—

There was this guy I was friends with, maybe dating. He was oddly detached but extremely, extremely kind to me. I was the only person he seemed to like, other than his mom. He never did anything but sweet, incredibly thoughtful things for me—he found my favorite album on vinyl and had it ready to go every time I came over, let me nap and tucked me into his bed when I showed up exhausted after work, even taught himself how to make special hot chocolate from scratch just to drink it with me and pretended to like coffee because I loved it.

One time, we were sitting in his living room at his cabinet grand piano. I am a singer, and he would always ask me to sing for him whenever he could—whether it was singing along to vinyls in his room, messing around while we ate lunch, or playing karaoke tracks on YouTube just so I could sing to him. He said my voice brought him peace.

He knew a little bit of piano, enough from childhood lessons to get by, and we were sharing the piano bench while he noodled around on the keys and I tried to make a melody over it.

Then his little brother came up the stairs—completely harmlessly—talking to their mom in the open-concept kitchen. The guy I was with immediately turned around and yelled at him, as brothers do—

"Can you be quiet? I can't hear her."

His brother shot back, "Shut up, I’m just talking to Mom," clearly pushing his buttons.

And then—

The guy I was with got up off the bench, jumped clear over the coffee table, and threw a full-force right hook straight into his brother’s jaw—just because he was speaking over my song.

There was a little blood.

I was so horrified—but mostly just shocked. It happened so fast I couldn’t even blink.

I later realized he had an extremely violent temper and was probably, genuinely, a sociopath. He seemed to feel no real empathy toward anything. I made myself disappear and have not seen him since.

But the weirdest part? He never did anything but kind things for me, always.

It was strange.

Anyways, that is that story.
---
Somebody messed with my brother. Don’t do that.

Middle school—I was in 8th grade, my brother was in 7th. I had never fought anyone in my life, never made a point of being mean, and hated confrontation up until this point.

One day after school, I walked outside to where we got picked up and saw some kids shoving my brother around, throwing snow at him, swinging their binders at him, and calling him a bunch of vile, nasty names I do not even want to think about.

I lost it. Absolutely lost it.

I pulled my brother out of there and just started screaming and swinging. He was crying, I was yelling so loud my voice hurt for a week. I told them to leave, get the fuck out, all while surrounded by people who had never heard me curse or raise my voice against anyone.

I do not really remember much of what happened after that, but I know they got suspended for a week and stuck with some random school chores or something.

Nobody ever messed with him again—at least, not at that school.

You can mess with me or bully me all you want, but don’t touch my family.

I have not fought or lost it at anyone since. My brother and I still fight with each other, because we are siblings and that is what siblings do, but he knows I have his back no matter what.




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
                transition_clip = VideoFileClip("video/transition_6.mp4").resized(res).with_start(current_time)

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
        if file.endswith(".mp3"):
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