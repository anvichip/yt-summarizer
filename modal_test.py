import modal
import asyncio
import tempfile
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import ffmpeg
from typing import Dict
from modal import web_endpoint


image = (
    modal.Image.debian_slim()
    .apt_install("git", "ffmpeg")
    .pip_install(
        "https://github.com/openai/whisper/archive/v20230314.tar.gz",
        "ffmpeg-python",
        "pytube @ git+https://github.com/felipeucelli/pytube",
        "torchaudio",
        "torch",
    )
)
stub = modal.Stub(name="example-whisper-streaming", image=image)
web_app = FastAPI()

@stub.function()
def get_mp3_yt(url):
    from pytube import YouTube
    import io
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    buffer = io.BytesIO()
    video.stream_to_buffer(buffer)
    buffer.seek(0)
    return buffer.read()

@stub.function()
def load_audio(data: bytes, start=None, end=None, sr: int = 16000):
    import ffmpeg
    import numpy as np

    try:
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        fp.write(data)
        fp.close()
        # This launches a subprocess to decode audio while down-mixing and resampling as necessary.
        # Requires the ffmpeg CLI and `ffmpeg-python` package to be installed.
        if start is None and end is None:
            out, _ = (
                ffmpeg.input(fp.name, threads=0)
                .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
                .run(
                    cmd=["ffmpeg", "-nostdin"],
                    capture_stdout=True,
                    capture_stderr=True,
                )
            )
        else:
            out, _ = (
                ffmpeg.input(fp.name, threads=0)
                .filter("atrim", start=start, end=end)
                .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
                .run(
                    cmd=["ffmpeg", "-nostdin"],
                    capture_stdout=True,
                    capture_stderr=True,
                )
            )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0


@stub.function()
def stream_whisper(audio_data: bytes):
    with tempfile.NamedTemporaryFile(delete=False) as fil:
        fil.write(audio_data)
        fil.flush()
        np_array = load_audio.remote(audio_data, start=None, end=None)
        transcripts = transcribe.remote(np_array)
    return transcripts

@stub.function()
def transcribe(np_array):
    import torch
    import whisper

    use_gpu = torch.cuda.is_available()
    device = "cuda" if use_gpu else "cpu"
    model = whisper.load_model("small", device=device)
    result = model.transcribe(np_array, language="en", fp16=use_gpu)  # type: ignore
    return result

#@stub.local_entrypoint()
@stub.function()
@web_endpoint(method="POST")
def main(item: Dict):
    #data = {"url": "https://www.youtube.com/watch?v=Jqoasg8HJsk"}
    #url = 'https://www.youtube.com/watch?v=Jqoasg8HJsk'
    url = str(item['url'])
    bytes = get_mp3_yt.remote(url)
    transcript = stream_whisper.remote(bytes)
    #print(transcript)
    return transcript

