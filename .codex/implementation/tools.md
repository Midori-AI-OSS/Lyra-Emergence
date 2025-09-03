# LangChain Tool Integrations

The `src/tools` package provides LangChain `Tool` classes for journal ingestion and search. These tools may be disabled based on the runtime environment:

- All tools are disabled when the host OS is not **PixelArch**.
- Network-dependent tools are disabled when internet connectivity is unavailable or when `https://tea-cup.midori-ai.xyz/health` is unreachable.

When adding or updating tools, review LangChain's official tool integration guide:

<https://python.langchain.com/docs/integrations/tools/>

Update this document whenever new tools are introduced or existing ones are modified.
