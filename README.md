# ollama-ci-test

A throwaway repo to prove one thing: **Ollama's cloud endpoint is reachable
from a public GitHub Actions runner using only a Bearer API key** — no local
Ollama daemon, no `ollama` CLI install, no `requests` dependency (stdlib
`urllib` only).

## Why

Before wiring an LLM pass into a real repo's CI, confirm the transport works
in isolation. This repo runs a single manual workflow (`Ollama CI probe`,
`workflow_dispatch` only) that POSTs a trivial prompt to
`https://ollama.com/api/generate` with `Authorization: Bearer $OLLAMA_API_KEY`
and prints the model's response. Green = the cloud-direct path works from CI.

## Setup (one-time, by the operator)

1. Create an Ollama API key at https://ollama.com/settings/keys.
2. Set it as a repo secret (prompts for the value locally; the key never
   enters the repo or git history):

   `gh secret set OLLAMA_API_KEY -R rohankhanna/ollama-ci-test`

## Run

```
gh workflow run test.yml -R rohankhanna/ollama-ci-test
gh run watch     -R rohankhanna/ollama-ci-test
```

Green `probe` job = proven. Delete the repo when done.