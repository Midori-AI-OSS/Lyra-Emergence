from argparse import ArgumentParser
from pathlib import Path

from langchain_core.language_models import BaseLanguageModel
from rich.console import Console

from src.cli.chat import ChatSession
from src.config.model_config import load_config
from src.publish.mark import toggle_publish_flag
from src.utils.device_fallback import safe_load_pipeline
from src.vectorstore.chroma import ingest_journal


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
    parser.add_argument(
        "--auto-select",
        action="store_true",
        help="Automatically select optimal model based on available system resources",
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        help="Launch the Text User Interface (TUI) for interactive use",
    )
    parser.set_defaults(rerank=True)
    args = parser.parse_args()

    if args.ingest:
        ingest_journal(args.ingest, persist_directory=Path("data/chroma"))
        return

    if args.mark:
        toggle_publish_flag(args.journal, args.mark)
        return

    # Launch TUI if requested
    if args.tui:
        from src.cli.tui import run_tui

        run_tui()
        return

    console = Console()
    console.print("Lyra Project startup initialized.")

    # Load model configuration (with optional auto-selection)
    config = load_config(config_path=args.model_config, auto_select=args.auto_select)

    llm: BaseLanguageModel = safe_load_pipeline(
        model_id=config.model_id,
        task=config.task,
        config_path=args.model_config,
        pipeline_kwargs=config.to_pipeline_kwargs(),
    )
    session = ChatSession(
        console=console, rerank=args.rerank, llm=llm, model_id=config.model_id
    )
    session.run()


if __name__ == "__main__":
    main()
