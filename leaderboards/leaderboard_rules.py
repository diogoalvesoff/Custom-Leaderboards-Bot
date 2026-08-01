def calc_battle_mode_points (kills: int, total_wins: int, full_lobby_wins: int) -> int:
    """
    Computes The Battle Mode points based on these rules:
    - Each Kill = 1 point
    - Each Win (Non Full Lobby) = 3 points
    - Each Win (Full lobby) = 5 points
    """
    non_full_lobby_wins = total_wins - full_lobby_wins
    pontuation = kills + (3 * non_full_lobby_wins) + (5 * full_lobby_wins)
    return pontuation

def calc_modded_run_points (hotel_mods: int, hotel_doors: int, mines_mods: int, mines_doors: int) -> int:
    """
    Computes the Modded Runs points based on these rules:
    - 1 doors opened = 1 point
    - +1% mod = 1* multiplier
    """
    pontuation = (hotel_mods * hotel_doors) + (mines_mods * mines_doors)
    return pontuation