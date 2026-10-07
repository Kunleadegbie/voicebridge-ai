import os
import sys
import requests

base = os.getenv("NATLAS_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
key = os.getenv("VLLM_API_KEY", "")
model = os.getenv("MODEL_ID", "NCAIR1/N-ATLaS")

if not key:
    raise SystemExit("Set VLLM_API_KEY before running this test.")

payload = {
    "model": model,
    "messages": [
        {
            "role": "system",
            "content": (
                "You are VoiceBridge, a financial-literacy assistant for everyday "
                "Nigerians. Give simple educational information, not personalised "
                "financial advice. Never request PINs, passwords, OTPs, BVNs, card "
                "numbers or CVVs."
            ),
        },
        {
            "role": "user",
            "content": "What does collateral mean? Answer briefly in Nigerian English.",
        },
    ],
    "temperature": 0.1,
    "max_tokens": 180,
}

r = requests.post(
    f"{base}/v1/chat/completions",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json=payload,
    timeout=180,
)
print("HTTP:", r.status_code)
if not r.ok:
    print(r.text)
    sys.exit(1)

data = r.json()
print("MODEL:", data.get("model"))
print("RESPONSE:")
print(data["choices"][0]["message"]["content"])
