import motor.motor_asyncio
import config
from datetime import datetime
#from bson.objectid import ObjectId

cluster = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URL)
db = cluster.ezxamsbot


async def add_user(user_id):
    check = await db["users"].find_one({"_id": user_id})
    if check:
        return
    payload = {
        "_id": user_id,
        "created_at": datetime.utcnow(),
        "balance": 0,
        "tables": []
    }
    db["users"].insert_one(payload)


async def check_balance(user_id):
    user = await db["users"].find_one({"_id": user_id})
    return user["balance"] < 1000000


async def get_balance(user_id):
    user = await db["users"].find_one({"_id": user_id})
    return user["balance"]


async def update_balance(user_id, tokens_cnt):
    user = await db["users"].find_one({"_id": user_id})
    new_balance = user["balance"] + tokens_cnt
    db["users"].update_one(
            filter={"_id": user_id},
            update={
                "$set": {
                    "balance": new_balance
                }
            },
        )