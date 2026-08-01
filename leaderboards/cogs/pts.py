import discord
from discord import app_commands
from discord.ext import commands

from shared.hardcore_globals import GUILD_INFO, CHANNEL_IDS
from leaderboards.leaderboards_constants import (
    SHARED_LEADERBOARD_CHOICES,
    ROLES_WITH_PERMS_TO_USE__PTS_ADD, ROLES_WITH_PERMS_TO_USE__PTS_REM, ROLES_WITH_PERMS_TO_USE__PTS_SET
)
from leaderboards import db_handler

class PtsCog(commands.GroupCog, group_name="pts", group_description="Administrate user points"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="see", description="See current points from a user")
    async def pts_see (self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        await interaction.response.defer()

        response_lines = [f"**{target.display_name} points:**"]
        for choice in SHARED_LEADERBOARD_CHOICES:
            pts = await db_handler.get_user_points(target.id, choice.value)
            response_lines.append(f"{choice.name}: {pts}")

        await interaction.followup.send("\n".join(response_lines))

    
    @app_commands.checks.has_any_role(*ROLES_WITH_PERMS_TO_USE__PTS_ADD)
    @app_commands.command(name="add", description="Adds points to an user")
    @app_commands.choices(leaderboard=SHARED_LEADERBOARD_CHOICES)
    async def pts_add (self, interaction: discord.Interaction, user: discord.Member, leaderboard: app_commands.Choice[str], points: int):
        if points <= 0:
            return await interaction.response.send_message("❌ The value to add must be higher then 0 ❌", ephemeral=True)
        
        new_total = await db_handler.update_user_points(user.id, leaderboard.value, points)
        await interaction.response.send_message(f"✅ Added **{points}** points to {user.mention} in {leaderboard.name}.✅\nCurrent Points: **{new_total}**.", ephemeral=True)
        
        bot_commands_channel = interaction.guild.get_channel(CHANNEL_IDS["BOT_COMMANDS_CHANNEL"])
        if not bot_commands_channel:
            print ("I could not find Bot Commands Channel")
            return
        await bot_commands_channel.send(f"✅ Added **{points}** points to {user.mention} in {leaderboard.name}.✅\nCurrent Points: **{new_total}**.")

    
    @app_commands.checks.has_any_role(*ROLES_WITH_PERMS_TO_USE__PTS_REM)
    @app_commands.command(name="rem", description="Removes points from an user")
    @app_commands.choices(leaderboard=SHARED_LEADERBOARD_CHOICES)
    async def pts_rem(self, interaction: discord.Interaction, user: discord.Member, leaderboard: app_commands.Choice[str], points: int):
        if points <= 0:
            return await interaction.response.send_message("❌ The value to remove must be higher then 0 ❌", ephemeral=True)
            
        new_total = await db_handler.update_user_points(user.id, leaderboard.value, -points)
        await interaction.response.send_message(f"✅ Removed **{points}** points from {user.display_name} in {leaderboard.name}.✅\nCurrent Points: **{new_total}**.", ephemeral=True)

        bot_commands_channel = interaction.guild.get_channel(CHANNEL_IDS["BOT_COMMANDS_CHANNEL"])
        if not bot_commands_channel:
            print ("I could not find Bot Commands Channel")
            return
        await bot_commands_channel.send(f"✅ Removed **{points}** points from {user.display_name} in {leaderboard.name}.✅\nCurrent Points: **{new_total}**.")


    @app_commands.checks.has_any_role(*ROLES_WITH_PERMS_TO_USE__PTS_SET)
    @app_commands.command(name="set", description="Sets the exact points to an user")
    @app_commands.choices(leaderboard=SHARED_LEADERBOARD_CHOICES)
    async def pts_set(self, interaction: discord.Interaction, user: discord.Member, leaderboard: app_commands.Choice[str], points: int):
        if points < 0:
            return await interaction.response.send_message("❌ Points can't be negative ❌", ephemeral=True)
            
        await db_handler.set_user_points(user.id, leaderboard.value, points)
        await interaction.response.send_message(f"🎯 Points from {user.mention} in {leaderboard.name} got set to **{points}**.", ephemeral=True)

        bot_commands_channel = interaction.guild.get_channel(CHANNEL_IDS["BOT_COMMANDS_CHANNEL"])
        if not bot_commands_channel:
            print ("I could not find Bot Commands Channel")
            return
        await bot_commands_channel.send(f"🎯 Points from {user.mention} in {leaderboard.name} got set to **{points}**.")


async def setup(bot: commands.Bot):
    await bot.add_cog(PtsCog(bot), guild=GUILD_INFO["GUILD"])