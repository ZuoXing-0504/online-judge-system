from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
    error_code: str = ""


class MessageResponse(BaseModel):
    message: str


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
