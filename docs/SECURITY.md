# Minimum security controls

1. Never commit Hugging Face tokens or inference API keys.
2. Use a dedicated inference API key, separate from the Hugging Face token.
3. Keep the Hugging Face token on the cloud host/provider secret store.
4. Use HTTPS for VoiceBridge-to-cloud traffic.
5. Do not expose raw vLLM port 8000 publicly.
6. Restrict ingress to the reverse proxy/gateway and, where practical, known
   application addresses.
7. Rotate any credential that appears in chat, screenshots, logs, or Git.
8. Keep the model's required public attribution in the eventual product/docs:
   "N-ATLaS is an initiative of the Federal Ministry of Communications,
   Innovation and Digital Economy, and powered by Awarri Technologies."
9. Keep validation logs free of PINs, passwords, OTPs, BVNs, card/CVV data.
10. Do not claim N-ATLAS provenance unless the successful provider path is
    actually N-ATLAS.
