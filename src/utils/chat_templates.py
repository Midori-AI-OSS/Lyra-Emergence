"""Automatic chat template management for HuggingFace models."""

import logging
from typing import Dict, List, Optional, Union, Any
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)


class AutoChatTemplateManager:
    """Manages automatic chat template selection and application for HuggingFace models."""
    
    def __init__(self, model_id: str):
        """Initialize the template manager for a specific model.
        
        Args:
            model_id: HuggingFace model identifier
        """
        self.model_id = model_id
        self.tokenizer: Optional[AutoTokenizer] = None
        self._load_tokenizer()
    
    def _load_tokenizer(self) -> None:
        """Load the tokenizer for the model to access its chat template."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                trust_remote_code=True,
                use_fast=True
            )
            
            # Check if the model has a chat template
            if hasattr(self.tokenizer, 'chat_template') and self.tokenizer.chat_template:
                logger.info(f"Loaded chat template for {self.model_id}")
            else:
                logger.warning(f"Model {self.model_id} does not have a built-in chat template, using default format")
                
        except Exception as e:
            logger.error(f"Failed to load tokenizer for {self.model_id}: {e}")
            self.tokenizer = None
    
    def format_conversation(
        self, 
        messages: List[Dict[str, str]], 
        add_generation_prompt: bool = True
    ) -> str:
        """Format a conversation using the model's native chat template.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            add_generation_prompt: Whether to add a generation prompt for the assistant
            
        Returns:
            Formatted conversation string ready for the model
        """
        if not self.tokenizer:
            # Fallback to basic format if tokenizer failed to load
            return self._fallback_format(messages, add_generation_prompt)
        
        try:
            # Use HuggingFace's automatic chat template application
            formatted = self.tokenizer.apply_chat_template(
                conversation=messages,
                add_generation_prompt=add_generation_prompt,
                tokenize=False,  # Return string, not tokens
                return_tensors=None
            )
            
            logger.debug(f"Applied chat template for {self.model_id}")
            return formatted
            
        except Exception as e:
            logger.warning(f"Failed to apply chat template for {self.model_id}: {e}. Using fallback.")
            return self._fallback_format(messages, add_generation_prompt)
    
    def _fallback_format(self, messages: List[Dict[str, str]], add_generation_prompt: bool) -> str:
        """Fallback formatting for models without chat templates.
        
        Args:
            messages: List of message dictionaries
            add_generation_prompt: Whether to add generation prompt
            
        Returns:
            Simple formatted conversation
        """
        formatted_parts = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                formatted_parts.append(f"System: {content}")
            elif role == 'user':
                formatted_parts.append(f"Human: {content}")
            elif role == 'assistant':
                formatted_parts.append(f"Assistant: {content}")
        
        conversation = "\n\n".join(formatted_parts)
        
        if add_generation_prompt:
            conversation += "\n\nAssistant:"
        
        return conversation
    
    def format_single_message(self, message: str, role: str = "user") -> str:
        """Format a single message using the chat template.
        
        Args:
            message: The message content
            role: The role ('user', 'assistant', 'system')
            
        Returns:
            Formatted message ready for the model
        """
        messages = [{"role": role, "content": message}]
        return self.format_conversation(messages, add_generation_prompt=True)
    
    def has_chat_template(self) -> bool:
        """Check if the model has a native chat template.
        
        Returns:
            True if the model has a chat template, False otherwise
        """
        return (
            self.tokenizer is not None 
            and hasattr(self.tokenizer, 'chat_template') 
            and self.tokenizer.chat_template is not None
        )
    
    def get_template_info(self) -> Dict[str, Any]:
        """Get information about the loaded chat template.
        
        Returns:
            Dictionary with template information
        """
        info = {
            "model_id": self.model_id,
            "tokenizer_loaded": self.tokenizer is not None,
            "has_chat_template": self.has_chat_template(),
            "chat_template": None
        }
        
        if self.tokenizer and hasattr(self.tokenizer, 'chat_template'):
            info["chat_template"] = self.tokenizer.chat_template
        
        return info


def create_template_manager(model_id: str) -> AutoChatTemplateManager:
    """Factory function to create a chat template manager.
    
    Args:
        model_id: HuggingFace model identifier
        
    Returns:
        AutoChatTemplateManager instance
    """
    return AutoChatTemplateManager(model_id)


def get_supported_models_with_templates() -> Dict[str, bool]:
    """Get a mapping of models to their chat template support.
    
    Returns:
        Dictionary mapping model IDs to whether they have chat templates
    """
    from src.config.model_recommendations import MODEL_DATABASE
    
    supported = {}
    for model_info in MODEL_DATABASE:
        try:
            manager = create_template_manager(model_info.model_id)
            supported[model_info.model_id] = manager.has_chat_template()
        except Exception as e:
            logger.warning(f"Could not check template support for {model_info.model_id}: {e}")
            supported[model_info.model_id] = False
    
    return supported