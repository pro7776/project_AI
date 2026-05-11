from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import httpx
import os

app = FastAPI(title="Book Recommender Web UI")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

API_URL = os.getenv("API_URL", "http://api:8001")


def render_html(books=None):
    with open("app/templates/index.html", "r", encoding="utf-8") as f:
        template = f.read()

    if books is not None:
        results_html = "<div class='results'><h2>Результаты:</h2>"
        if books:
            results_html += "<ul>"
            for book in books:
                results_html += f"<li><strong>{book['title']}</strong> – {book['author']}<br><span class='desc'>{book['description']}</span></li>"
            results_html += "</ul>"
        else:
            results_html += "<p>Ничего не найдено. Попробуйте другой запрос.</p>"
        results_html += "</div>"
    else:
        results_html = ""

    return template.replace("{{ results }}", results_html)


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=render_html(books=None))


@app.post("/search", response_class=HTMLResponse)
async def search(query: str = Form(...), search_type: str = Form(...)):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{API_URL}/recommend",
                json={"query": query, "type": search_type},
                timeout=5.0
            )
            resp.raise_for_status()
            books = resp.json()
        except Exception:
            books = []
    return HTMLResponse(content=render_html(books=books))
