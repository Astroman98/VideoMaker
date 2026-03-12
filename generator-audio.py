# archivo: azure_tts_mp3.py
# Requisitos:
#   pip install azure-cognitiveservices-speech

import os
import sys
from xml.sax.saxutils import escape
import azure.cognitiveservices.speech as speechsdk


def guess_lang_from_voice(voice_name: str) -> str:
    parts = voice_name.split("-")
    if len(parts) >= 2:
        return f"{parts[0]}-{parts[1]}"
    return "en-US"


def synthesize_mp3(
    text: str,
    output_file: str,
    voice: str = "es-US-AlonsoNeural",
    rate: str = "+0%"
) -> None:
    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION")

    if not key or not region:
        raise RuntimeError(
            "Faltan variables de entorno. Define AZURE_SPEECH_KEY y AZURE_SPEECH_REGION."
        )

    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.speech_synthesis_voice_name = voice
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio24Khz48KBitRateMonoMp3
    )

    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    lang = guess_lang_from_voice(voice)
    safe_text = escape(text)

    ssml = (
        f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{lang}">'
        f'<voice name="{voice}">'
        f'<prosody rate="{rate}">{safe_text}</prosody>'
        f"</voice>"
        f"</speak>"
    )

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


def main() -> int:
    text = "Hola, esta es una prueba de Azure Text to Speech."
    output_file = "salida.mp3"
    voice = "es-US-AlonsoNeural"
    rate = "+10%"

    try:
        synthesize_mp3(text, output_file, voice, rate)
        print(f"Listo. Audio guardado en: {output_file}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
