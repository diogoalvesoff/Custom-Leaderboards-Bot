import discord
from discord import app_commands
from discord.ext import commands
from shared.hardcore_globals import GUILD_INFO
from leaderboards.leaderboards_constants import (
    LEADERBOARD_DATABASE_PATH, LEADERBOARD_OPTIONS, LEADERBOARD_NAMES, LEADERBOARD_EMOJIS,
    ROLES_WITH_PERMS_TO_USE__LEADERBOARD_PRINT, ROLES_WITH_PERMS_TO_USE__LEADERBOARD_SET,
    BUTTON_LEADERBOARD_PREVIOUS_PAGE, BUTTON_LEADERBOARD_NEXT_PAGE,
)

"""
#################################################################################################################################
#                                                            LEADERBOARD                                                        #
#################################################################################################################################
"""

class LeaderboardView(discord.ui.View):
    def __init__(self, leaderboard_name: str, total_pages: int, current_page: int = 1):
        super().__init__(timeout=None)
        self.leaderboard_name = leaderboard_name
        self.total_pages = total_pages
        self.current_page = current_page
        self.update_buttons()

    def update_buttons(self):
        self.btn_prev.disabled = self.current_page == 1
        self.btn_next.disabled = self.current_page >= self.total_pages

    async def generate_page_embed(self) -> discord.Embed:
        offset = (self.current_page - 1) * 10
        embed = discord.Embed(title=f"{LEADERBOARD_OPTIONS[self.leaderboard_name]}")
        embed.description = "Here are the top players."
        async with aiosqlite.connect(LEADERBOARD_DATABASE_PATH) as db:
            query = """
                SELECT user_id, pts
                FROM leaderboards
                WHERE leaderboard_name = ?
                ORDER BY pts DESC
                LIMIT 10 OFFSET ?
            """
            async with db.execute(query, (LEADERBOARD_NAMES[self.leaderboard_name], offset)) as cursor:
                resultados = await cursor.fetchall()

        text_lines = []
        for i, (user_id, pts) in enumerate(resultados):
            rank = i + offset + 1
            text_lines.append(f"**{rank}** <@{user_id}> • {LEADERBOARD_EMOJIS[self.leaderboard_name]} {pts:,}")
        
        if not text_lines:
            embed.add_field(name="Empty", value="There are no players on this leaderboard yet.")
        else:
            embed.description = "\n".join(text_lines)

        embed.set_footer(text=f"Page {self.current_page}/{self.total_pages}")
        return embed

    @discord.ui.button(label=BUTTON_LEADERBOARD_PREVIOUS_PAGE["label"], style=BUTTON_LEADERBOARD_PREVIOUS_PAGE["style"], custom_id=BUTTON_LEADERBOARD_PREVIOUS_PAGE["cid"])
    async def btn_leaderboard_previous_page (self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        self.update_buttons()
        new_embed = await self.generate_page_embed()
        await interaction.response.edit_message(embed=new_embed, view=self)

    @discord.ui.button(label=BUTTON_LEADERBOARD_NEXT_PAGE["label"], style=BUTTON_LEADERBOARD_NEXT_PAGE["style"], custom_id=BUTTON_LEADERBOARD_NEXT_PAGE["cid"])
    async def btn_leaderboard_next_page (self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        self.update_buttons()
        new_embed = await self.generate_page_embed()
        await interaction.response.edit_message(embed=new_embed, view=self)


class LeaderboardCog (commands.GroupCog, group_name="pts", group_description="Leaderboards management commands"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.checks.has_any_role(*ROLES_WITH_PERMS_TO_USE__LEADERBOARD_PRINT)
    @app_commands.command(name="print", description="print leaderboard", guild=GUILD_INFO["GUILD"])
    @app_commands.choices(leaderboard=SHARED_LEADERBOARD_CHOICES)
    async def leaderboard_print(interaction: discord.Interaction, leaderboard: app_commands.Choice[str]):
        await interaction.response.defer()

        async with aiosqlite.connect(LEADERBOARD_DATABASE_PATH) as db:
            async with db.execute("SELECT COUNT(*) FROM leaderboards WHERE leaderboard_name = ?", (LEADERBOARD_NAMES[leaderboard.value],)) as cursor:
                total_players = (await cursor.fetchone())[0]
            if total_players == 0:
                await interaction.followup.send("That leaderboard is empty.")
                return

            total_pages = math.ceil(total_players / 10)
            view = LeaderboardView(leaderboard_name=leaderboard.value, total_pages=total_pages, current_page=1)
            initial_embed = await view.generate_page_embed()
            await interaction.followup.send(embed=initial_embed, view=view)

    @app_commands.checks.has_any_role(*ROLES_WITH_PERMS_TO_USE__LEADERBOARD_SET)
    @app_commands.command(name="set", description="Defines a user's points for a leaderboard, according to that leaderboard's rules.", guild=GUILD_INFO["GUILD"])
    @app_commands.choices(leaderboard=SHARED_LEADERBOARD_CHOICES)
    async def leaderboard_set(interaction: discord.Interaction, leaderboard: app_commands.Choice[str], user: discord.Member):
        pass

async def setup(bot: commands.Bot):
    await bot.add_cog(LeaderboardCog(bot), guild=GUILD_INFO["GUILD"])