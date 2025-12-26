import os, csv, datetime, requests
from slugify import slugify

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:8b-instruct"

SYSTEM = ("You write concise, factual buying guides. Short sentences. "
          "Avoid hype. Ban these verbs in marketing copy: experience, discover, uncover, explore.")

PROMPT_TMPL = """{system}

Write a structured article in Markdown about: "{kw}".
Sections:
- Intro (2–3 short sentences)
- Top Picks (explain selection criteria; do not invent specs)
- Buying Guide (materials, sizes, care)
- FAQs (5)
Add YAML front matter at the very top with fields:
title: "{title}"
description: ""
date: "{date}"
draft: false
products: []
"""

def call_ollama(prompt: str) -> str:
    r = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": prompt, "stream": False}, timeout=180)
    r.raise_for_status()
    return r.json()["response"]

def main():
    os.makedirs("content/posts", exi t_ok=True)
    with open("scripts/10_keywords.csv") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            kw = row["keyword"].strip()
            slug = slugify(kw)
            outp = f"content/posts/{slug}.md"
            if os.path.exists(outp):
                continue
            prompt = PROMPT_TMPL.format(
                system=SYSTEM,
                kw=kw,
                title=kw.capitalize(),
                date=datetime.date.today().isoformat()
            )
            md = call_ollama(prompt).strip()
            # Ensure front matter fences if missing
            if not md.startswith("---"):
                fm = f'---\ntitle: "{kw.capitalize()}"\ndescription: ""\ndate: {datetime.date.today().isoformat()}\ndraft: false\nproducts: []\n---\n'
                md = fm + "\n" + md
            with open(outp, "w") as w:
                w.write(md)
            print("Wrote", outp)

if __name__ == "__main__":
    main()
