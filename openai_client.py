from typing import Optional
from openai import OpenAI

class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize the OpenAI client with your API key.
        
        Args:
            api_key (str): Your OpenAI API key
        """
        self.client = OpenAI(api_key=api_key)
        
        # Default settings
        self.default_model = model
        self.default_temperature = 0.7
        self.default_max_tokens = 1000
        
    def set_default_parameters(
        self,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> None:
        """
        Update default parameters for API calls.
        
        Args:
            model (str): The default model to use
            temperature (float): Default temperature setting
            max_tokens (int): Default maximum tokens
        """
        self.default_model = model
        self.default_temperature = temperature
        self.default_max_tokens = max_tokens
    
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a response using OpenAI's API.
        
        Args:
            prompt (str): The user's prompt
            system_prompt (str, optional): Instructions for how the AI should behave
            model (str, optional): Override default model
            temperature (float, optional): Override default temperature
            max_tokens (int, optional): Override default max tokens
            
        Returns:
            str: The generated response
        """
        # Use provided parameters or fall back to defaults
        model = model or self.default_model
        temperature = temperature or self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens
        
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add user prompt
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=max_tokens
            )
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def generate_chat_response(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a response using a full chat history.
        
        Args:
            messages (list[dict]): List of message dictionaries with 'role' and 'content'
            model (str, optional): Override default model
            temperature (float, optional): Override default temperature
            max_tokens (int, optional): Override default max tokens
            
        Returns:
            str: The generated response
        """
        model = model or self.default_model
        temperature = temperature or self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating response: {str(e)}"