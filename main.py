from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx
from urllib.parse import quote

app = FastAPI()

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.get("/api/naukowiec/{imie_i_nazwisko}")
async def get_naukowiec(imie_i_nazwisko: str):
    safe_query = quote(imie_i_nazwisko)
    async with httpx.AsyncClient() as client:
        url = f"https://api.openalex.org/authors?search={safe_query}"
        response = await client.get(url)
        data = response.json()

        if not data['results']:
            return {"error": "Nie znaleziono"}

        author = data['results'][0]
        return {
            "name": author['display_name'],
            "cited_by_count": author['cited_by_count'],
            "coauthors": [{"id": c['id'], "label": c['display_name']} for c in
                          author.get('last_known_institutions', [])]
        }