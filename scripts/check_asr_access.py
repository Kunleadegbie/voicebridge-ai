from huggingface_hub import HfApi
MODELS=["NCAIR1/NigerianAccentedEnglish","NCAIR1/Yoruba-ASR","NCAIR1/Hausa-ASR","NCAIR1/Igbo-ASR"]
api=HfApi()
for m in MODELS:
    print("ACCESS VERIFIED:", api.model_info(m).id)
