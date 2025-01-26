import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
from datetime import datetime
import pytz
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the bot token from the environment
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Bot token not found! Make sure DISCORD_BOT_TOKEN is set in the .env file.")

# Configure Chicago timezone
CHICAGO_TZ = pytz.timezone("America/Chicago")

# Custom log formatter for timestamps in Chicago time
class ChicagoTimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=CHICAGO_TZ)
        return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")

# Configure logging
log_formatter = ChicagoTimeFormatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler = logging.FileHandler("reaction_role_bot.log")
file_handler.setFormatter(log_formatter)
logging.basicConfig(level=logging.INFO, handlers=[file_handler])

# Enable privileged intents for member access
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Reaction role configuration
GUILD_ID = 1329284464928624752  # Replace with your server's ID
ROLE_CHANNEL_ID = 1329284464928624755  # Replace with the channel ID where reactions occur
ROLE_MESSAGE_ID = 1330743887345487872  # Replace with the message ID for reactions
EMOJI_ROLE_MAP = {
    ":heart_on_fire:": 1330735745526272102,  # Replace with emoji and role ID
}

# Event: Bot is ready
@bot.event
async def on_ready():
    logging.info(f"Bot logged in as {bot.user}")
    print(f"Bot logged in as {bot.user}")

# Event: Add role on reaction add
@bot.event
async def on_raw_reaction_add(payload):
    if payload.guild_id == GUILD_ID and payload.channel_id == ROLE_CHANNEL_ID and payload.message_id == ROLE_MESSAGE_ID:
        guild = bot.get_guild(GUILD_ID)
        role = guild.get_role(EMOJI_ROLE_MAP.get(payload.emoji.name))
        member = guild.get_member(payload.user_id)
        if role and member:
            await member.add_roles(role)
            logging.info(f"Assigned role {role.name} to {member.name} (ID: {member.id})")

        # Log the reaction in the channel
        channel = guild.get_channel(ROLE_CHANNEL_ID)
        if channel:
            await channel.send(f"{member.name} reacted with {payload.emoji.name}.")

# Event: Remove role on reaction remove
@bot.event
async def on_raw_reaction_remove(payload):
    if payload.guild_id == GUILD_ID and payload.channel_id == ROLE_CHANNEL_ID and payload.message_id == ROLE_MESSAGE_ID:
        guild = bot.get_guild(GUILD_ID)
        role = guild.get_role(EMOJI_ROLE_MAP.get(payload.emoji.name))
        member = guild.get_member(payload.user_id)
        if role and member:
            await member.remove_roles(role)
            logging.info(f"Removed role {role.name} from {member.name} (ID: {member.id})")

        # Log the reaction removal in the channel
        channel = guild.get_channel(ROLE_CHANNEL_ID)
        if channel:
            await channel.send(f"{member.name} removed reaction {payload.emoji.name}.")

# Run the bot
bot.run(TOKEN)