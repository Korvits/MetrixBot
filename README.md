# MetrixBot

MetrixBot is a Discord bot that finds disc golf competitions from Disc Golf Metrix by course and date. It displays event details and registered player counts, with responses in Estonian.

## Run locally

1. Open a terminal in the extracted project folder and install dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

2. Create a `.env` file in that folder:

   ```env
   DISCORD_TOKEN=your_discord_bot_token
   COUNTRY_CODE=EE
   METRIX_API_CODE=your_metrix_api_code
   ```

3. Enable **Message Content Intent** in the Discord Developer Portal and invite your bot to your server with permission to view and send messages.
4. Start the bot:

   ```powershell
   py src/bot.py
   ```

Use `!järve` or `!järve 18.04` in Discord. Press **Ctrl+C** to stop the bot. Keep `.env` private and stop any hosted copy before running the same bot locally.