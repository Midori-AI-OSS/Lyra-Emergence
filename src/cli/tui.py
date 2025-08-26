"""Text User Interface for Lyra using Rich."""

import asyncio
from typing import Optional, Callable, List
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.align import Align
from langchain_core.language_models import BaseLanguageModel

from src.cli.chat import ChatSession
from src.config.model_config import load_config
from src.config.model_recommendations import get_models_by_category, MODEL_DATABASE
from src.utils.system_info import get_available_memory, get_memory_tier
from src.utils.device_fallback import safe_load_pipeline


class LyraTUI:
    """Text User Interface for Lyra."""
    
    def __init__(self):
        self.console = Console()
        self.llm: Optional[BaseLanguageModel] = None
        self.chat_session: Optional[ChatSession] = None
        self.layout = Layout()
        self.chat_history: List[tuple[str, str]] = []  # (user, bot) pairs
        self.current_model_id: Optional[str] = None  # Track current model for templating
        
    def create_header(self) -> Panel:
        """Create the header panel."""
        title = Text("🌟 Lyra-Emergence Interactive AI", style="bold magenta")
        subtitle = Text("Advanced Language Model Interface", style="dim")
        header_content = Align.center(Text.assemble(title, "\n", subtitle))
        return Panel(header_content, style="blue", padding=(1, 2))
    
    def create_status_panel(self) -> Panel:
        """Create the status panel showing system info."""
        ram_gb, vram_gb = get_available_memory()
        memory_tier = get_memory_tier(ram_gb, vram_gb)
        
        status_table = Table(show_header=False, box=None, padding=(0, 1))
        status_table.add_column("Label", style="cyan")
        status_table.add_column("Value", style="green")
        
        status_table.add_row("💾 Available RAM", f"{ram_gb:.1f} GB")
        status_table.add_row("🖥️  Available VRAM", f"{vram_gb:.1f} GB" if vram_gb > 0 else "No GPU")
        status_table.add_row("📊 Memory Tier", memory_tier.title())
        
        if self.llm:
            # Try to get model info
            model_name = getattr(self.llm, 'model_id', self.current_model_id or 'Unknown')
            status_table.add_row("🤖 Active Model", model_name)
            
            # Show chat template info if available
            if self.chat_session and hasattr(self.chat_session, 'template_manager'):
                template_info = self.chat_session.get_template_info()
                if template_info:
                    template_status = "✓ Auto" if template_info.get("has_chat_template") else "⚠ Fallback"
                    status_table.add_row("🎭 Chat Template", template_status)
        
        return Panel(status_table, title="System Status", style="green")
    
    def create_model_selection_panel(self) -> Panel:
        """Create panel for model selection."""
        table = Table(title="Available Models", show_header=True, header_style="bold cyan")
        table.add_column("Category", style="cyan")
        table.add_column("Model", style="green") 
        table.add_column("Size", style="yellow")
        table.add_column("Description", style="white")
        
        for category in ["small", "medium", "large"]:
            models = get_models_by_category(category)
            for i, model in enumerate(models[:3]):  # Show top 3 per category
                cat_display = category.title() if i == 0 else ""
                table.add_row(
                    cat_display,
                    model.model_id.split("/")[-1], 
                    model.parameter_count,
                    model.description[:50] + "..." if len(model.description) > 50 else model.description
                )
        
        return Panel(table, style="blue")
    
    def show_main_menu(self):
        """Show the main menu and handle navigation."""
        while True:
            self.console.clear()
            
            # Create layout
            layout = Layout()
            layout.split_column(
                Layout(self.create_header(), size=4),
                Layout(name="body"),
                Layout(size=3, name="footer")
            )
            
            # Create body with two columns
            status_panel = self.create_status_panel()
            
            menu_text = Text.assemble(
                ("📝 Main Menu\n\n", "bold cyan"),
                ("1. Start Chat Session\n", "green"),
                ("2. Auto-Select Model\n", "green"), 
                ("3. Manual Model Selection\n", "green"),
                ("4. View Model Database\n", "green"),
                ("5. System Information\n", "green"),
                ("6. Configuration\n", "green"),
                ("7. Exit\n", "green"),
                ("\nEnter your choice (1-7): ", "yellow")
            )
            menu_panel = Panel(menu_text, title="Options", style="blue")
            
            layout["body"].split_row(
                Layout(status_panel, ratio=1),
                Layout(menu_panel, ratio=2)
            )
            
            layout["footer"] = Panel(
                "Use Ctrl+C to return to menu at any time • Press Enter to continue",
                style="dim"
            )
            
            self.console.print(layout)
            
            try:
                choice = Prompt.ask("Choice", choices=["1", "2", "3", "4", "5", "6", "7"], default="1")
                
                if choice == "1":
                    self.start_chat()
                elif choice == "2":
                    self.auto_select_model()
                elif choice == "3":
                    self.manual_model_selection()
                elif choice == "4":
                    self.show_model_database()
                elif choice == "5":
                    self.show_system_info()
                elif choice == "6":
                    self.show_configuration()
                elif choice == "7":
                    self.console.print("👋 Goodbye!", style="bold green")
                    break
                    
            except KeyboardInterrupt:
                self.console.print("\n👋 Goodbye!", style="bold green")
                break
    
    def auto_select_model(self):
        """Automatically select and load optimal model."""
        self.console.clear()
        with self.console.status("[bold green]Auto-selecting optimal model..."):
            try:
                config = load_config(auto_select=True)
                self.current_model_id = config.model_id
                self.llm = safe_load_pipeline(
                    model_id=config.model_id,
                    task=config.task,
                    pipeline_kwargs=config.to_pipeline_kwargs(),
                )
                self.chat_session = ChatSession(console=self.console, llm=self.llm, model_id=self.current_model_id)
                
                self.console.print(f"✅ Successfully loaded model: {self.current_model_id}", style="bold green")
                Prompt.ask("Press Enter to continue")
                
            except Exception as e:
                self.console.print(f"❌ Error loading model: {e}", style="bold red")
                Prompt.ask("Press Enter to continue")
    
    def manual_model_selection(self):
        """Show manual model selection interface."""
        self.console.clear()
        self.console.print(self.create_model_selection_panel())
        
        # Get model choice
        model_id = Prompt.ask("Enter model ID (e.g., Qwen/Qwen2.5-7B-Instruct)")
        
        if model_id:
            with self.console.status(f"[bold green]Loading {model_id}..."):
                try:
                    self.current_model_id = model_id
                    self.llm = safe_load_pipeline(
                        model_id=model_id,
                        task="text-generation",
                        pipeline_kwargs={"max_new_tokens": 4000},
                    )
                    self.chat_session = ChatSession(console=self.console, llm=self.llm, model_id=self.current_model_id)
                    
                    self.console.print(f"✅ Successfully loaded model: {model_id}", style="bold green")
                    
                except Exception as e:
                    self.console.print(f"❌ Error loading model: {e}", style="bold red")
        
        Prompt.ask("Press Enter to continue")
    
    def show_model_database(self):
        """Show the complete model database."""
        self.console.clear()
        
        # Create comprehensive model table
        table = Table(title="🤖 Complete Model Database", show_header=True, header_style="bold cyan")
        table.add_column("Model ID", style="green", width=30)
        table.add_column("Size", style="yellow", width=8)
        table.add_column("Params", style="cyan", width=8)
        table.add_column("Min RAM", style="red", width=8)
        table.add_column("Min VRAM", style="red", width=9)
        table.add_column("License", style="blue", width=12)
        table.add_column("Description", style="white")
        
        for model in MODEL_DATABASE:
            table.add_row(
                model.model_id,
                model.size_category.title(),
                model.parameter_count,
                f"{model.min_ram_gb:.1f}GB",
                f"{model.min_vram_gb:.1f}GB",
                model.license,
                model.description[:40] + "..." if len(model.description) > 40 else model.description
            )
        
        self.console.print(table)
        Prompt.ask("Press Enter to continue")
    
    def show_system_info(self):
        """Show detailed system information."""
        self.console.clear()
        
        ram_gb, vram_gb = get_available_memory()
        memory_tier = get_memory_tier(ram_gb, vram_gb)
        
        info_table = Table(title="🖥️ System Information", show_header=True, header_style="bold cyan")
        info_table.add_column("Component", style="cyan", width=20)
        info_table.add_column("Value", style="green", width=15)
        info_table.add_column("Recommendation", style="yellow")
        
        info_table.add_row("Available RAM", f"{ram_gb:.1f} GB", "Good" if ram_gb >= 8 else "Consider upgrading")
        info_table.add_row("Available VRAM", f"{vram_gb:.1f} GB" if vram_gb > 0 else "No GPU", "Good" if vram_gb >= 4 else "CPU mode recommended")
        info_table.add_row("Memory Tier", memory_tier.title(), f"Suitable for {memory_tier} models")
        
        # Add model recommendations
        from src.config.model_recommendations import recommend_model
        recommended = recommend_model(ram_gb, vram_gb)
        if recommended:
            info_table.add_row("Recommended Model", recommended.model_id.split("/")[-1], recommended.description[:50])
        
        self.console.print(info_table)
        Prompt.ask("Press Enter to continue")
    
    def show_configuration(self):
        """Show configuration options."""
        self.console.clear()
        
        config_text = Text.assemble(
            ("⚙️  Configuration Options\n\n", "bold cyan"),
            ("Current configuration files:\n", "white"),
            ("• config/model_config.json - Model settings\n", "green"),
            ("• Default models in database\n", "green"),
            ("\nConfiguration features:\n", "white"),
            ("• Automatic model selection\n", "yellow"),
            ("• Progressive GPU fallback\n", "yellow"),
            ("• Quantization support (8-bit, 4-bit)\n", "yellow"),
            ("• Custom device mapping\n", "yellow"),
        )
        
        panel = Panel(config_text, title="Configuration", style="blue")
        self.console.print(panel)
        Prompt.ask("Press Enter to continue")
    
    def start_chat(self):
        """Start the chat interface."""
        if not self.llm:
            self.console.print("⚠️  No model loaded. Please select a model first.", style="bold yellow")
            Prompt.ask("Press Enter to continue")
            return
        
        self.console.clear()
        self.console.print("🚀 Starting chat session... Type 'exit' to return to menu", style="bold green")
        self.console.print()
        
        # Use the existing ChatSession but customize it
        try:
            if not self.chat_session:
                self.chat_session = ChatSession(console=self.console, llm=self.llm, model_id=self.current_model_id)
            
            self.chat_session.run()
            
        except KeyboardInterrupt:
            self.console.print("\n🔙 Returning to main menu...", style="bold yellow")


def run_tui():
    """Run the Lyra TUI."""
    tui = LyraTUI()
    tui.show_main_menu()