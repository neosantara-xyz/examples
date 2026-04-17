# 🧑‍🍳 Neosantara AI Cookbook

A collection of interactive "recipes" to help you build with Neosantara AI. Each recipe can be opened directly in **Google Colab**.

## 🛠️ Getting Started with Google Colab

If you are new to Google Colab, follow these steps to set up your API Key safely:

1.  **Open a Notebook**: Click any of the "Open in Colab" badges below.
2.  **Set up Secrets**:
    *   On the left sidebar, click the **Key icon (Secrets)** 🔑.
    *   Click **"Add new secret"**.
    *   Name the secret `NEOSANTARA_API_KEY`.
    *   Paste your API Key from the [Neosantara Dashboard](https://app.neosantara.xyz/api-keys) into the "Value" field.
    *   **Enable "Notebook access"** for this secret.
3.  **Run Cells**: Click the Play button ▶️ on each code cell.

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
