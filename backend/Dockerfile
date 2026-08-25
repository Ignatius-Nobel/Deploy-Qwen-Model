FROM python:3.11-slim
WORKDIR /app

# CPU-only torch first — large layer, cached separately
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# App deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Bake model into the image — no HF token needed, no download at runtime
ENV HF_HOME=/app/hf_cache
RUN python -c "\
import torch; \
from transformers import AutoTokenizer, AutoModelForCausalLM; \
AutoTokenizer.from_pretrained('Qwen/Qwen2.5-0.5B-Instruct'); \
AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-0.5B-Instruct', torch_dtype=torch.bfloat16); \
print('Model baked.')"

ENV TRANSFORMERS_OFFLINE=1
ENV MODEL_ID=Qwen/Qwen2.5-0.5B-Instruct

# --preload: master loads model before forking workers (faster worker start)
# -w 1:      single worker keeps the model in one process
# --timeout: covers both model load time and slow inference
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5001", "--timeout", "600", "app:app"]
