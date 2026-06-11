from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx
from urllib.parse import quote
from collections import Counter

app = FastAPI()

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.get("/api/naukowiec/{imie_i_nazwisko}")
async def get_naukowiec(imie_i_nazwisko: str):
    safe_query = quote(imie_i_nazwisko)
    async with httpx.AsyncClient() as client:
        auth_resp = await client.get(f"https://api.openalex.org/authors?search={safe_query}")
        author = auth_resp.json()['results'][0]
        author_id = author['id']

        works_resp = await client.get(f"https://api.openalex.org/works?filter=author.id:{author_id}&per-page=25")
        works = works_resp.json()['results']

        coauthors = []
        cited_by = []

        for work in works:
            for autorship in work['authorships']:
                a_name = autorship['author']['display_name']
                if a_name != author['display_name']:
                    coauthors.append(a_name)
            cited_by.append(work['cited_by_count'])

        top_coauthors = Counter(coauthors).most_common(5)
        return {
            "name": author['display_name'],
            "total_citations": author['cited_by_count'],
            "top_coauthors": [{"name": name, "count": count} for name, count in top_coauthors],
            "h_index": author.get('summary_stats', {}).get('h_index', 0)
        }