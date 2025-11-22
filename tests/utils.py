def make_team(name: str, members: list):
    return {
        "team_name": name,
        "members": [
            {"user_id": uid, "username": uname, "is_active": active}
            for uid, uname, active in members
        ],
    }
