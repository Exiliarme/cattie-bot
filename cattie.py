import discord
from discord.ext import commands, tasks
from discord import app_commands
import openai
import os
import random
import logging
from datetime import datetime

# ----------------------------------------
# CONFIGURATION
# ----------------------------------------

# Load environment variables
DISCORD_TOKEN = os.getenv("CATTIE-TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = 901223334480576643  # Only this user can activate Cattie
ACTIVATION_KEY = "sprinkles-forever"

# Set up OpenAI
openai.api_key = OPENAI_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)

# Intents
intents = discord.Intents.default()
intents.message_content = True

# Bot Setup
bot = commands.Bot(command_prefix="!", intents=intents)

activated = False

# ----------------------------------------
# CHATGPT REPLY HELPER
# ----------------------------------------

async def get_chatgpt_reply(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Oops! I had a little meltdown.\n\n{e}"

# ----------------------------------------
# AUTO-RESPONSE TO MENTIONS
# ----------------------------------------

@bot.event
async def on_message(message):
    global activated

    if message.author.bot:
        return

    if bot.user in message.mentions:
        content_lower = message.content.lower()

        # Check activation
        if not activated and message.author.id == OWNER_ID:
            if ACTIVATION_KEY in content_lower:
                activated = True
                await message.channel.send("Cattie is now activated and ready to flirt 💋")
                return

        if not activated:
            return

        if "love advice" in content_lower:
            prompt = "You're a sweet, flirty, but respectful girl named Cattie who gives warm, charming, and cheeky love advice. A user asked for love advice. Give your best tip."
            reply = await get_chatgpt_reply(prompt)
            await message.channel.send(reply)

        elif "gif" in content_lower:
            prompt = "You're a flirty, funny character named Cattie. Write a description of a hilarious or cute reaction GIF in a single sentence, like you're sending one."
            reply = await get_chatgpt_reply(prompt)
            await message.channel.send(reply)

        elif "help" in content_lower:
            await message.channel.send(
                "Hey love 💋 I'm Cattie — your favorite flirt and life coach. Try asking me:\n"
                "- @Cattie love advice\n"
                "- @Cattie gif\n"
                "And I *might* reply. Depends if you're cute. 💅"
            )

        else:
            prompt = f"You're a sweet, flirty, fun girl named Cattie. Someone just said: '{message.content}'. Write a playful and cheeky one-line response."
            reply = await get_chatgpt_reply(prompt)
            await message.channel.send(reply)

    await bot.process_commands(message)

# ----------------------------------------
# WEEKLY LOVE MESSAGE TO BEEF
# ----------------------------------------

@tasks.loop(hours=24)
async def weekly_message():
    today = datetime.utcnow().weekday()  # Monday = 0 ... Sunday = 6
    if today == 2:  # Wednesday, change as needed
        guild = discord.utils.get(bot.guilds)
        if guild:
            user = guild.get_member(480787863936565261)
            if user:
                prompt = "You're Cattie. Send a sweet, flirty, loving weekly message to Beef (your crush) without being too intense."
                message = await get_chatgpt_reply(prompt)
                channel = discord.utils.get(guild.text_channels, name="general")  # Change as needed
                if channel:
                    await channel.send(f"{user.mention} {message}")

# ----------------------------------------
# ON READY
# ----------------------------------------

@bot.event
async def on_ready():
    print(f"Cattie is online as {bot.user}")
    if not weekly_message.is_running():
        weekly_message.start()

# ----------------------------------------
# RUN CATTIE
# ----------------------------------------

bot.run(DISCORD_TOKEN)
