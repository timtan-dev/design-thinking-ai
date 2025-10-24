"""
AI Service - OpenAI API Integration
Wrapper for all AI-powered generation tasks
"""

from openai import OpenAI
from config.settings import Settings
from typing import Dict, Any, Optional
import json
import base64

class AIService:
    """AI service for generating content using OpenAI API"""

    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=Settings.OPENAI_API_KEY)
        self.model = Settings.OPENAI_MODEL
        self.temperature = Settings.OPENAI_TEMPERATURE
        self.max_tokens = Settings.OPENAI_MAX_TOKENS

    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """
        Make a call to OpenAI API

        Args:
            system_prompt: System instruction
            user_prompt: User message

        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating content: {str(e)}"

    def analyze_image_with_vision(self, image_path: str, prompt: str, system_context: Optional[str] = None) -> str:
        """
        Analyze an image using GPT-4o vision model

        Args:
            image_path: Path to the image file
            prompt: Analysis prompt/question about the image
            system_context: Optional system context for the analysis

        Returns:
            AI analysis of the image
        """
        try:
            # Read and encode image to base64
            with open(image_path, 'rb') as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            # Prepare messages
            messages = []

            # Add system context if provided
            if system_context:
                messages.append({"role": "system", "content": system_context})

            # Add user message with image
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            })

            # Call vision model
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error analyzing image: {str(e)}"

    def generate_image_with_dalle(self, prompt: str, size: str = "1024x1024", quality: str = "standard") -> Optional[str]:
        """
        Generate an image using DALL-E

        Args:
            prompt: Description of the image to generate
            size: Image size (1024x1024, 1792x1024, or 1024x1792)
            quality: Image quality (standard or hd)

        Returns:
            URL of the generated image, or None if error
        """
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )

            return response.data[0].url

        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return None


