from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

app = FastAPI()

# ============================
# 🚀 1. Data Models
# ============================
class Item(BaseModel):
    itemId: str
    name: str
    width: int
    depth: int
    height: int
    priority: int
    expiryDate: Optional[str]  # Format: YYYY-MM-DD
    usageLimit: Optional[int]
    preferredZone: str

class Container(BaseModel):
    containerId: str
    zone: str
    width: int
    depth: int
    height: int

class PlacementResponse(BaseModel):
    success: bool
    placements: List[dict]

# Dummy storage for testing
items_db = []
containers_db = []

# ============================
# 🚀 2. Placement API
# ============================
@app.post("/api/placement", response_model=PlacementResponse)
def place_items(items: List[Item], containers: List[Container]):
    global items_db, containers_db
    items_db.extend(items)
    containers_db.extend(containers)

    placements = []
    for item in items:
        placed = False
        for container in containers:
            if (item.width <= container.width and
                item.depth <= container.depth and
                item.height <= container.height):
                placements.append({
                    "itemId": item.itemId,
                    "containerId": container.containerId,
                    "position": {"width": 0, "depth": 0, "height": 0}  # Simplified positioning
                })
                placed = True
                break
        
        if not placed:
            raise HTTPException(status_code=400, detail=f"No space for item {item.itemId}")

    return {"success": True, "placements": placements}

# ============================
# 🚀 3. Search & Retrieval API
# ============================
@app.get("/api/search")
def search_item(itemId: Optional[str] = None, name: Optional[str] = None):
    for item in items_db:
        if itemId and item.itemId == itemId:
            return {"success": True, "item": item}
        if name and item.name.lower() == name.lower():
            return {"success": True, "item": item}
    return {"success": False, "message": "Item not found"}

@app.post("/api/retrieve")
def retrieve_item(itemId: str):
    for item in items_db:
        if item.itemId == itemId:
            item.usageLimit -= 1 if item.usageLimit else 0
            return {"success": True, "message": f"Retrieved item {itemId}"}
    return {"success": False, "message": "Item not found"}

# ============================
# 🚀 4. Waste Management API
# ============================
@app.get("/api/waste/identify")
def identify_waste():
    expired_items = []
    today = datetime.today().strftime('%Y-%m-%d')

    for item in items_db:
        if (item.expiryDate and item.expiryDate < today) or (item.usageLimit == 0):
            expired_items.append(item)

    return {"success": True, "wasteItems": expired_items}

# ============================
# 🚀 5. Time Simulation API
# ============================
@app.post("/api/simulate/day")
def simulate_time(numOfDays: int):
    today = datetime.today()
    new_date = today.replace(day=today.day + numOfDays)

    for item in items_db:
        if item.expiryDate and datetime.strptime(item.expiryDate, "%Y-%m-%d") < new_date:
            item.usageLimit = 0  # Mark as expired

    return {"success": True, "newDate": new_date.strftime('%Y-%m-%d')}

# ============================
# 🚀 6. Logging API
# ============================
logs_db = []

@app.get("/api/logs")
def get_logs():
    return {"logs": logs_db}
