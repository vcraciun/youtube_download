import time
from string import Template
import httpx
import pyperclip

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"

OLLAMA_CONFIG1 = {
    "model": "mistral:7b-instruct-v0.2-q4_K_S",
    "keep_alive": "5m",
    "stream": False,
}

OLLAMA_CONFIG2 = {
    "model": "vicuna",
    "keep_alive": "5m",
    "stream": False,
}

OLLAMA_CONFIG3 = {
    "model": "llama2:70b",
    "keep_alive": "5m",
    "stream": False,
}

PROMPT_TEMPLATE_DE = Template(
    """Translate this text from English to German:

$text
"""
)

PROMPT_TEMPLATE_RO = Template(
    """Translate this text from English to Romanian:

$text
"""
)

PROMPT_TEMPLATE_GR = Template(
    """Translate this text from English to Greek:

$text
"""
)


def Translate(text, lang):
    lang_templates = {
        "ro": PROMPT_TEMPLATE_RO,
        "de": PROMPT_TEMPLATE_DE,
        "gr": PROMPT_TEMPLATE_GR
    }    
    if lang not in lang_templates:
        return ""
    prompt = lang_templates[lang].substitute(text=text)
    response = httpx.post(
        OLLAMA_ENDPOINT,
        json={"prompt": prompt, **OLLAMA_CONFIG3},
        headers={"Content-Type": "application/json"},
        timeout=600,
    )
    if response.status_code != 200:
        print("Error", response.status_code)
        return None
    return response.json()["response"].strip()

def Normalize(result):
    result = result.replace('\u0103', 'a')
    result = result.replace('\u021b', 't')
    result = result.replace('\u0219', 's')
    return result

with open('Slaying the Dragon Within Us_correct_ro.txt', 'w', encoding='utf-16le') as g:
    with open('Slaying the Dragon Within Us_correct.txt', 'r') as f:    
        i = 1
        for ln in f.readlines():
            print(f"Translating paragraph [{i}]")
            data = ln.strip()
            result = Translate(data, 'ro')
            #result = Normalize(result)
            g.write(result)
            g.write('\n')
            i += 1
            break
