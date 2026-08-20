import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput
import aiosqlite
import math

from shared.hardcore_globals import GUILD_INFO, CHANNEL_IDS
from leaderboards.leaderboards_constants import (
    LEADERBOARD_DATABASE_PATH, LEADERBOARD_OPTIONS, LEADERBOARD_EMOJIS, LEADERBOARD_NAMES, SHARED_LEADERBOARD_CHOICES,
    ROLES_WITH_PERMS_TO_USE__LEADERBOARD_PRINT, ROLES_WITH_PERMS_TO_USE__LEADERBOARD_SET,
    BUTTON_LEADERBOARD_PREVIOUS_PAGE, BUTTON_LEADERBOARD_NEXT_PAGE,
)
from leaderboards import db_handler
from leaderboards import leaderboard_rules

"""
#################################################################################################################################
#                                                         LEADERBOARD VIEW                                                      #
#################################################################################################################################
"""

class LeaderboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    def update_buttons(self, current_page: int, total_pages: int):
        self.btn_leaderboard_previous_page.disabled = current_page <= 1
        self.btn_leaderboard_next_page.disabled = current_page >= total_pages

    async def generate_page_embed(self, leaderboard_name: str, total_pages: int, current_page: int) -> discord.Embed:
        offset = (current_page - 1) * 10
        embed = discord.Embed(title=f"{LEADERBOARD_OPTIONS[leaderboard_name]}")
        embed.description = "Here are the top players."
        async with aiosqlite.connect(LEADERBOARD_DATABASE_PATH) as db:
            query = """
                SELECT user_id, pts
                FROM leaderboards
                WHERE leaderboard_name = ?
                ORDER BY pts DESC
                LIMIT 10 OFFSET ?
            """
            async with db.execute(query, (LEADERBOARD_NAMES[leaderboard_name], offset)) as cursor:
                resultados = await cursor.fetchall()

        text_lines = []
        for i, (user_id, pts) in enumerate(resultados):
            rank = i + offset + 1
            text_lines.append(f"**{rank}** <@{user_id}> • {LEADERBOARD_EMOJIS[leaderboard_name]} {pts:,}")
        
        if not text_lines:
            embed.add_field(name="Empty", value="There are no players on this leaderboard yet.")
        else:
            embed.description = "\n".join(text_lines)

        embed.set_footer(text=f"Page {current_page}/{total_pages}")
        return embed

    async def parse_embed_and_turn_page(self, interaction: discord.Interaction, step: int):
        message = interaction.message
        if not message.embeds:
            return await interaction.response.send_message("❌ Could not read embed data ❌", ephemeral=True)

        embed = message.embeds[0]
        lb_code = next((k for k, v in LEADERBOARD_OPTIONS.items() if v == embed.title), None)
        if not lb_code:
            return await interaction.response.send_message("❌ Leaderboard not found ❌", ephemeral=True)

        try:
            pages_str = embed.footer.text.replace("Page ", "").split("/")
            current_page = int(pages_str[0])
            total_pages = int(pages_str[1])
        except Exception:
            return await interaction.response.send_message("❌ Could not read page info ❌", ephemeral=True)

        new_page = current_page + step
        self.update_buttons(new_page, total_pages)
        new_embed = await self.generate_page_embed(lb_code, total_pages, new_page)
        await interaction.response.edit_message(embed=new_embed, view=self)




    @discord.ui.button(label=BUTTON_LEADERBOARD_PREVIOUS_PAGE["label"], style=BUTTON_LEADERBOARD_PREVIOUS_PAGE["style"], custom_id=BUTTON_LEADERBOARD_PREVIOUS_PAGE["cid"])
    async def btn_leaderboard_previous_page (self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.parse_embed_and_turn_page(interaction, -1)

    @discord.ui.button(label=BUTTON_LEADERBOARD_NEXT_PAGE["label"], style=BUTTON_LEADERBOARD_NEXT_PAGE["style"], custom_id=BUTTON_LEADERBOARD_NEXT_PAGE["cid"])
    async def btn_leaderboard_next_page (self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.parse_embed_and_turn_page(interaction, 1)


"""
#################################################################################################################################
#                                                               MODALS                                                          #
#################################################################################################################################
"""

class BattleModeModal(Modal, title="Battle Mode Stats"):
    kills = TextInput(label="Eliminations (Kills)", placeholder="Ex: 287", style=discord.TextStyle.short)
    wins = TextInput(label="Total Wins", placeholder="Ex: 182", style=discord.TextStyle.short)
    full_lobby_wins = TextInput(label="Full Lobby Wins", placeholder="Ex: 59", style=discord.TextStyle.short)

    def __init__ (self, target_user: discord.Member):
        super().__init__()
        self.target_user = target_user

    async def on_submit(self, interaction: discord.Interaction):
        try:
            k = int(self.kills.value)
            w = int(self.wins.value)
            fw = int(self.full_lobby_wins.value)
        except ValueError:
            return await interaction.response.send_message("❌ Please enter only valid integers ❌", ephemeral=True)

        if fw > w:
            return await interaction.response.send_message("❌ The number of 'Full Lobby Wins' cannot be greater than the number of 'Total Wins' ❌", ephemeral=True)
        
        points = leaderboard_rules.calc_battle_mode_points(k, w, fw)
        await db_handler.set_user_points(self.target_user.id, "bm", points)
        
        await interaction.response.send_message(f"✅ The score for {self.target_user.mention} in **{LEADERBOARD_OPTIONS['bm']}** has been set to **{points}** ✅", ephemeral=True)

        bot_commands_channel = interaction.guild.get_channel(CHANNEL_IDS["BOT_COMMANDS_CHANNEL"])
        if not bot_commands_channel:
            print ("I could not find Bot Commands Channel")
            return
        await bot_commands_channel.send(f"✅ Added **{points}** points to {user.mention} in {leaderboard.name}.✅\nCurrent Points: **{new_total}**.")
        leaderboard_logs_channel = interaction.guild.get_channel(CHANNEL_IDS["LEADERBOARD_LOG_CHANNEL"])
        if not leaderboard_logs_channel:
            print ("I could not find Leaderboard Log Channel")
            return
        await leaderboard_logs_channel.send(f"✅ Added **{points}** points to {user.mention} in {leaderboard.name}.✅\nCurrent Points: **{new_total}**.")


class ModdedRunModal(Modal, title="Modded Run Stats"):
    h_mods = TextInput(label="Hotel Modifier %", placeholder="Ex: 300", style=discord.TextStyle.short)
    h_doors = TextInput(label="Hotel Doors Opened", placeholder="Ex: 100", style=discord.TextStyle.short)
    m_mods = TextInput(label="Mines Modifier %", placeholder="Ex: 300", style=discord.TextStyle.short)
    m_doors = TextInput(label="Mines Doors Opened", placeholder="Ex: 100", style=discord.TextStyle.short)

    def __init__ (self, target_user: discord.Member):
        super().__init__()
        self.target_user = target_user

    async def on_submit(self, interaction: discord.Interaction):
        try:
            hm = int(self.h_mods.value)
            hd = int(self.h_doors.value)
            mm = int(self.m_mods.value)
            md = int(self.m_doors.value)
        except ValueError:
            return await interaction.response.send_message("❌ Please enter only valid integers ❌", ephemeral=True)

        if hd > 100 or md > 100:
            return await interaction.response.send_message("❌ It is not possible to open more than 100 doors on the same floor ❌", ephemeral=True)
        
        points = leaderboard_rules.calc_modded_run_points(hm, hd, mm, md)
        await db_handler.set_user_points(self.target_user.id, "m", points)
        
        await interaction.response.send_message(f"✅ The score for {self.target_user.mention} in **{LEADERBOARD_OPTIONS['m']}** has been set to **{points}** ✅", ephemeral=True)

        bot_commands_channel = interaction.guild.get_channel(CHANNEL_IDS["BOT_COMMANDS_CHANNEL"])
        if not bot_commands_channel:
            print ("I could not find Bot Commands Channel")
            return
        await bot_commands_channel.send(f"✅ Added **{points}** points to {user.mention} in {leaderboard.name}.✅\nCurrent Points: **{new_total}**.")
        leaderboard_logs_channel = interaction.guild.get_channel(CHANNEL_IDS["LEADERBOARD_LOG_CHANNEL"])
        if not leaderboard_logs_channel:
            print ("I could not find Leaderboard Log Channel")
            return
        await leaderboard_logs_channel.send(f"✅ Added **{points}** points to {user.mention} in {leaderboard.name}.✅\nCurrent Points: **{new_total}**.")


"""
#################################################################################################################################
#                                                       LEADERBOARD COMMAND                                                     #
#################################################################################################################################
"""

SET_LEADERBOARD_CHOICES = [
    app_commands.Choice(name=LEADERBOARD_OPTIONS["bm"], value="bm"),
    app_commands.Choice(name=LEADERBOARD_OPTIONS["m"], value="m")
]

class LeaderboardCog (commands.GroupCog, group_name="leaderboard", group_description="Leaderboards management commands"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.checks.has_any_role(*ROLES_WITH_PERMS_TO_USE__LEADERBOARD_PRINT)
    @app_commands.command(name="print", description="print leaderboard")
    @app_commands.choices(leaderboard=SHARED_LEADERBOARD_CHOICES)
    async def leaderboard_print(self, interaction: discord.Interaction, leaderboard: app_commands.Choice[str]):
        await interaction.response.defer()

        async with aiosqlite.connect(LEADERBOARD_DATABASE_PATH) as db:
            async with db.execute("SELECT COUNT(*) FROM leaderboards WHERE leaderboard_name = ?", (LEADERBOARD_NAMES[leaderboard.value],)) as cursor:
                total_players = (await cursor.fetchone())[0]
            if total_players == 0:
                await interaction.followup.send("That leaderboard is empty.")
                return

            total_pages = math.ceil(total_players / 10)
            view = LeaderboardView()
            view.update_buttons(current_page=1, total_pages=total_pages)
            initial_embed = await view.generate_page_embed(leaderboard.value, total_pages, 1)
            await interaction.followup.send(embed=initial_embed, view=view)

    @app_commands.checks.has_any_role(*ROLES_WITH_PERMS_TO_USE__LEADERBOARD_SET)
    @app_commands.command(name="set", description="Defines a user's points for a leaderboard, according to that leaderboard's rules.")
    @app_commands.choices(leaderboard=SET_LEADERBOARD_CHOICES)
    async def leaderboard_set(self, interaction: discord.Interaction, leaderboard: app_commands.Choice[str], user: discord.Member):
        if leaderboard.value == "bm":
            modal = BattleModeModal(target_user=user)
            await interaction.response.send_modal(modal)
            return
        
        if leaderboard.value == "m":
            modal = ModdedRunModal(target_user=user)
            await interaction.response.send_modal(modal)
            return

        await interaction.response.send_message("❌ The leaderboard you selected is not supported by this command ❌\nUse /pts instead")

async def setup(bot: commands.Bot):
    await bot.add_cog(LeaderboardCog(bot), guild=GUILD_INFO["GUILD"])