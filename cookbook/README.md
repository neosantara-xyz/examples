# 🧑‍🍳 Neosantara AI Cookbook

A collection of interactive "recipes" to help you build with Neosantara AI. Each recipe can be opened directly in **Google Colab**.

## 🛠️ Getting Started (Desktop & Mobile)

If you are new to Google Colab, here is how to set up your API Key:

### Option A: Use Colab Secrets (Recommended for Desktop)
1. On the left sidebar, click the **Key icon (Secrets)** 🔑.
2. Add a new secret named `NEOSANTARA_API_KEY`.
3. Paste your key from the [Neosantara Dashboard](https://app.neosantara.xyz/api-keys).
4. Enable **"Notebook access"**.

### Option B: Manual Input (Best for Mobile)
If you are on a mobile device or cannot find the Key icon:
1. Simply **run the first code cell**.
2. A password prompt will appear asking for your `Neosantara API Key`.
3. Paste your key there and press Enter.

---

## 🚀 Beginner Recipes
| Recipe | Description | Model Used | Open in Colab |
| :--- | :--- | :--- | :--- |
| **Hello Neosantara** | Basic chat completions & setup | `gemini-3-flash` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/neosantara-xyz/examples/blob/main/cookbook/beginner/hello-neosantara.ipynb) |
| **Image Gen Basics** | Generating images with Flux.1 | `neosantara-gen-2045` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/neosantara-xyz/examples/blob/main/cookbook/beginner/image-gen-basics.ipynb) |
| **Audio Transcription** | High-accuracy speech-to-text | `whisper-large-v3-turbo` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/neosantara-xyz/examples/blob/main/cookbook/beginner/audio-transcription.ipynb) |
| **Streaming Chat** | Real-time response generation | `grok-4.1-fast-non-reasoning` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/neosantara-xyz/examples/blob/main/cookbook/beginner/streaming-chat.ipynb) |
| **Responses API Intro** | Modern, stateful AI Gateway usage | `claude-4.5-sonnet` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/neosantara-xyz/examples/blob/main/cookbook/beginner/responses-api-intro.ipynb) |

## 🧠 Advanced Recipes
| Recipe | Description | Model Used | Open in Colab |
| :--- | :--- | :--- | :--- |
| **Multimodal OCR** | Structured data from images | `glm-4.6-plus` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/neosantara-xyz/examples/blob/main/cookbook/advanced/multimodal-ocr.ipynb) |
| **RAG with ChromaDB** | Knowledge-aware AI pipeline | `llama-3.3-49b` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/neosantara-xyz/examples/blob/main/cookbook/advanced/rag-chromadb.ipynb) |
| **Video Generation** | Text-to-Video generation | `neosantara-video-v1` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/neosantara-xyz/examples/blob/main/cookbook/advanced/video-generation.ipynb) |
| **Guardrails & PII** | Safety & data protection | `nusantara-base` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/neosantara-xyz/examples/blob/main/cookbook/advanced/guardrails-pii.ipynb) |
| **Stateful Conversations** | Automatic history management | `gemini-3-flash` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/neosantara-xyz/examples/blob/main/cookbook/advanced/stateful-conversations.ipynb) |
| **Migration Guide** | Switching from OpenAI SDK | `claude-4.5-sonnet` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/neosantara-xyz/examples/blob/main/cookbook/advanced/openai-to-responses-migration.ipynb) |

---
[Official Documentation](https://docs.neosantara.xyz)
