from typing import Dict, Any, List, Optional
import json
import google.generativeai as genai
from app.config.settings import settings


class GeminiLLMConfig:
    """
    Custom LLM config for AutoGen to work with Gemini API
    """
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.gemini_model
        self.api_key = settings.gemini_api_key
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
    
    def create_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Create completion compatible with AutoGen's expected format
        """
        # Convert AutoGen messages to Gemini format
        system_prompt = ""
        user_content = ""
        
        for message in messages:
            if message.get("role") == "system":
                system_prompt = message.get("content", "")
            elif message.get("role") == "user":
                user_content = message.get("content", "")
            elif message.get("role") == "assistant":
                # For conversation history
                user_content += f"\n\nPrevious response: {message.get('content', '')}"
        
        # Combine system and user content
        full_prompt = f"""
{system_prompt}

ISTRUZIONI SPECIFICHE:
- Rispondi sempre in italiano per contenuti HSE
- Usa terminologia tecnica precisa
- Fornisci risposte strutturate e dettagliate
- Cita normative italiane quando applicabile

RICHIESTA:
{user_content}
"""
        
        try:
            # Generate response with Gemini
            generation_config = genai.types.GenerationConfig(
                temperature=kwargs.get("temperature", 0.7),
                max_output_tokens=kwargs.get("max_tokens", 2000),
            )
            
            response = self.model.generate_content(full_prompt, generation_config=generation_config)
            
            # Format response for AutoGen
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": response.text
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(full_prompt.split()),
                    "completion_tokens": len(response.text.split()),
                    "total_tokens": len(full_prompt.split()) + len(response.text.split())
                }
            }
            
        except Exception as e:
            # Return error in AutoGen format
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": f"Errore nella generazione della risposta: {str(e)}"
                        },
                        "finish_reason": "error"
                    }
                ],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }


def get_autogen_llm_config() -> Optional[Dict[str, Any]]:
    """
    Get AutoGen LLM configuration - return None to use direct Gemini calls
    Since AutoGen's LLM integration with Gemini is complex, we'll use direct API calls
    """
    if not settings.gemini_api_key:
        print("[AutoGen Config] No Gemini API key found")
        return None
    
    # For now, return None to signal that we should use direct Gemini calls
    # instead of trying to integrate with AutoGen's LLM system
    return None


def create_hse_agent_config(
    name: str,
    system_message: str,
    description: str,
    max_consecutive_auto_reply: int = 3
) -> Dict[str, Any]:
    """
    Create standardized HSE agent configuration for AutoGen
    """
    return {
        "name": name,
        "system_message": system_message,
        "description": description,
        "llm_config": get_autogen_llm_config(),
        "max_consecutive_auto_reply": max_consecutive_auto_reply,
        "human_input_mode": "NEVER",  # Fully automated
        "code_execution_config": False,  # No code execution for safety
    }