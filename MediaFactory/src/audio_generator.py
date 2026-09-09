import asyncio
import edge_tts

async def synthesize_speech(text: str, output_path: str = "output_voice.mp3", voice: str = "en-US-ChristopherNeural"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def create_audio(text: str, output_path: str = "output_voice.mp3"):
    asyncio.run(synthesize_speech(text, output_path))
    print(f"Audio synthesized successfully -> {output_path}")
