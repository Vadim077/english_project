import io
import wave
import base64
import json
import grpc
import httpx
from typing import List, Dict, Optional
from config import llm_client, RIVA_KEY, RIVA_GRPC_SERVER, TTS_FUNCTION_ID, NVIDIA_API_KEY, FLUX_API_URL, FLUX_API_KEY

# Riva Protobufs
import riva.client.proto.riva_tts_pb2 as riva_tts
import riva.client.proto.riva_tts_pb2_grpc as riva_tts_grpc

def add_wav_header(pcm_data: bytes, rate=22050) -> bytes:
    """Wraps raw PCM bytes into a standard WAV container."""
    with io.BytesIO() as wav_io:
        with wave.open(wav_io, 'wb') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(rate)
            f.writeframes(pcm_data)
        return wav_io.getvalue()

async def generate_speech(text: str) -> Optional[str]:
    """Generates high-quality speech using NVIDIA Riva gRPC."""
    try:
        metadata = [
            ("authorization", f"Bearer {RIVA_KEY}"), 
            ("function-id", TTS_FUNCTION_ID)
        ]
        
        channel = grpc.secure_channel(RIVA_GRPC_SERVER, grpc.ssl_channel_credentials())
        stub = riva_tts_grpc.RivaSpeechSynthesisStub(channel)
        
        req = riva_tts.SynthesizeSpeechRequest(
            text=text, 
            language_code="en-US", 
            encoding=1, 
            sample_rate_hz=22050, 
            voice_name="Magpie-Multilingual.EN-US.Aria"
        )
        
        resp = stub.Synthesize(req, metadata=metadata)
        wav_header_data = add_wav_header(resp.audio)
        return base64.b64encode(wav_header_data).decode('utf-8')
    except Exception as e:
        print(f"TTS_LOG ERROR: {e}")
        return None

async def call_llm(prompt: str, chat_history: List[Dict]):
    """Standard method to call Llama-3.3 on NVIDIA NIM."""
    res = llm_client.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=[{"role": "system", "content": prompt}] + chat_history,
        response_format={"type": "json_object"},
        temperature=0.7
    )
    return json.loads(res.choices[0].message.content)

async def generate_image(prompt: str) -> Optional[str]:
    """Generates a background image using NVIDIA NIM Flux.1."""
    print(f"DEBUG: Generating image for: {prompt[:30]}...")
    headers = {
        "Authorization": f"Bearer {FLUX_API_KEY}",
        "Accept": "application/json",
    }
    # Оптимизируем промпт для заднего фона
    enhanced_prompt = f"Cinematic interior background of {prompt}, professional photography, high detail, no people, empty scene, architectural shot"
    
    payload = {
        "prompt": enhanced_prompt,
        "width": 1024,
        "height": 768,
        "seed": 0,
        "steps": 4
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(FLUX_API_URL, headers=headers, json=payload, timeout=40.0)
            if response.status_code == 200:
                data = response.json()
                return data['artifacts'][0]['base64']
            else:
                print(f"IMAGE ERROR {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"IMAGE EXCEPTION: {e}")
            return None
