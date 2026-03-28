from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

curtidas_count = 0
current_tab_index = 0                         

def render_str(template_name: str, **kwargs) -> str:
    return templates.env.get_template(template_name).render(**kwargs)

def tab_response(content_template: str, active_tab: str, **extra) -> HTMLResponse:
    global current_tab_index
    current_tab_index = tabs.index(active_tab)

    content_html = render_str(content_template, active_tab=active_tab,
                              curtidas=curtidas_count, **extra)
    nav_html = render_str("nav.html", active_tab=active_tab, oob=True)

    return HTMLResponse(content=content_html + nav_html)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    global current_tab_index
    current_tab_index = 0
    return templates.TemplateResponse("base.html", {
        "request": request,
        "active_tab": "curtidas",
        "curtidas": curtidas_count,
        "oob": False,
    })

@app.get("/tab/curtidas", response_class=HTMLResponse)
def tab_curtidas():
    return tab_response("tab_curtidas.html", "curtidas")

@app.get("/tab/jupiter", response_class=HTMLResponse)
def tab_jupiter():
    return tab_response("tab_jupiter.html", "jupiter")

@app.get("/tab/professor", response_class=HTMLResponse)
def tab_professor():
    return tab_response("tab_professor.html", "professor")

@app.get("/tab/next", response_class=HTMLResponse)
def tab_next():
    """Avança ciclicamente para a próxima aba. Chamado pelo atalho de teclado."""
    global current_tab_index
    current_tab_index = (current_tab_index + 1) % len(tabs)
    next_tab = tabs[current_tab_index]

    template_map = {
        "curtidas":  "tab_curtidas.html",
        "jupiter":   "tab_jupiter.html",
        "professor": "tab_professor.html",
    }
    return tab_response(template_map[next_tab], next_tab)


@app.post("/curtir", response_class=HTMLResponse)
def curtir():
    """Incrementa o contador e devolve apenas o novo número."""
    global curtidas_count
    curtidas_count += 1
    return HTMLResponse(str(curtidas_count))

@app.delete("/curtir", response_class=HTMLResponse)
def resetar_curtidas():
    """Zera o contador e devolve 0."""
    global curtidas_count
    curtidas_count = 0
    return HTMLResponse(str(curtidas_count))
