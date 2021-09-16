# Imports
import aioredis
import hashlib


async def check_master_hash(name, namespace, token, cache_key):
    redis = aioredis.from_url("redis://localhost")
    master_hash = hashlib.md5(f"{token}".encode('utf-8')).hexdigest()

    result = await redis.hgetall(name=name)
    if not result:
        await set_master_hash(name, master_hash)

    result = await redis.hget(name, "master-key")
    decoded_result = result.decode("utf-8")
    if decoded_result != master_hash:
        await clear_old_keys(name, namespace)
        await clear_master_key(name, decoded_result)
        await set_master_hash(name, master_hash)
        keypair = {namespace: cache_key}
        await set_endpoint_hash(name, **keypair)


async def set_master_hash(name, masterkey):
    redis = aioredis.from_url("redis://localhost")

    await redis.hset(name, key="master-key", value=masterkey)


async def set_endpoint_hash(name, **kwargs):
    redis = aioredis.from_url("redis://localhost")

    for key, value in kwargs.items():
        await redis.hset(name, key=key, value=value)


async def clear_master_key(name, old_masterkey):
    redis = aioredis.from_url("redis://localhost")

    await redis.hdel(name, old_masterkey)


async def clear_old_keys(name, namespace):
    redis = aioredis.from_url("redis://localhost")

    master_keys = await redis.hkeys(name)
    for mkey in master_keys:
        decoded_mkey = mkey.decode("utf-8")
        if decoded_mkey == "master-key":
            continue

        old_endpoint_bytes = await redis.hget(name, decoded_mkey)
        old_endpoint_hash = old_endpoint_bytes.decode("utf-8")

        await redis.delete(f"example:{namespace}:{old_endpoint_hash}")
