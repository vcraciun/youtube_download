import time
from string import Template
import httpx
import pyperclip

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_CONFIG = {
    "model": "ifioravanti/mistral-grammar-checker:latest",
    "keep_alive": "5m",
    "stream": False,
}

PROMPT_TEMPLATE1 = Template(
    """Fix all typos, casing and punctuation in this text:

$text

Return only the corrected text, don't include a preamble.
"""
)

PROMPT_TEMPLATE2 = Template(
    """Fix all typos, casing, punctuation and also reformulate and correct the grammar errors in this text:

$text

Return only the corrected text, don't include a preamble.
"""
)


def fix_text(text):
    prompt = PROMPT_TEMPLATE2.substitute(text=text)
    response = httpx.post(
        OLLAMA_ENDPOINT,
        json={"prompt": prompt, **OLLAMA_CONFIG},
        headers={"Content-Type": "application/json"},
        timeout=300,
    )
    if response.status_code != 200:
        print("Error", response.status_code)
        return None
    return response.json()["response"].strip()

correct_text = []
with open('input.txt', 'r') as f:    
    i = 1
    for ln in f.readlines():
        print(f"Correcting paragraph [{i}]")
        data = ln.strip()
        result = fix_text(data)
        correct_text += [result]
        i += 1

with open('output.txt', 'w') as f:
    for item in correct_text:
        f.write(item)
        f.write('\n')

