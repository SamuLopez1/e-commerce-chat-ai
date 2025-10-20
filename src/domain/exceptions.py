"""
Excepciones específicas del dominio.
Representan errores de negocio, no errores técnicos.
"""

class ProductNotFoundError(Exception):
    """Se lanza cuando se busca un producto que no existe."""
    def __init__(self, product_id: int | None = None):
        msg = f"Producto con ID {product_id} no encontrado" if product_id is not None else "Producto no encontrado"
        super().__init__(msg)

class InvalidProductDataError(Exception):
    """Se lanza cuando los datos de un producto son inválidos."""
    def __init__(self, message: str = "Datos de producto inválidos"):
        super().__init__(message)

class ChatServiceError(Exception):
    """Se lanza cuando hay un error en el servicio de chat."""
    def __init__(self, message: str = "Error en el servicio de chat"):
        super().__init__(message)