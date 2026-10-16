import aiohttp
from datetime import datetime
import json
from html import unescape

class MetrixService:
    def __init__(self, country_code, metrix_api):
        self.country_code = country_code
        self.base_url = "https://discgolfmetrix.com/api.php"
        self.metrix_api = metrix_api

    async def does_course_exist(self, course_name: str) -> bool:
        """Kontrollib API-st, kas rada eksisteerib (Täpitähtede toega!)"""
        
        # Küsime KÕIK Eesti rajad, eemaldame "name" parameetri, et API-t mitte segadusse ajada
        params = {
            "content": "courses_list",
            "country_code": self.country_code
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        # Loeme API vastuse õigeks JSON andmestikuks
                        data = await response.json()
                        
                        # See on MAAGILINE RIDA: muudame andmed tagasi tekstiks,
                        # aga ensure_ascii=False sunnib "\u00e4" muutuma tagasi iluseks "ä"-ks!
                        text_with_accents = json.dumps(data, ensure_ascii=False).lower()
                        
                        # Nüüd suudab Python "järve" otsida
                        return course_name.lower() in text_with_accents
        except Exception as e:
            print(f"Viga radade laadimisel: {e}")
            
        return True # Fail-safe, kui API on maas

    async def get_schedule_message(self, course_name: str, target_date: str) -> str:
        """Küsib mängud ja paneb Discordi vastuse kokku"""
        
        if not await self.does_course_exist(course_name):
            return f"Vabandust, aga rada nimega **{course_name}** ei leidu süsteemis!"

        # (MÄRKUS: Lisa siia params sisse täpselt need väljad, mida sa Javas kasutasid mängude otsimiseks!)
        params = {
            "content": "competitions", # Või mis iganes sisu sa Javas küsisid
            "code": self.metrix_api,
            "country_code": self.country_code,
            "date1": target_date,
            "date2": target_date,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        # Python muudab JSONi automaatselt mugavaks listiks! Ei mingit DTO-d!
                        data = await response.json() 
                        
                        # See eeldab, et API tagastab listi nimega "competitions"
                        competitions = data.get("Competitions", [])
                        
                        # Filtreerime välja õige raja
                        matching_events = [
                            comp for comp in competitions
                            if course_name.lower() in comp.get("CourseName", "").lower()
                        ]

                        # Muudame kuupäeva ilusamaks (YYYY-MM-DD -> DD.MM.YYYY)
                        pretty_date = datetime.strptime(target_date, "%Y-%m-%d").strftime("%d.%m.%Y")

                        if matching_events:
                            reply = f" **MÄNGUD LEITUD!** \n\n"
                            for comp in matching_events:
                                name = unescape(comp.get('Name'))
                                course = unescape(comp.get('CourseName'))

                                reply += f"**Võistlus:** {name}\n"
                                reply += f"**Rada:** {course}\n"
                                reply += f"**Aeg:** {comp.get('Time')}\n"
                                reply += f"**Kuupäev:** {pretty_date}\n"
                                reply += f"**Hetkel registreerinud mängijate arv:** {comp.get('PlayersCount')}\n"
                                reply += "-------------------------\n"
                            return reply
                        else:
                            return f"Kuupäeval **{pretty_date}** ei tundu rajal **{course_name}** ühtegi mängu olevat."

        except Exception as e:
            return f"Viga Metrixiga ühendumisel: {e}"

        return "Andmeid ei leitud."