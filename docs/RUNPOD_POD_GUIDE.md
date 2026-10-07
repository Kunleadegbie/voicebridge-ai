# Runpod Pod deployment guide

This is the recommended first deployment because a Pod gives us direct control
while proving N-ATLAS works. Serverless optimization can come later.

## 1. Create the cloud account
Create/sign in to Runpod and add only a small initial credit balance.

## 2. Create a GPU Pod
Choose an NVIDIA GPU with at least 24 GB VRAM as the first test target.
Use a current PyTorch/CUDA template or a Docker-capable Linux image.
Give the Pod enough disk/volume space for the N-ATLAS weights, Docker layers,
and Hugging Face cache.

Do not choose a CPU-only Pod.

## 3. Connect to the Pod
Use Runpod's web terminal or SSH.

## 4. Confirm GPU
Run:
`nvidia-smi`

Stop if the GPU is not visible.

## 5. Install Docker/Compose if the chosen template does not include them
Follow the cloud image/provider instructions. Then verify:
`docker --version`
`docker compose version`

## 6. Upload this package
Copy the `voicebridge-natlas-cloud` folder to the Pod.

## 7. Create secrets on the Pod
`cp .env.cloud.example .env.cloud`
Edit `.env.cloud`.

Set:
- `HF_TOKEN` to a Hugging Face read token/account token that has N-ATLAS access.
- `VLLM_API_KEY` to a new random secret used only for this inference service.

Never put these secrets into source control or screenshots.

## 8. Start N-ATLAS
`docker compose --env-file .env.cloud up -d`

First startup can take time because the model weights must be downloaded to
the cloud machine.

Follow logs:
`docker compose --env-file .env.cloud logs -f natlas`

Wait until vLLM reports the server is ready.

## 9. Local-on-Pod test
Install requests if needed:
`python3 -m pip install requests`

Load environment values safely in your shell, or set:
`export VLLM_API_KEY='...'`

Run:
`python3 scripts/test_natlas.py`

Expected:
- HTTP 200
- MODEL identifies NCAIR1/N-ATLaS
- a sensible collateral explanation

## 10. Public connectivity
Do not simply expose raw vLLM port 8000 to the Internet. The compose file binds
it to loopback deliberately. Put an HTTPS reverse proxy/provider gateway in
front of it, or use a secure tunnel/private network.

Only after HTTPS access is configured should VoiceBridge be pointed at it.

## 11. Cost control
Stop the Pod when not testing. Confirm whether attached storage continues to
incur charges while compute is stopped. Delete unneeded resources after tests.
