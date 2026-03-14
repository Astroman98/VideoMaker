# archivo: generate_title_eng.py
# Requisitos:
#   pip install azure-cognitiveservices-speech
# Variables de entorno:
#   AZURE_SPEECH_KEY
#   AZURE_SPEECH_REGION

from moviepy import TextClip, CompositeVideoClip, VideoFileClip, AudioFileClip
from moviepy import CompositeAudioClip
from moviepy.audio.AudioClip import AudioArrayClip
from moviepy import concatenate_audioclips
import asyncio
import os
import keys
import numpy as np
from xml.sax.saxutils import escape
import azure.cognitiveservices.speech as speechsdk
from moviepy.video.fx.FadeOut import FadeOut
from moviepy.video.fx.FadeIn import FadeIn
from moviepy.audio.fx.AudioFadeIn import AudioFadeIn
from moviepy.audio.fx.AudioFadeOut import AudioFadeOut


def solicitar_intro_video():
    if "ENG_INTRO" in os.environ:
        return os.environ["ENG_INTRO"]

    print("\n--- INTRO VIDEO CONFIGURATION ---")
    print("Available intro files in 'video' folder:")

    archivos_intro = [f for f in os.listdir("video") if f.startswith("intro") and f.endswith(".mp4")]

    if not archivos_intro:
        print("No intro files found in the 'video' folder.")
        return "intro8.mp4"

    for i, archivo in enumerate(archivos_intro, 1):
        print(f"{i}. {archivo}")

    seleccion = input("\nSelect the intro video number to use (or press Enter to use intro8.mp4): ")

    if not seleccion:
        return "intro8.mp4"

    try:
        indice = int(seleccion) - 1
        if 0 <= indice < len(archivos_intro):
            print(f"Using intro video: {archivos_intro[indice]}")
            return archivos_intro[indice]
        print("Selection out of range. Using intro8.mp4")
        return "intro8.mp4"
    except ValueError:
        print("Invalid input. Using intro8.mp4")
        return "intro8.mp4"


def _guess_lang_from_voice(voice_name: str) -> str:
    parts = voice_name.split("-")
    return "-".join(parts[:2]) if len(parts) >= 2 else "en-US"


def _azure_tts_to_wav(text: str, output_wav: str, voice: str, rate: str) -> None:
    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION")

    if not key or not region:
        raise RuntimeError("Faltan AZURE_SPEECH_KEY o AZURE_SPEECH_REGION en el entorno.")

    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.speech_synthesis_voice_name = voice
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Riff48Khz16BitMonoPcm
    )

    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_wav)
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
    del synthesizer

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return

    if result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        msg = f"TTS cancelado: {details.reason}"
        if details.error_details:
            msg += f" | {details.error_details}"
        raise RuntimeError(msg)

    raise RuntimeError(f"TTS falló: {result.reason}")


async def generate_title_video(
    text="Hello, this is a title",
    resolution=(1920, 1080),
    font_size=140,
    font_color="#cfcfcf",
    voz="en-US-ChristopherNeural",
    rate="+7%",
):
    intro_video = solicitar_intro_video()
    os.makedirs("audio", exist_ok=True)

    audio_file = "audio/eng_title_audio.mp3"

    # Azure TTS en hilo para no bloquear el loop
    await asyncio.to_thread(_azure_tts_to_wav, text, audio_file, voz, rate)

    background = VideoFileClip(f"video/{intro_video}", audio=False).resized(resolution)
    tts_audio = AudioFileClip(audio_file)

    silence_duration = 1
    fps = tts_audio.fps
    samples = int(fps * silence_duration)
    silence_array = np.zeros((samples, 2), dtype=np.float32)
    silence_clip = AudioArrayClip(silence_array, fps=fps)
    combined_audio = concatenate_audioclips([silence_clip, tts_audio])

    duration = combined_audio.duration

    background_music = AudioFileClip("music/intro_sound.mp3")
    if background_music.duration > duration:
        background_music = background_music.subclipped(0, duration)

    audio_fadein = AudioFadeIn(1.5).copy()
    audio_fadeout = AudioFadeOut(0.8).copy()
    background_music = audio_fadein.apply(background_music)
    background_music = audio_fadeout.apply(background_music)

    background = background.subclipped(0, duration)

    text_clip = TextClip(
        text=text,
        font_size=font_size,
        color=font_color,
        font="font/Grand_Aventure_Text.otf",
        text_align="center",
        method="caption",
        stroke_width=2,
        stroke_color="black",
        size=(resolution[0] - 100, None),
        margin=(100, 100),
    ).with_position("center")

    final_audio = CompositeAudioClip([combined_audio, background_music])

    final_clip = CompositeVideoClip([background, text_clip], size=resolution).with_duration(duration)
    final_clip = final_clip.with_audio(final_audio)

    fade_in = FadeIn(1.5).copy()
    fade_out = FadeOut(0.8).copy()
    final_clip = fade_in.apply(final_clip)
    final_clip = fade_out.apply(final_clip)

    final_clip.write_videofile(
        "title(eng).mp4",
        fps=60,
        codec="libx264",
        bitrate="20000k",
        audio_codec="aac",
        audio_bitrate="320k",
        preset="medium",
        threads=8,
        ffmpeg_params=[
            "-crf", "17",
            "-profile:v", "high",
            "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-tune", "film",
            "-movflags", "+faststart",
            "-bf", "2",
            "-g", "30",
            "-keyint_min", "25",
            "-sc_threshold", "40",
            "-b_strategy", "1",
            "-qmin", "10",
            "-qmax", "51",
        ],
    )

    final_clip.close()
    text_clip.close()
    background.close()
    tts_audio.close()
    background_music.close()
    combined_audio.close()


if __name__ == "__main__":
    asyncio.run(generate_title_video(text="Hello, this is a title"))
