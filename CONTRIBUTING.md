# Contributing to Neosantara AI Examples

Thank you for your interest in contributing to the Neosantara AI examples! We welcome community contributions to help developers better understand how to integrate our Indonesian LLM gateway with various frameworks.

## How to Contribute

1.  **Fork the repository**: Create a copy of this repository on your GitHub account.
2.  **Create a new folder**: If you are adding a new framework or a significantly different example, create a dedicated folder.
3.  **Adhere to conventions**:
    *   Use English for `README.md` files.
    *   Include a `requirements.txt` for dependencies.
    *   Provide a clear explanation of how the example works with Neosantara.
4.  **Use Model IDs**: Always use official model IDs (e.g., `claude-3-haiku`, `kimi-k2`) rather than generic names.
5.  **Submit a Pull Request**: Provide a clear description of your changes and why they are valuable.

## Development Guidelines

*   **OpenAI Compatibility**: Neosantara is OpenAI-compatible. Use standard SDKs (OpenAI, LangChain, LiteLLM) and point the `base_url` to `https://api.neosantara.xyz/v1`.
*   **Security**: Never commit API keys. Use `.env` files and include an `.env.example` template.
*   **Testing**: Ensure your example runs without errors before submitting.

We appreciate your help in making Neosantara AI more accessible to developers!
