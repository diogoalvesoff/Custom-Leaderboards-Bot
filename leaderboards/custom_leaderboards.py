import os
import math
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import aiosqlite
import asyncio

from shared.hardcore_globals import GUILD_INFO, ROLE_IDS, CHANNEL_IDS
from leaderboards.leaderboards_constants import (
    COOLDOWN, DELAY_BEFORE_DELETING_MESSAGE,
    LEADERBOARD_DATABASE_PATH,
    ROLES_WITH_PERMS_TO__TALK_IN_BATTLE_CHANNEL
)
from leaderboards.cogs.battle import ChallengeView, CloseThreadView
from leaderboards.cogs.leaderboard import LeaderboardView

load_dotenv()
TOKEN = os.getenv('TOKEN')

async def setup_db():
    async with aiosqlite.connect(LEADERBOARD_DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS leaderboards (
                user_id TEXT,
                leaderboard_name TEXT,
                pts INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, leaderboard_name)
            )
        """)
        await db.commit()

class Client (commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True                                    # lets see reactions
        intents.guilds = True                                       # lets see specific guild info
        intents.members = True                                      # lets assign roles to users~
        super().__init__(command_prefix="!", intents=intents)
        self.cooldown = commands.CooldownMapping.from_cooldown(1, COOLDOWN, commands.BucketType.user)

    async def setup_hook(self) -> None:
        self.add_view(ChallengeView())
        self.add_view(CloseThreadView())
        self.add_view(LeaderboardView())
        await setup_db()
        await self.load_extension("leaderboards.cogs.battle")
        await self.load_extension("leaderboards.cogs.leaderboard")
        await self.load_extension("leaderboards.cogs.pts")
        
    async def on_ready(self):
        print(f'Logged on as {self.user}')
        try:
            synced = await self.tree.sync(guild=GUILD_INFO["GUILD"])
            print (f'Synced {len(synced)} commands to guild {GUILD_INFO["GUILD_ID"]}')
        except Exception as e:
            print (f'Error syncing commands: {e}')

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        bucket = self.cooldown.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            print(f"Rate limit catch. {message.author.name} gotta wait more {retry_after:.2f}s")
            return
        
        await self.process_commands(message)

        battle_channel = CHANNEL_IDS.get("BATTLE_CHANNEL")
        if not battle_channel:
            print("[BOT] - Err: Battle channel not found")
        elif message.channel.id == battle_channel:
            have_permission = any(role.id in ROLES_WITH_PERMS_TO__TALK_IN_BATTLE_CHANNEL for role in message.author.roles)
            if not have_permission:
                try:
                    await message.delete()
                    await message.channel.send(f"⚠️ {message.author.mention}, This channel is fight only. Use /battle to fight others warriors", delete_after=DELAY_BEFORE_DELETING_MESSAGE)
                except discord.Forbidden:
                    print("[BOT] - E: I don't have perms to delete messages")
                except Exception as e:
                    print(f"[BOT] - E: Something wrong happened: {e}")

        # content = message.content

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        print(f"E: '{ctx.command} failed: {error}")

client = Client()

@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingAnyRole):
        await interaction.response.send_message("You don't have perms to execute me", ephemeral=True)
        return
    print(f"E: '{interaction.command.name}' failed: {error}")
    if not interaction.response.is_done():
        await interaction.response.send_message(f"I think smth went wrong... role <@&{ROLE_IDS.get('ADMIN_ROLE_ID')}>")


"""
#################################################################################################################################
#                                                               COMMANDS                                                        #
#################################################################################################################################

1. /battle [title] [description]
2. /leaderboard print [leaderboard]
3. /leaderboard set [leaderboard] [user]
3. /pts see [user]
4. /pts add [user] [leaderboard] [points]
5. /pts rem [user] [leaderboard] [points]
6. /pts set [user] [leaderboard] [points]
"""


"""
#################################################################################################################################
#                                                               MAIN                                                            #
#################################################################################################################################
"""


def main():
    if not TOKEN:
        print ("E: Token not found!")
        return
    print ("Starting!")
    client.run(TOKEN)

if __name__ == "__main__":
    main()