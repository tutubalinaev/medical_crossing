from transformers import AutoTokenizer, AutoModelForMaskedLM

tokenizer = AutoTokenizer.from_pretrained("cambridgeltl/SapBERT-UMLS-2020AB-all-lang-from-XLMR")
model = AutoModelForMaskedLM.from_pretrained("cambridgeltl/SapBERT-UMLS-2020AB-all-lang-from-XLMR")

print(model)