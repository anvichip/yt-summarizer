import pandas as pd
import openai
import torch
import torch_utils
from pytube import YouTube
import whisper
import torch
import os

model = whisper.load_model("large")
# result = model.transcribe("audio.mp3")
# print(result["text"])
print("sucess")