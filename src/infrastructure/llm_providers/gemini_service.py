"""
Servicio de IA con Google Gemini.
Lee GEMINI_API_KEY de .env y genera respuestas usando el contexto y los productos.
"""

import os
import asyncio
from typing import Iterable, Union
from dotenv import load_dotenv
import google.generativeai as genai
from src.domain.entities import Product, ChatContext

load_dotenv()


class GeminiService:
    def __init__(self, model_name: str | None = None) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY no configurada.")
        genai.configure(api_key=api_key)

        # Default moderno (alineado a la guía)
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        # Instancia del modelo
        self.model = genai.GenerativeModel(self.model_name)

    def format_products_info(self, products: Iterable[Product]) -> str:
        lines = [
            f"- {p.name} | {p.brand} | ${p.price:.2f} | Stock: {p.stock} | Talla: {p.size} | Color: {p.color}"
            for p in products
        ]
        return "\n".join(lines) if lines else "- (sin productos)"

    def _build_prompt(
        self,
        user_message: str,
        products: Iterable[Product],
        context: Union[ChatContext, str],
    ) -> str:
        """
        Acepta `context` como ChatContext o como string ya formateado.
        """
        history = context.format_for_prompt() if isinstance(context, ChatContext) else (context or "")
        products_txt = self.format_products_info(products)

        return (
            "Eres un asistente virtual experto en ventas de zapatos para un e-commerce.\n"
            "Tu objetivo es ayudar a los clientes a encontrar los zapatos perfectos.\n\n"
            f"PRODUCTOS DISPONIBLES:\n{products_txt}\n\n"
            "INSTRUCCIONES:\n"
            "- Sé amigable y profesional\n"
            "- Usa el contexto de la conversación anterior\n"
            "- Recomienda productos específicos cuando sea apropiado\n"
            "- Menciona precios, tallas y disponibilidad\n"
            "- Si no tienes información, sé honesto\n\n"
            f"{history}\n\n"
            f"Usuario: {user_message}\n\nAsistente:"
        )

    async def generate_response(
        self,
        user_message: str,
        products: Iterable[Product],
        context: Union[ChatContext, str],
    ) -> str:
        """
        Genera la respuesta usando el modelo; `context` puede ser ChatContext o str.
        """
        prompt = self._build_prompt(user_message, products, context)

        def _call():
            try:
                resp = self.model.generate_content(prompt)
                text = getattr(resp, "text", "")
                return text.strip() if isinstance(text, str) and text.strip() else "No pude generar una respuesta en este momento."
            except Exception as e:
                # Fallback rápido a un modelo muy compatible si el actual no está habilitado/permitido
                if "not found" in str(e).lower() or "unsupported" in str(e).lower():
                    fallback = "gemini-1.5-flash"
                    self.model = genai.GenerativeModel(fallback)
                    resp2 = self.model.generate_content(prompt)
                    text2 = getattr(resp2, "text", "")
                    return text2.strip() if isinstance(text2, str) and text2.strip() else "No pude generar una respuesta en este momento."
                raise

        return await asyncio.to_thread(_call)

