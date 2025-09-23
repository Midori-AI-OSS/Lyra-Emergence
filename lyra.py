from argparse import ArgumentParser
from pathlib import Path

from langchain_core.language_models import BaseLanguageModel
from rich.console import Console

from src.cli.chat import ChatSession
from src.journal.paths import JournalPathError
from src.journal.paths import normalize_journal_path
from src.publish.mark import toggle_publish_flag
from src.utils.env_check import get_env_status
from src.vectorstore.chroma import ingest_journal
from src.utils.device_fallback import safe_load_pipeline
from src.config.model_config import load_config


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "--notui",
        action="store_true",
        help="Disable the Text User Interface (TUI) and run in command-line mode",
    )
    parser.add_argument(
        "--model-config",
        type=Path,
        help="Path to model configuration file for sharding and device mapping",
    )
    parser.add_argument(
        "--no-auto-select",
        action="store_true",
        help="Disable automatic model selection and require manual model configuration",
    )
    
    # Legacy command line tools (deprecated in favor of TUI)
    parser.add_argument(
        "--ingest",
        type=Path,
        help="Path to a journal JSON file to ingest into ChromaDB (deprecated: use TUI tools menu)",
    )
    parser.add_argument(
        "--mark",
        type=str,
        help="Toggle publish flag for the journal entry with the given ID (deprecated: use TUI tools menu)",
    )
    parser.add_argument(
        "--journal",
        type=Path,
        default=Path("data/gemjournals/sample.json"),
        help="Path to the journal JSON file",
    )
    
    args = parser.parse_args()

    # Detect environment status so other modules can react accordingly
    get_env_status()

    # Handle legacy command line tools
    if args.ingest:
        ingest_journal(args.ingest, persist_directory=Path("data/chroma"))
        return

    if args.mark:
        console = Console()
        try:
            journal_path = normalize_journal_path(args.journal)
            updated = toggle_publish_flag(journal_path, args.mark)
        except JournalPathError as exc:
            console.print(f"❌ {exc}", style="bold red")
            raise SystemExit(1)
        if not updated:
            console.print(
                f"⚠️  Entry {args.mark} was not found in {journal_path}",
                style="bold yellow",
            )
            raise SystemExit(1)
        console.print(
            f"✅ Toggled publish flag for entry {args.mark} in {journal_path}",
            style="bold green",
        )
        return

    # Default behavior: Launch TUI unless --notui is specified
    if not args.notui:
        from src.cli.tui import run_tui

        run_tui()
        return

    # Command-line mode (when --notui is specified)
    console = Console()
    console.print("Lyra Project startup initialized.")

    # Load model configuration (auto-select is default unless disabled)
    auto_select = not args.no_auto_select
    config = load_config(config_path=args.model_config, auto_select=auto_select)

    llm: BaseLanguageModel = safe_load_pipeline(
        model_id=config.model_id,
        task=config.task,
        config_path=args.model_config,
        pipeline_kwargs=config.to_pipeline_kwargs(),
    )
    # Reranking is always enabled
    session = ChatSession(
        console=console, rerank=True, llm=llm, model_id=config.model_id
    )
    session.run()


if __name__ == "__main__":
    main()
