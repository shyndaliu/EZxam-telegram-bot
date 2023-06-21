import motor.motor_asyncio
import config

cluster = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URL)
collection = cluster.ezxambot