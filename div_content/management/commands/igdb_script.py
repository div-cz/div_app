import json
import re
import requests
import time

from div_content.models import Game
from django.core.management.base import BaseCommand

# nohup python manage.py igdb_script > div_app/igdb_log_03.log 2>&1 &

# Hide into env variables
IGDB_ID = "wyfdqx678alz66zr0coud8ex9qxn3e"
IGDB_SECRET = "qjvl95ic0wrwqa6mfdidbee54oc1on "
IGDB_TOKEN = "o8s0odvsflgvt573dmfyca0v1bqhbn" # Renew every 60? days

OUTPUT = "div_app/igdb_mapping_04.jsonl"
NOT_FOUND_OUTPUT = "div_app/igdb_not_found_03.jsonl"

CONTROL_CHARS_RE = re.compile(r"[\x00-\x1F\x7F]")

def apicalypse_str(s: str) -> str:
    """Bezpečný string do IGDB APICALYPSE: odstraní řídicí znaky,
    escapuje backslash a dvojité uvozovky, zkrátí extrémně dlouhé vstupy."""
    if not s:
        return ""
    s = CONTROL_CHARS_RE.sub(" ", s).strip()
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return s[:200]


class Command(BaseCommand):
    help = "Namapuje hry z DIV DB na IGDB a uloží je do JSONL souboru"

    def handle(self, *args, **options):
        headers = {
            "Client-ID": IGDB_ID,
            "Authorization": f"Bearer {IGDB_TOKEN}",
        }

        with open(OUTPUT, "w", encoding="utf-8") as f:
            games = Game.objects.filter(gameid__gte=98782) # ID hry
            for game in games: # modify
                self.stdout.write(f"Hledám hru: {game.title}")

                gametitle = apicalypse_str(game.title)

                query = f"""
                fields id, name, cover, summary, first_release_date;
                where name="{gametitle}";
                limit 1;
                """

                r = requests.post(
                    "https://api.igdb.com/v4/games",
                    data=query,
                    headers={**headers, "Content-Type": "text/plain"},
                )
                r.raise_for_status()
                results = r.json()

                if not results:
                    # data = {
                    #     "gameid": game.gameid,
                    #     "title": game.title,
                    #     "summary": None,
                    #     "igdb_id": None, # ID na db igdb
                    #     "cover_id": None, # cover_id z /games
                    #     "image_id": None, # image_id z /covers
                    #     "cover_url": None, # sestavené url
                    # }

                    # f.write(json.dumps(data, ensure_ascii=False) + "\n")´
                    with open(NOT_FOUND_OUTPUT, "a", encoding="utf-8") as nf:
                        nf.write(json.dumps({"gameid": game.gameid, "title": game.title}, ensure_ascii=False) + "\n")
                    self.stdout.write(f"Záznam na IGDB nenalezen: ID={game.gameid}, title={game.title}")
                    continue
                
                igdb_game = results[0]
                igdb_id = igdb_game["id"]
                igdb_name = igdb_game.get("name")
                cover_id = igdb_game.get("cover")
                summary = igdb_game.get("summary")
                first_release_date = igdb_game.get("first_release_date")
                image_id = None
                cover_url = None

                if cover_id:
                    q2 = f"fields id, game, image_id; where id={cover_id};"
                    r2 = requests.post(
                        "https://api.igdb.com/v4/covers",
                        data=q2,
                        headers={**headers, "Content-Type": "text/plain"},
                    )
                    r2.raise_for_status()
                    covers = r2.json()
                    if covers:
                        image_id = covers[0]["image_id"]
                        cover_url = f"https://images.igdb.com/igdb/image/upload/t_cover_big/{image_id}.jpg"
                
                data = {
                    "gameid": game.gameid,
                    "title": game.title,
                    "summary": summary,
                    "first_release_date": first_release_date,
                    "igdb_id": igdb_id, # ID na db igdb
                    "cover_id": cover_id, # cover_id z /games
                    "image_id": image_id, # image_id z /covers
                    "cover_url": cover_url, # sestavené url
                }
                f.write(json.dumps(data, ensure_ascii=False) + "\n")

                self.stdout.write(self.style.SUCCESS(f"{game.title} zapsán úspěšně pod {igdb_game}"))

                time.sleep(0.4)