from fastapi import FastAPI, Request, Depends, HTTPException, status, Cookie, Response, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Annotated

app = FastAPI()
templates = Jinja2Templates(directory="templates")

users_db = []

@app.get("/", response_class=HTMLResponse)
def pagina_cadastro(request: Request):
    return templates.TemplateResponse(request=request, name="cadastro.html")

class Usuario:
    def __init__(self, username: str, senha: str, bio: str):
        self.username = username
        self.senha = senha
        self.bio = bio

@app.get("/login", response_class=HTMLResponse)
def pagina_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

from pydantic import BaseModel

class UsuarioInput(BaseModel):
    username: str
    senha: str
    bio: str

@app.post("/users")
def criar_usuario(dados: UsuarioInput):

    for u in users_db:
        if u.username == dados.username:
            raise HTTPException(status_code=400, detail="Usuário já existe")

    novo_usuario = Usuario(dados.username, dados.senha, dados.bio)

    users_db.append(novo_usuario)
    
    return {"message": "Usuário criado com sucesso!"}


@app.post("/login")
def fazer_login(dados: UsuarioInput, response: Response):
    usuario_encontrado = None
    for u in users_db:
        if u.username == dados.username:
            usuario_encontrado = u
            break
    
    if not usuario_encontrado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if (usuario_encontrado.senha != dados.senha):
        raise HTTPException(status_code=401, detail="Senha incorreta")
    
    response.set_cookie(key="session_user", value=usuario_encontrado.username)
    
    return {"message": "Logado com sucesso!"}

def get_active_user(session_user: Annotated[str | None, Cookie()] = None):
    if not session_user:
        raise HTTPException(status_code=401, detail="Não está logado")

    user = next((u for u in users_db if u.username == session_user), None)
    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida")

    return user

@app.get("/home", response_class=HTMLResponse)
def home(request: Request, user = Depends(get_active_user)):
    return templates.TemplateResponse(
        request=request,
        name="perfil.html",
        context={"username": user.username, "bio": user.bio}
    )