from argparse import ArgumentParser
from pathlib import Path

from rich.console import Console
from langchain_huggingface import HuggingFacePipeline
from langchain_core.language_models import BaseLanguageModel

from src.cli.chat import ChatSession
from src.publish.mark import toggle_publish_flag
from src.vectorstore.chroma import ingest_journal
from src.utils.device_fallback import safe_load_pipeline


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "--ingest",
        type=Path,
        help="Path to a journal JSON file to ingest into ChromaDB",
    )
    parser.add_argument(
        "--mark",
        type=str,
        help="Toggle publish flag for the journal entry with the given ID",
    )
    parser.add_argument(
        "--journal",
        type=Path,
        default=Path("data/journal/sample.json"),
        help="Path to the journal JSON file",
    )
    parser.add_argument(
        "--rerank",
        dest="rerank",
        action="store_true",
        help="Enable CPU-based reranking of search results",
    )
    parser.add_argument(
        "--no-rerank",
        dest="rerank",
        action="store_false",
        help="Disable CPU-based reranking",
    )
    parser.add_argument(
        "--model-config",
        type=Path,
        help="Path to model configuration file for sharding and device mapping",
    )
    parser.set_defaults(rerank=True)
    args = parser.parse_args()

    if args.ingest:
        ingest_journal(args.ingest, persist_directory=Path("data/chroma"))
        return

    if args.mark:
        toggle_publish_flag(args.journal, args.mark)
        return

    console = Console()
    console.print("Lyra Project startup initialized.")

    llm: BaseLanguageModel = safe_load_pipeline(
        model_id="microsoft/phi-2",
        task="text-generation",
        config_path=args.model_config,
        pipeline_kwargs={"max_new_tokens": 4000},
    )
    session = ChatSession(console=console, rerank=args.rerank, llm=llm)
    session.run()


if __name__ == "__main__":
    main()
