import aiosqlite
from leaderboards.leaderboards_constants import LEADERBOARD_DATABASE_PATH, LEADERBOARD_NAMES

async def get_user_points (user_id: int, leaderboard_code: str) -> int:
    """Returns the current user points from a specific leaderboard"""
    table_name = LEADERBOARD_NAMES[leaderboard_code]
    async with aiosqlite.connect(LEADERBOARD_DATABASE_PATH) as db:
        async with db.execute(
            "SELECT pts FROM leaderboards WHERE user_id = ? AND leaderboard_name = ?",
            (str(user_id), table_name)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def set_user_points(user_id: int, leaderboard_code: str, points: int) -> None:
    """Defines the exact points a user has"""
    table_name = LEADERBOARD_NAMES[leaderboard_code]
    async with aiosqlite.connect(LEADERBOARD_DATABASE_PATH) as db:
        await db.execute(
            """
            INSERT INTO leaderboards (user_id, leaderboard_name, pts)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, leaderboard_name)
            DO UPDATE SET pts = excluded.pts
            """,
            (str(user_id), table_name, points)
        )
        await db.commit()

async def update_user_points(user_id: int, leaderboard_code: str, points_to_add: int) -> int:
    """
    Adds (or removes, if negative) points to user
    Returns the total updated value
    """
    current_pts = await get_user_points(user_id, leaderboard_code)
    new_pts = max(0, current_pts + points_to_add)

    await set_user_points(user_id, leaderboard_code, new_pts)
    return new_pts