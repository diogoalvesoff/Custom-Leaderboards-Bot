import os
import asyncpg
import socket
import ssl
from dotenv import load_dotenv

from leaderboards.leaderboards_constants import LEADERBOARD_DATABASE_PATH, LEADERBOARD_NAMES

load_dotenv()
DB_URL = os.getenv("SUPABASE_DB_URL")
pool = None

async def create_pool():
    """Creates a Supabase conection pool. Needs to be called on_ready or setup_hook"""
    global pool
    
    domain = "aws-0-ca-central-1.pooler.supabase.com"
    ipv4_ip = socket.gethostbyname(domain)
    ipv4_url = DB_URL.replace(domain, ipv4_ip)

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    pool = await asyncpg.create_pool(ipv4_url, ssl=ctx)


async def setup_db_tables():
    query = """
        CREATE TABLE IF NOT EXISTS leaderboards (
            user_id TEXT,
            leaderboard_name TEXT,
            pts INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, leaderboard_name)
        )
    """
    async with pool.acquire() as conn:
        await conn.execute(query)


async def get_user_points (user_id: int, leaderboard_code: str) -> int:
    """Returns the current user points from a specific leaderboard"""
    table_name = LEADERBOARD_NAMES[leaderboard_code]
    query = "SELECT pts FROM leaderboards WHERE user_id = $1 AND leaderboard_name = $2"
    async with pool.acquire() as conn:
        record = await conn.fetchrow(query, str(user_id), table_name)
        return record['pts'] if record else 0


async def set_user_points(user_id: int, leaderboard_code: str, points: int) -> None:
    """Defines the exact points a user has"""
    table_name = LEADERBOARD_NAMES[leaderboard_code]
    query = """
        INSERT INTO leaderboards (user_id, leaderboard_name, pts)
        VALUES($1, $2, $3)
        ON CONFLICT (user_id, leaderboard_name)
        DO UPDATE SET pts = EXCLUDED.pts
    """
    async with pool.acquire() as conn:
        await conn.execute(query, str(user_id), table_name, points)


async def update_user_points(user_id: int, leaderboard_code: str, points_to_add: int) -> int:
    """
    Adds (or removes, if negative) points to user
    Returns the total updated value
    """
    current_pts = await get_user_points(user_id, leaderboard_code)
    new_pts = max(0, current_pts + points_to_add)

    await set_user_points(user_id, leaderboard_code, new_pts)
    return new_pts


async def get_leaderboard_count(leaderboard_code: str) -> int:
    table_name = LEADERBOARD_NAMES.get(leaderboard_code)
    query = "SELECT COUNT(*) FROM leaderboards WHERE leaderboard_name = $1"
    async with pool.acquire() as conn:
        record = await conn.fetchrow(query, table_name)
        return record['count'] if record else 0


async def get_leaderboard_page(leaderboard_code: str, offset: int, limit: int = 10) -> list:
    table_name = LEADERBOARD_NAMES.get(leaderboard_code)
    query="""
        SELECT user_id, pts
        FROM leaderboards
        WHERE leaderboard_name = $1
        ORDER BY pts DESC
        LIMIT $2 OFFSET $3
    """
    async with pool.acquire() as conn:
        records = await conn.fetch(query, table_name, limit, offset)
        return [(row['user_id'], row['pts']) for row in records]