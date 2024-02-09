import json

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict
from pydantic import BaseModel, HttpUrl

class MiningItem(BaseModel):
    name: str = Field(..., description="Name of the item")
    target_url: HttpUrl = Field(None, description="URL related to the item")
    frequency_seconds: int = Field(None, description="Scheduling frequency in seconds")

class MiningOperationResponse(BaseModel):
    status: str
    message: str

class MiningItemManager:
    def __init__(self, filename: str = "mining_items.json"):
        self.filename = filename
        self.mining_items = self.load_items()

    def load_items(self) -> Dict[str, MiningItem]:
        try:
            with open(self.filename, "r") as file:
                content = file.read().strip()
                if content:  # Check if the file is not empty
                    items_data = json.loads(content)
                    # Parse each item into a MiningItem instance
                    return {k: MiningItem.parse_raw(v) for k, v in items_data.items()}
                else:
                    return {}
        except FileNotFoundError:
            return {}

    def save_items(self):
        with open(self.filename, "w") as file:
            items_data = {k: v.json() for k, v in self.mining_items.items()}  # Convert to JSON
            json.dump(items_data, file)

    def add_item(self, name: str, item_data: MiningItem):
        if name in self.mining_items:
            raise ValueError("Item already exists")
        self.mining_items[name] = item_data  # Store the MiningItem instance
        self.save_items()

    def update_item(self, name: str, item_data: MiningItem):
        if name not in self.mining_items:
            raise ValueError("Item not found")
        self.mining_items[name] = item_data  # Store the MiningItem instance
        self.save_items()

    def delete_item(self, name: str):
        if name not in self.mining_items:
            raise ValueError("Item not found")
        del self.mining_items[name]  # Delete the item
        self.save_items()  # Save the updated items to the file

    def get_all_items(self):
        return self.mining_items
