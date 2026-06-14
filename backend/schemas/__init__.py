# Makes `backend/schemas/` a package and re-exports schemas for easy importing,
# e.g. `from app.schemas import CustomerCreate, CustomerRead`.

from backend.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from backend.schemas.product import ProductCreate, ProductRead, ProductUpdate
from backend.schemas.order import OrderCreate, OrderRead, OrderUpdate
from backend.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionRead,
    SubscriptionUpdate,
)
from backend.schemas.search import SearchHit, SearchResponse
from backend.schemas.chat import ChatMessage, ChatRequest, ChatResponse

__all__ = [
    "CustomerCreate", "CustomerRead", "CustomerUpdate",
    "ProductCreate", "ProductRead", "ProductUpdate",
    "OrderCreate", "OrderRead", "OrderUpdate",
    "SubscriptionCreate", "SubscriptionRead", "SubscriptionUpdate",
    "SearchHit", "SearchResponse",
    "ChatMessage", "ChatRequest", "ChatResponse",
]
