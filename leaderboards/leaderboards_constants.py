import discord
from discord import app_commands
from shared.hardcore_globals import ROLE_IDS


"""
#################################################################################################################################
#                                                              CONFIGS                                                          #
#################################################################################################################################
"""

COOLDOWN = 2
DELAY_BEFORE_DELETING_MESSAGE = 10


"""
#################################################################################################################################
#                                                               DATA                                                            #
#################################################################################################################################
"""

LEADERBOARD_DATABASE_PATH = "leaderboards/data.db"
LEADERBOARD_OPTIONS = {
    "c": "🎯 Challenge 🎯",
    "bm": "💣 Battle Mode 💣",
    "m": "💯 Modifier 💯",
    "d": "🏴‍☠️ Death 🏴‍☠️",
    "t": "⚔️ Tournament ⚔️"
}
LEADERBOARD_EMOJIS = {
    "c": "🎯",
    "bm": "💣",
    "m": "💯",
    "d": "🏴‍☠️",
    "t": "⚔️"
}
LEADERBOARD_NAMES = {
    "c": "challenge_leaderboard", "challenge": "challenge_leaderboard",
    "bm": "battle_mode_leaderboard", "battle mode": "battle_mode_leaderboard",
    "m": "modifiers_leaderboard", "modifiers": "modifiers_leaderboard",
    "d": "death_leaderboard", "death": "death_leaderboard",
    "t": "tournament_leaderboard", "tournament": "tournament_leaderboard"
}

SHARED_LEADERBOARD_CHOICES = [
    app_commands.Choice(name=LEADERBOARD_OPTIONS["c"], value="c"),
    app_commands.Choice(name=LEADERBOARD_OPTIONS["bm"], value="bm"),
    app_commands.Choice(name=LEADERBOARD_OPTIONS["m"], value="m"),
    app_commands.Choice(name=LEADERBOARD_OPTIONS["d"], value="d"),
    app_commands.Choice(name=LEADERBOARD_OPTIONS["t"], value="t")
]


"""
#################################################################################################################################
#                                                           COMMAND PERMS                                                       #
#################################################################################################################################
"""

ROLES_WITH_PERMS_TO_USE__LEADERBOARD_PRINT = [
    ROLE_IDS["ADMIN_ROLE_ID"],
    ROLE_IDS["HEAD_MOD_ROLE_ID"],
    ROLE_IDS["LEADERBOARDS_MANAGER_ROLE_ID"]
]
ROLES_WITH_PERMS_TO_USE__LEADERBOARD_SET = [
    ROLE_IDS["ADMIN_ROLE_ID"],
    ROLE_IDS["LEADERBOARDS_MANAGER_ROLE_ID"]
]

ROLES_WITH_PERMS_TO_USE__PTS_ADD = [
    ROLE_IDS["ADMIN_ROLE_ID"],
    ROLE_IDS["LEADERBOARDS_MANAGER_ROLE_ID"]
]
ROLES_WITH_PERMS_TO_USE__PTS_REM = [
    ROLE_IDS["ADMIN_ROLE_ID"],
    ROLE_IDS["LEADERBOARDS_MANAGER_ROLE_ID"]
]
ROLES_WITH_PERMS_TO_USE__PTS_SET = [
    ROLE_IDS["ADMIN_ROLE_ID"],
]

ROLES_WITH_PERMS_TO__CLOSE_A_BATTLE_THREAD = [
    ROLE_IDS["ADMIN_ROLE_ID"],
    ROLE_IDS["HEAD_MOD_ROLE_ID"],
    ROLE_IDS["LEADERBOARDS_MANAGER_ROLE_ID"]
]
ROLES_WITH_PERMS_TO__LOCK_A_BATTLE_THREAD = [
    ROLE_IDS["ADMIN_ROLE_ID"],
    ROLE_IDS["HEAD_MOD_ROLE_ID"],
    ROLE_IDS["LEADERBOARDS_MANAGER_ROLE_ID"]
]
ROLES_WITH_PERMS_TO__UNLOCK_A_BATTLE_THREAD = [
    ROLE_IDS["ADMIN_ROLE_ID"],
    ROLE_IDS["HEAD_MOD_ROLE_ID"],
    ROLE_IDS["LEADERBOARDS_MANAGER_ROLE_ID"]
]
ROLES_WITH_PERMS_TO__TALK_IN_BATTLE_CHANNEL = [
    ROLE_IDS["ADMIN_ROLE_ID"],
    ROLE_IDS["HEAD_MOD_ROLE_ID"],
    ROLE_IDS["MOD_ROLE_ID"],
    ROLE_IDS["LEADERBOARDS_MANAGER_ROLE_ID"]
]


"""
#################################################################################################################################
#                                                              BUTTONS                                                          #
#################################################################################################################################
"""

BUTTON_BATTLE_JOIN_THREAD = {
    "label": "🔥JOIN🔥",
    "style": discord.ButtonStyle.success,
    "cid": "btn_battle_join"
}
BUTTON_BATTLE_CLOSE_THREAD = {
    "label": "✖️CLOSE✖️",
    "style": discord.ButtonStyle.danger,
    "cid": "btn_battle_close_thread"
}
BUTTON_BATTLE_LOCK_THREAD = {
    "label": "🔒LOCK🔒",
    "style": discord.ButtonStyle.secondary,
    "cid": "btn_battle_lock_thread"
}
BUTTON_BATTLE_UNLOCK_THREAD = {
    "label": "🔓UNLOCK🔓",
    "style": discord.ButtonStyle.success,
    "cid": "btn_battle_unlock_thread"
}

BUTTON_LEADERBOARD_PREVIOUS_PAGE = {
    "label": "Previous Page",
    "style": discord.ButtonStyle.primary,
    "cid": "btn_leaderboard_previous_page"
}
BUTTON_LEADERBOARD_NEXT_PAGE = {
    "label": "Next Page",
    "style": discord.ButtonStyle.primary,
    "cid": "btn_leaderboard_next_page"
}


"""
#################################################################################################################################
#                                                              EMBEDS                                                           #
#################################################################################################################################
"""

EMBED_BATTLE_THREAD = {
    "title" : "⚔️ Battle Session ⚔️",
    "description" : "Use this space to describe the battle terms.\nTry to make it clear so all players understand the rules",
    "color" : 0xff5500
}