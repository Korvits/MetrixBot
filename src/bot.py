import discord
import os
from datetime import datetime
from dotenv import load_dotenv
from src.metrix_service import MetrixService

# Laeme .env failist muutujad
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
COUNTRY_CODE = os.getenv("COUNTRY_CODE", "EE")
METRIX_API = os.getenv("METRIX_API_CODE")

# Seadistame boti ja õigused (Intents)
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

service = MetrixService(COUNTRY_CODE, METRIX_API)

@client.event
async def on_ready():
    print(f"Juhuu! Olen sisse loginud kui {client.user}")

@client.event
async def on_message(message):
    # Ignoreerime iseenda ja teiste botide sõnumeid
    if message.author.bot:
        return

    if message.content.startswith("!"):
        # Lõikame hüüumärgi ära ja jagame sõnumi juppideks
        parts = message.content[1:].strip().split()
        if not parts:
            return

        course_name = parts[0]
        
        # Vaikimisi kasutame tänast kuupäeva
        target_date = datetime.now().strftime("%Y-%m-%d")

        # Kui kasutaja andis kaasa kuupäeva (nt "18.04")
        if len(parts) > 1:
            try:
                # Parsime DD.MM ja lisame käesoleva aasta
                current_year = datetime.now().year
                parsed_date = datetime.strptime(parts[1], "%d.%m")
                parsed_date = parsed_date.replace(year=current_year)
                
                # Muudame YYYY-MM-DD kujule
                target_date = parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                await message.channel.send("Viga! Kuupäev peab olema kujul PP.KK (nt 18.04).")
                return

        # Anname teada, et mõtleme
        await message.channel.send("Otsin andmeid...")

        # KÜSIME TEENUSELT VASTUST (kuna see on async, kasutame 'await')
        final_reply = await service.get_schedule_message(course_name, target_date)
        
        # DISCORDI PIIRANGU LAHENDUS: Saadame vastuse juppidena, kui see on üle 1900 märgi
        while len(final_reply) > 0:
            # Võtame esimesed 1900 tähemärki (jätame väikese varu 2000-st)
            chunk = final_reply[:1900]
            await message.channel.send(chunk)
            
            # Eemaldame saadetud osa algsest tekstist, et tsükkel saaks jätkuda
            final_reply = final_reply[1900:]

# Paneme boti tööle!
client.run(TOKEN)