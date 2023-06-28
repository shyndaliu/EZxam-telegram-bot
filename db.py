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
        "prev_request": "Hey, Cal, nice to meet you!",
        "prev_response": "Nice to meet you too! What study hacks are you most interested in?",
        "tables": []
    }
    db["users"].insert_one(payload)


async def get_request_response(user_id):
    user = await db["users"].find_one({"_id": user_id})
    return user["prev_request"], user["prev_response"]

async def update_request_response(user_id, new_request, new_response):
    db["users"].update_one(
            filter={"_id": user_id},
            update={
                "$set": {
                    "prev_request": new_request,
                    "prev_response": new_response
                }
            },
        )


async def get_tables(user_id):
    user = await db["users"].find_one({"_id": user_id})
    return user["tables"]


async def check_balance(user_id):
    user = await db["users"].find_one({"_id": user_id})
    return user["balance"] < 50000


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

async def create_table(user_id, topics, free_time):
    payload = {
        "user": user_id,
        "topics": topics,
        "calendar": free_time,
        "table": {}
    }
    data = await db["tables"].insert_one(payload)
    db["users"].update_one(
            filter={"_id": user_id},
            update={
                "$push": {
                    "tables": str(data.inserted_id)
                }
            },
        )