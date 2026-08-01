import discord
from discord import app_commands
from discord.ext import commands
from shared.hardcore_globals import (
    GUILD_INFO, CHANNEL_IDS
)
from leaderboards.leaderboards_constants import (
    BUTTON_BATTLE_JOIN_THREAD, BUTTON_BATTLE_CLOSE_THREAD, BUTTON_BATTLE_LOCK_THREAD, BUTTON_BATTLE_UNLOCK_THREAD,
    EMBED_BATTLE_THREAD,
    ROLES_WITH_PERMS_TO__CLOSE_A_BATTLE_THREAD, ROLES_WITH_PERMS_TO__CLOSE_A_BATTLE_THREAD_WITH_VALID_SEED, ROLES_WITH_PERMS_TO__LOCK_A_BATTLE_THREAD, ROLES_WITH_PERMS_TO__UNLOCK_A_BATTLE_THREAD
)


"""
#################################################################################################################################
#                                                            UTILS (TEMP)                                                       #
#################################################################################################################################
"""

def is_valid_seed(seed: str) -> bool:
    return False


"""
#################################################################################################################################
#                                                               BATTLE                                                          #
#################################################################################################################################
"""

class ChallengeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label=BUTTON_BATTLE_JOIN_THREAD["label"], style=BUTTON_BATTLE_JOIN_THREAD["style"], custom_id=BUTTON_BATTLE_JOIN_THREAD["cid"])
    async def btn_challenge_join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.message.embeds:
            await interaction.response.send_message("❌ Coudn't read message embed")
            print ("Err: Coudn't read battle embed to extract thread id")
            return
        embed = interaction.message.embeds[0]
        try:
            thread_id_str = embed.footer.text.split("Thread: ")[1]
            thread_id = int(thread_id_str)
        except (IndexError, ValueError, AttributeError) as e:
            await interaction.response.send_message("Err: Coudn't find thread ID. Technical detail", ephemeral=True)
            print(f"Err: Coudnt't extract thread ID from embed: {e}")
            return

        thread = interaction.guild.get_thread(thread_id)
        if not thread:
            await interaction.response.send_message("❌ This thread doesn't exist.", ephemeral=True)
            return
        
        if thread.archived:
            await interaction.response.send_message("❌ Too late! This challenge is over.", ephemeral=True)
            return
        await thread.add_user(interaction.user)
        await interaction.response.send_message(f"✅ You joined {thread.mention}! Good luck!.", ephemeral=True)


class WinnerSelectView(discord.ui.View):
    def __init__(self, thread: discord.Thread, seed: str):
        super().__init__(timeout=None)
        self.thread = thread
        self.seed = seed
        self.add_item(WinnerSelect())

class WinnerSelect(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(placeholder="Select the winner...", min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        winner = self.values[0]
        # In the future, use self.view.seed to search info and add the points to the winner here

        await interaction.response.send_message(f"🏆 {winner.mention} won this battle🏆\n Closing the arena...", ephemeral=False)
        await self.view.thread.edit(archived=True, locked=True)


class CloseThreadView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # close
    @discord.ui.button(label = BUTTON_BATTLE_CLOSE_THREAD["label"], style=BUTTON_BATTLE_CLOSE_THREAD["style"], custom_id=BUTTON_BATTLE_CLOSE_THREAD["cid"])
    async def btn_battle_close_thread(self, interaction: discord.Interaction, button: discord.ui.Button):
        thread = interaction.channel

        # Extract Seed
        seed = None
        author_id = None
        if interaction.message.embeds:
            footer_text = interaction.message.embeds[0].footer.text

            # Expected format: "AuthorID: 1234567890 | Seed: None"
            if "AuthorID: " in footer_text:
                parts = footer_text.split(" | ")
                author_id_str = parts[0].replace("AuthorID: ", "").strip()
                if author_id_str.isdigit():
                    author_id = int(author_id_str)

            if " | Seed: " in footer_text:
                extracted_seed = footer_text.split(" | Seed: ")[1]
                if extracted_seed != "None":
                    seed = extracted_seed
        
        # Process Seed
        if seed and is_valid_seed(seed):
            has_permission = any(role.id in ROLES_WITH_PERMS_TO__CLOSE_A_BATTLE_THREAD_WITH_VALID_SEED for role in interaction.user.roles)
            if not has_permission:
                await interaction.response.send_message("❌ Only Admins and Leaderboards Managers can close ranked battles ❌", ephemeral=True)
                return

            await interaction.response.send_message(
                "🏆 Ranked Battle detected! Select the winner below to close the arena:",
                view=WinnerSelectView(thread=thread, seed=seed),
                ephemeral=True
            )

        else:
            has_permission = any(role.id in ROLES_WITH_PERMS_TO__CLOSE_A_BATTLE_THREAD for role in interaction.user.roles)
            is_author = (interaction.user.id == author_id)

            if not (has_permission or is_author):
                await interaction.response.send_message("❌ You don't have permission to close this casual battle ❌", ephemeral=True)
                return
                
            await interaction.response.send_message("🏁 Arena closed 🏁")
            await thread.edit(archived=True, locked=True)

    # lock
    @discord.ui.button(label = BUTTON_BATTLE_LOCK_THREAD["label"], style=BUTTON_BATTLE_LOCK_THREAD["style"], custom_id=BUTTON_BATTLE_LOCK_THREAD["cid"])
    async def btn_battle_lock_thread(self, interaction: discord.Interaction, button: discord.ui.Button):
        thread = interaction.channel

        has_permission = any(role.id in ROLES_WITH_PERMS_TO__LOCK_A_BATTLE_THREAD for role in interaction.user.roles)
        if not has_permission:
            await interaction.response.send_message("❌ You can't lock this thread.", ephemeral=True)
            return

        await interaction.response.send_message("🔒 Arena Locked 🔒")
        await thread.edit(locked=True)

    # unlock
    @discord.ui.button(label = BUTTON_BATTLE_UNLOCK_THREAD["label"], style=BUTTON_BATTLE_UNLOCK_THREAD["style"], custom_id=BUTTON_BATTLE_UNLOCK_THREAD["cid"])
    async def btn_battle_unlock_thread(self, interaction: discord.Interaction, button: discord.ui.Button):
        thread = interaction.channel

        has_permission = any(role.id in ROLES_WITH_PERMS_TO__UNLOCK_A_BATTLE_THREAD for role in interaction.user.roles)
        if not has_permission:
            await interaction.response.send_message("❌ You can't unlock this thread.", ephemeral=True)
            return

        await interaction.response.send_message("🔓 Arena Unlocked 🔓")
        await thread.edit(locked=False)

class BattleCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="battle", description="Hello warrior. Use me to fight 1 or more warriors in an organized battle field")
    async def battle(self, interaction: discord.Interaction, title: str, description: str = None, seed: str = None):
        if interaction.channel.id != CHANNEL_IDS.get("BATTLE_CHANNEL"):
            battle_channel = interaction.guild.get_channel(CHANNEL_IDS.get("BATTLE_CHANNEL"))
            if not battle_channel:
                print("Err: Battle channel doesn't exist")
                return
            await interaction.response.send_message(f"❌ I'm only only executable in {battle_channel.mention}", ephemeral=True)
            return

        await interaction.response.defer()
        try:
            thread = await interaction.channel.create_thread(
                name = f"⚔️ Battle: {title[:40]} - {interaction.user.display_name} ⚔️",
                type = discord.ChannelType.private_thread,
                invitable=False
            )
        except discord.Forbidden as e:
            await interaction.followup.send("❌ I don't have perms create private threads in this channel")
            print(f"Err: Missing Access - {e}")
            return
        except discord.HTTPException as e:
            await interaction.followup.send("❌ An error occurred while communicating with discord", ephemeral=True)
            print(f"Err: HTTP Exception - {e}")
            return
        except Exception as e:
            await interaction.followup.send("❌ Something wrong happened")
            print(f"Err: Something wrong happened - {e}")
            return

        embed_main = discord.Embed(
            title=f"⚔️ Battle {title} ⚔️",
            description=description.capitalize() if description and description.strip() else "Join to compete!",
            color=discord.Color.dark_purple()
        )
        embed_main.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed_main.set_footer(text=f"Created by {interaction.user.display_name} | Thread: {thread.id}")

        await interaction.followup.send(embed=embed_main, view=ChallengeView())

        embed_thread = discord.Embed(
            title=EMBED_BATTLE_THREAD["title"],
            description=EMBED_BATTLE_THREAD["description"],
            color=EMBED_BATTLE_THREAD["color"]
        )
        embed_thread.set_footer(text=f"AuthorID: {interaction.user.id} | Seed: {seed if seed else 'None'}")
    
        await thread.send(f"{interaction.user.mention}, the arena is ready!", embed=embed_thread, view=CloseThreadView())


async def setup(bot: commands.Bot):
    await bot.add_cog(BattleCog(bot), guild=GUILD_INFO["GUILD"])