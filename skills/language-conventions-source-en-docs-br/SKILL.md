---
name: language-conventions-source-en-docs-br
description: Enforces language usage conventions for teams based in Brazil. Use when writing code, documentation, docstrings, comments, configuration, or any project artifact. Brazilian Portuguese for documentation and docstrings; English for everything else (source code, identifiers, parameters, class names, function names, settings, configuration keys, commit messages, PR descriptions).
---

# Language Conventions

## Rule

| Artifact                                                          | Language             |
| ----------------------------------------------------------------- | -------------------- |
| Docstrings                                                        | Brazilian Portuguese |
| README and markdown docs                                          | Brazilian Portuguese |
| Inline comments explaining intent                                 | Brazilian Portuguese |
| Source code (identifiers, variables, functions, classes, modules) | English              |
| Parameters and arguments                                          | English              |
| Settings / configuration keys                                     | English              |
| Exception messages (runtime)                                      | English              |
| Log messages                                                      | English              |
| Test names and assertions                                         | English              |
| Commit messages and PR descriptions                               | English              |

## Examples

**Docstring — Brazilian Portuguese:**
```python
def submit_transcription(audio_path: str) -> str:
    """
    Submete um arquivo de áudio para transcrição assíncrona.

    Args:
        audio_path: Caminho do arquivo de áudio no armazenamento blob.

    Returns:
        Identificador do trabalho de transcrição criado.

    Raises:
        TranscriptionError: Quando o serviço de fala não está disponível.
    """
```

**Source code — English:**
```python
class TranscriptionRepository:
    def find_by_status(self, status: JobStatus) -> list[TranscriptionJob]:
        ...
```

**Inline comment explaining intent — Brazilian Portuguese:**
```python
# Agrupa por locutor antes de calcular métricas de sobreposição
grouped = group_by_speaker(segments)
```

**Settings — English:**
```python
MAX_RETRY_ATTEMPTS = 3
BLOB_CONTAINER_NAME = "audio-uploads"
```

## Checklist

When writing any file, verify:

- [ ] All docstrings are written in Brazilian Portuguese
- [ ] All identifiers (variables, functions, classes, modules) are English
- [ ] Parameter names and type annotations are English
- [ ] Configuration keys and environment variable names are English
- [ ] Inline comments that explain non-obvious intent use Brazilian Portuguese
- [ ] Log messages and exception strings are English
