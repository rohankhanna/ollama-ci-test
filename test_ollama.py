#!/usr/bin/env python3
"""Minimal Ollama cloud-direct CI probe.

Proves one thing: a GitHub Actions runner can reach Ollama's cloud endpoint
(https://ollama.com/api/generate) with a Bearer API key and get a model
response back — no local daemon, no `ollama` CLI install, no `requests`
dependency (stdlib urllib only, mirroring the real client this proxies for).

Exit 0 = the cloud-direct path works from CI. Exit 1 = it doesn't (prints why).
OLLAMA_API_KEY is read from the env (the GitHub Actions secret); the key is
never logged.
"""
import json
import os
import sys
import urllib.error
import urllib.request

ENDPOINT = "https://ollama.com/api/generate"
DEFAULT_MODEL = "glm-5.2"


def main() -> int:
    key = os.environ.get("OLLAMA_API_KEY")
    if not key:
        print("FAIL: OLLAMA_API_KEY is not set (configure the repo secret).")
        return 1
    model = os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
    if model.endswith(":cloud"):          # cloud-direct already serves cloud models
        model = model[: -len(":cloud")]

    payload = json.dumps({
        "model": model,
        "prompt": 'Reply with exactly this JSON and nothing else: {"answer":"pong"}',
        "stream": False,
        "format": "json",
    }).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=payload,
        headers={"Content-Type": "application/json",
                  "Authorization": f"Bearer {key}"},
        method="POST",
    )
    print(f"POST {ENDPOINT}  model={model}")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            status = resp.status
            body = resp.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as e:
        print(f"FAIL: network/HTTP error: {e}")
        return 1
    print(f"HTTP status: {status}")
    if status != 200:
        print(f"FAIL: non-200 response body (first 500 chars):\n{body[:500]}")
        return 1
    try:
        obj = json.loads(body)
    except json.JSONDecodeError:
        print(f"FAIL: response not JSON (first 500 chars):\n{body[:500]}")
        return 1
    print(f"model response: {obj.get('response')!r}")
    print(f"model field:    {obj.get('model')!r}")
    print("OK: Ollama cloud-direct works from CI.")
    return 0


if __name__ == "__main__":
    sys.exit(main())