import re

def ready_text_for_pred(text):
    processed_text = re.sub(r" +", " ", (re.sub(r"[^a-zA-Z]", " ", text)).lower().strip())
    return processed_text