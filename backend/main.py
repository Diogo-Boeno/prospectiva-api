import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="FollowUp SaaS", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "followup.db"


# ──────────────────────────────────────────
# Banco de dados
# ──────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contatos (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            nome             TEXT    NOT NULL,
            empresa          TEXT    NOT NULL,
            proximo_contato  TEXT    NOT NULL,
            contexto         TEXT    NOT NULL DEFAULT '',
            criado_em        TEXT    NOT NULL
        )
    """)
    # migration segura: adiciona coluna se o banco já existia sem ela
    try:
        conn.execute("ALTER TABLE contatos ADD COLUMN contexto TEXT NOT NULL DEFAULT ''")
    except Exception:
        pass  # coluna já existe, tudo certo
    conn.commit()
    conn.close()


init_db()


# ──────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────

class ContatoCreate(BaseModel):
    nome: str
    empresa: str
    proximo_contato: str
    contexto: Optional[str] = ""

class ContatoResponse(ContatoCreate):
    id: int
    criado_em: str

class ContatoUpdate(BaseModel):
    proximo_contato: Optional[str] = None
    contexto: Optional[str] = None


# ──────────────────────────────────────────
# Rotas
# ──────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "FollowUp SaaS rodando ✅"}


@app.post("/contatos", response_model=ContatoResponse, status_code=201)
def criar_contato(body: ContatoCreate):
    try:
        datetime.strptime(body.proximo_contato, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=422, detail="proximo_contato deve estar no formato YYYY-MM-DD")

    criado_em = datetime.utcnow().isoformat()
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO contatos (nome, empresa, proximo_contato, contexto, criado_em) VALUES (?, ?, ?, ?, ?)",
        (body.nome, body.empresa, body.proximo_contato, body.contexto or "", criado_em),
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()

    return ContatoResponse(
        id=novo_id,
        nome=body.nome,
        empresa=body.empresa,
        proximo_contato=body.proximo_contato,
        contexto=body.contexto or "",
        criado_em=criado_em,
    )


@app.get("/contatos", response_model=list[ContatoResponse])
def listar_contatos():
    conn = get_db()
    rows = conn.execute("SELECT * FROM contatos ORDER BY proximo_contato ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.delete("/contatos/{id}", status_code=204)
def deletar_contato(id: int):
    conn = get_db()
    result = conn.execute("DELETE FROM contatos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Contato não encontrado")


@app.patch("/contatos/{id}", response_model=ContatoResponse)
def atualizar_contato(id: int, body: ContatoUpdate):
    if body.proximo_contato:
        try:
            datetime.strptime(body.proximo_contato, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=422, detail="proximo_contato deve estar no formato YYYY-MM-DD")

    conn = get_db()
    row = conn.execute("SELECT * FROM contatos WHERE id = ?", (id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    nova_data = body.proximo_contato or row["proximo_contato"]
    novo_contexto = body.contexto if body.contexto is not None else row["contexto"]

    conn.execute(
        "UPDATE contatos SET proximo_contato = ?, contexto = ? WHERE id = ?",
        (nova_data, novo_contexto, id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM contatos WHERE id = ?", (id,)).fetchone()
    conn.close()
    return dict(row)


@app.get("/contatos/hoje")
def contatos_hoje():
    hoje = datetime.utcnow().strftime("%Y-%m-%d")
    conn = get_db()
    rows = conn.execute("SELECT * FROM contatos WHERE proximo_contato = ?", (hoje,)).fetchall()
    conn.close()
    return {"data": hoje, "total": len(rows), "contatos": [dict(r) for r in rows]}