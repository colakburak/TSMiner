from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

class Item(BaseModel):
    id: int = Field(None, description="The unique identifier of the item")
    name: str = Field(..., description="Name of the item")
    price: float = Field(..., description="The price of the item")
    target_url: HttpUrl = Field(None, description="URL related to the item")
    description: Optional[str] = Field(None, description="A brief description of the item")


    class Config:
        schema_extra = {
            "example": {
                "id": 123,
                "name": "Sample Item",
                "description": "This is a sample item for demonstration purposes",
                "price": 9.99,
                "target_url": "https://example.com/item/123"
            }
        }

class SettingsModel(BaseModel):
    frequency_seconds: int = Field(None, description="Scheduling frequency in seconds")
    max_runtime: Optional[int] = Field(None, description="Maximum runtime of the mining process in minutes")

    class Config:
        schema_extra = {
            "example": {
                "frequency_seconds": None,
                "max_runtime": 120,
            }
        }

class ResponseModel(BaseModel):
    success: bool = Field(default=True, description="Indicates if the request was successful or not.")
    message: str = Field(default="Operation completed successfully", description="A message providing more details about the response.")
    data: dict = Field(default={}, description="Any data returned by the API.")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"key": "value"}
            }
        }
