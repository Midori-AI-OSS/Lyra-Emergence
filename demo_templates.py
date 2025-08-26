#!/usr/bin/env python3
"""Demo script to showcase automatic chat template functionality."""

import sys
from pathlib import Path

# Add the src directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.chat_templates import create_template_manager


def demo_auto_templates():
    """Demonstrate auto template functionality with different models."""
    print("🎭 Auto Chat Template Demo\n")
    print(
        "This demo shows how Lyra automatically selects the best chat template for each model.\n"
    )

    # Show a few example models from our database
    demo_models = [
        "Qwen/Qwen2.5-7B-Instruct",
        "meta-llama/Llama-3.2-3B-Instruct",
        "microsoft/Phi-3.5-mini-instruct",
        "google/gemma-2-9b-it",
    ]

    test_conversation = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Hello! Can you explain what you are?"},
        {
            "role": "assistant",
            "content": "I'm an AI assistant designed to help you with various tasks and questions.",
        },
        {"role": "user", "content": "That's great! What can you help me with?"},
    ]

    for model_id in demo_models:
        print(f"🤖 Model: {model_id}")
        print("=" * 60)

        try:
            # Create template manager for this model
            manager = create_template_manager(model_id)

            # Show template info
            info = manager.get_template_info()
            print(f"✓ Tokenizer loaded: {info['tokenizer_loaded']}")
            print(f"✓ Has chat template: {info['has_chat_template']}")

            if info["has_chat_template"]:
                print("✓ Using automatic model-specific chat template")
            else:
                print(
                    "⚠ Using fallback template (model doesn't have built-in template)"
                )

            # Format the conversation
            formatted = manager.format_conversation(
                test_conversation, add_generation_prompt=True
            )

            print(f"\n📝 Formatted conversation for {model_id}:")
            print("-" * 40)
            print(formatted)
            print("-" * 40)

        except Exception as e:
            print(f"❌ Error with {model_id}: {e}")
            print("⚠ This is expected in demo mode without actual model files")

        print("\n")

    print("🎉 Demo complete!")
    print("\nKey benefits of auto chat templates:")
    print("• Each model uses its optimal conversation format")
    print("• No manual template configuration needed")
    print("• Better response quality from properly formatted inputs")
    print("• Automatic fallback for models without templates")
    print("• Seamless integration with existing chat functionality")


if __name__ == "__main__":
    demo_auto_templates()
