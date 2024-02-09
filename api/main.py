from typing import List, Dict

from fastapi import FastAPI, WebSocket, HTTPException, Path, Query, Request
from api.models import MiningItem, MiningOperationResponse, MiningItemManager

from influxdb_client import InfluxDBClient, Point


app = FastAPI()
item_manager = MiningItemManager()

influxdb_client = InfluxDBClient(url="http://localhost:8086", token="your-token", org="your-org")


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to Miner API"}

# ITEM operationsn
@app.post("/items/")
async def add_item(item: MiningItem):
    try:
        item_manager.add_item(item.name, item)
        return {"message": "Item added"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/items/{name}")
async def delete_item(name: str):
    try:
        item_manager.delete_item(name)
        return {"message": "Item deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/items/{name}")
async def update_item(name: str, item: MiningItem):
    try:
        item_manager.update_item(name, item)
        return {"message": "Item updated"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/items/", response_model=Dict[str, MiningItem])
async def get_all_items():
    return item_manager.get_all_items()

# Miner Opertations
@app.websocket("/ws/{miner_id}")
async def websocket_endpoint(websocket: WebSocket, miner_id: str):
    await websocket.accept()
    print(f"Miner {miner_id} connected")
    while True:
        data = await websocket.receive_text()
        print(data, miner_id)

@app.post("/start-mining/{item_name}", tags=["Mining Operations"], response_model=MiningOperationResponse)
async def start_mining(item_name: str):
    # Logic to start mining for the specified item
    try:
        # Assuming a function `start_mining_operation` which starts mining based on item_name
        # start_mining_operation(item_name)
        return MiningOperationResponse(status="Success", message=f"Mining started for {item_name}")
    except Exception as e:
        return MiningOperationResponse(status="Error", message=str(e))

@app.post("/stop-mining/{item_name}", tags=["Mining Operations"], response_model=MiningOperationResponse)
async def stop_mining(item_name: str):
    # Logic to stop mining for the specified item
    try:
        # Assuming a function `stop_mining_operation` which stops mining based on item_name
        # stop_mining_operation(item_name)
        return MiningOperationResponse(status="Success", message=f"Mining stopped for {item_name}")
    except Exception as e:
        return MiningOperationResponse(status="Error", message=str(e))

@app.get("/mining-status", tags=["Mining Operations"])
async def mining_status():
    # Logic to check the status of mining
    return {"status": "Mining is running"}

@app.get("/health", tags=["System"])
async def health_check():
    # Logic to check the health of the system
    return {"status": "System is healthy"}

@app.get("/logs", tags=["System"], response_model=List[str])
async def get_logs():
    # Logic to retrieve logs
    return ["Log data"]