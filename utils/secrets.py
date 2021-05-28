from os import environ as env
import CONFIG

SECRETS = ("TOKEN", "MONGO_URI", "GUILD_ID", "MUTE_ROLE_ID",
           "COUNTING_CHANNEL", "ADMIN_CHANNEL", "BOT_STATUS_CHANNEL",
           "TAG_BLACKLIST_ROLE", "PREFIX", "MOD_ROLE_NAME", "ADMIN_ROLE_NAME",
           "ADDBOT_BLACKLIST_ROLE", "HIDE_NSFW_ROLE_ID", "MOD_ROLE_ID")

for secret in SECRETS:
    globals()[secret] = env.get(secret) or getattr(CONFIG, secret, "")
