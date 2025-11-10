"""
AI Service - Multi-Provider AI Integration
Wrapper for all AI-powered generation tasks using LangChain
Supports: OpenAI (GPT-4.1, GPT-5), Anthropic (Claude), xAI (Grok)
"""

from openai import OpenAI
from config.settings import Settings
from typing import Dict, Any, Optional, Union, Tuple
from datetime import datetime
import json
import base64
import time
from config.model_pricing import calculate_cost

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel

class AIService:
    """AI service for generating content using multiple AI providers via LangChain"""

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """
        Initialize AI service with LangChain multi-provider support

        Args:
            model: Optional model override. If not provided, uses Settings.OPENAI_MODEL
            temperature: Optional temperature override (0.0-1.0). Controls randomness.
            top_p: Optional top_p override (0.0-1.0). Controls diversity via nucleus sampling.
            max_tokens: Optional max_tokens override. Maximum tokens to generate.
        """
        self.model = model if model else Settings.OPENAI_MODEL
        self.temperature = temperature if temperature is not None else Settings.OPENAI_TEMPERATURE
        self.top_p = top_p  # Will be None if not provided
        self.max_tokens = max_tokens if max_tokens is not None else Settings.OPENAI_MAX_TOKENS

        # Initialize the appropriate LangChain chat model based on model name
        self.llm = self._initialize_llm()

        # Keep OpenAI client for image generation (DALL-E)
        self.client = OpenAI(api_key=Settings.OPENAI_API_KEY)

    def _initialize_llm(self) -> BaseChatModel:
        """
        Initialize the appropriate LangChain chat model based on model name

        Model-specific parameter handling:
        - GPT-5: No temperature/top_p (only max_tokens)
        - Claude: Only temperature (no top_p)
        - GPT-4.1: temperature + top_p
        - Grok-4: temperature + top_p

        Returns:
            LangChain chat model instance
        """
        # GPT-5 - No parameters except max_tokens
        if self.model == 'gpt-5':
            return ChatOpenAI(
                model=self.model,
                api_key=Settings.OPENAI_API_KEY,
                max_tokens=self.max_tokens
            )

        # Anthropic models (Claude) - Only temperature, no top_p
        elif self.model.startswith('claude'):
            if not Settings.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not set in environment variables")
            return ChatAnthropic(
                model=self.model,
                api_key=Settings.ANTHROPIC_API_KEY,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

        # xAI models (Grok) - temperature + top_p
        elif self.model.startswith('grok'):
            if not Settings.XAI_API_KEY:
                raise ValueError("XAI_API_KEY not set in environment variables")

            kwargs = {
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }
            if self.top_p is not None:
                kwargs["top_p"] = self.top_p

            return ChatOpenAI(
                model=self.model,
                api_key=Settings.XAI_API_KEY,
                base_url="https://api.x.ai/v1",
                **kwargs
            )

        # OpenAI models (GPT-4.1, etc.) - temperature + top_p
        elif self.model.startswith('gpt'):
            kwargs = {
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }
            if self.top_p is not None:
                kwargs["top_p"] = self.top_p

            return ChatOpenAI(
                model=self.model,
                api_key=Settings.OPENAI_API_KEY,
                **kwargs
            )

        else:
            # Default to OpenAI with full parameters
            kwargs = {
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }
            if self.top_p is not None:
                kwargs["top_p"] = self.top_p

            return ChatOpenAI(
                model=self.model,
                api_key=Settings.OPENAI_API_KEY,
                **kwargs
            )

    def _call_openai(self, system_prompt: str, user_prompt: str) -> Tuple[str, Dict[str, Any]]:
        """
        Make a call to AI provider via LangChain

        LangChain automatically handles:
        - Model-specific parameter requirements (GPT-5: no params, Claude: no top_p)
        - Provider-specific API formats
        - System message compatibility

        Args:
            system_prompt: System instruction
            user_prompt: User message

        Returns:
            Tuple of (response_content, usage_metadata) where usage_metadata contains:
            - duration_seconds: Time taken for the API call
            - input_tokens: Number of input/prompt tokens
            - output_tokens: Number of output/completion tokens
            - cost_usd: Calculated cost in USD
            - model: Model used for the generation
        """
        try:
            # Start timing
            start_time = time.time()

            # Create messages using LangChain message types
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            # LangChain automatically handles model-specific requirements:
            # - GPT-5: no temperature/top_p parameters
            # - Claude: uses Anthropic API format, no top_p
            # - Grok: uses xAI API format
            response = self.llm.invoke(messages)

            # Calculate duration
            duration_seconds = time.time() - start_time

            # Extract token usage from response
            # LangChain stores usage info in response_metadata
            input_tokens = 0
            output_tokens = 0

            if hasattr(response, 'response_metadata') and response.response_metadata:
                metadata = response.response_metadata

                # OpenAI format
                if 'token_usage' in metadata:
                    usage = metadata['token_usage']
                    input_tokens = usage.get('prompt_tokens', 0)
                    output_tokens = usage.get('completion_tokens', 0)

                # Anthropic format
                elif 'usage' in metadata:
                    usage = metadata['usage']
                    input_tokens = usage.get('input_tokens', 0)
                    output_tokens = usage.get('output_tokens', 0)

            # Calculate cost
            cost_usd = calculate_cost(self.model, input_tokens, output_tokens)

            # Build usage metadata
            usage_metadata = {
                'duration_seconds': duration_seconds,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'cost_usd': cost_usd,
                'model': self.model
            }

            return response.content, usage_metadata

        except Exception as e:
            # Return error with empty metadata
            error_metadata = {
                'duration_seconds': 0.0,
                'input_tokens': 0,
                'output_tokens': 0,
                'cost_usd': 0.0,
                'model': self.model
            }
            return f"Error generating content: {str(e)}", error_metadata

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
                model="gpt-4.1",
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

    def generate_image_with_gpt4o(self, prompt: str, reference_image_path: Optional[str] = None) -> tuple[Optional[str], Optional[str]]:
        """
        Generate an image using GPT-4o image generation (gpt-image-1) with DALL-E 3 fallback
        For refinements, analyzes the reference image first to enhance prompt

        Args:
            prompt: Description of the image to generate or refinement instructions
            reference_image_path: Optional path to reference image for refinement

        Returns:
            Tuple of (image_path, error_message). If successful, error_message is None.
            If failed, image_path is None and error_message contains the error.
        """
        from pathlib import Path
        import requests

        # If there's a reference image, use GPT-4o vision to analyze it first
        enhanced_prompt = prompt
        if reference_image_path:
            try:
                # Use vision to understand the previous mockup
                analysis_prompt = f"""Analyze this mockup image in detail. Describe the layout, visual style, colors, typography, and key UI elements.

Based on your analysis, suggest how to generate a refined version with these changes:
{prompt}

Maintain all other aspects of the design including layout structure, visual style, and elements not mentioned in the changes."""

                analysis = self.analyze_image_with_vision(
                    image_path=reference_image_path,
                    prompt=analysis_prompt
                )

                # Use the analysis to create a more detailed generation prompt
                enhanced_prompt = f"{prompt}\n\nPrevious design context: {analysis[:1500]}"
            except Exception as e:
                print(f"Warning: Could not analyze reference image: {str(e)}")
                # Continue with original prompt if analysis fails

        # Use DALL-E 3 for image generation with base64 response (avoids network download issues)
        try:
            print("Generating image with DALL-E 3...")
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt[:4000],  # DALL-E 3 has a 4000 char limit
                size="1024x1024",
                quality="standard",
                n=1,
                response_format="b64_json"  # Get base64 directly instead of URL
            )

            # Get base64 image data directly (no network download needed)
            image_b64 = response.data[0].b64_json
            image_bytes = base64.b64decode(image_b64)

            # Save to temporary file
            temp_dir = Path("uploads/mockups/temp")
            temp_dir.mkdir(parents=True, exist_ok=True)

            temp_file = temp_dir / f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            with open(temp_file, 'wb') as f:
                f.write(image_bytes)

            print(f"✅ Successfully generated image (received as base64)")
            return str(temp_file), None

        except Exception as dalle_error:
            dalle_error_msg = str(dalle_error)
            print(f"❌ DALL-E 3 failed: {dalle_error_msg}")
            import traceback
            traceback.print_exc()

            # Return detailed error message
            return None, f"Image generation failed: {dalle_error_msg}"


