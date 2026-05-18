import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# API Keys
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
RIVA_KEY = os.getenv("RIVA_API_KEY") or NVIDIA_API_KEY
FLUX_API_KEY = os.getenv("FLUX_API_KEY") or NVIDIA_API_KEY

# NVIDIA Cloud Endpoints
NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
FLUX_API_URL = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.2-klein-4b"
RIVA_GRPC_SERVER = "grpc.nvcf.nvidia.com:443"

# Function IDs
TTS_FUNCTION_ID = "877104f7-e885-42b9-8de8-f6e4c6303969"

# Shared Clients
llm_client = OpenAI(base_url=NIM_BASE_URL, api_key=NVIDIA_API_KEY, timeout=60.0)
