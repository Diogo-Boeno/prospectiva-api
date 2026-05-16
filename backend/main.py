import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="FollowUp SaaS", version="0.1")

# CORS liberado para dev local
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
    conn.row_factory = sqlite3.Row  # retorna dicts em vez de tuplas
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contatos (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            nome             TEXT    NOT NULL,
            empresa          TEXT    NOT NULL,
            proximo_contato  TEXT    NOT NULL,   -- data no formato YYYY-MM-DD
            criado_em        TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# Roda ao iniciar o servidor
init_db()


# ──────────────────────────────────────────
# Schemas (validação automática)
# ──────────────────────────────────────────

class ContatoCreate(BaseModel):
    nome: str
    empresa: str
    proximo_contato: str   # ex: "2025-06-01"

class ContatoResponse(ContatoCreate):
    id: int
    criado_em: str


# ──────────────────────────────────────────
# Rotas
# ──────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "FollowUp SaaS rodando ✅"}


@app.post("/contatos", response_model=ContatoResponse, status_code=201)
def criar_contato(body: ContatoCreate):
    """Cria um novo contato com data de próximo follow-up."""

    # Valida formato de data simples
    try:
        datetime.strptime(body.proximo_contato, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="proximo_contato deve estar no formato YYYY-MM-DD"
        )

    criado_em = datetime.utcnow().isoformat()

    conn = get_db()
    cursor = conn.execute(
        """
        INSERT INTO contatos (nome, empresa, proximo_contato, criado_em)
        VALUES (?, ?, ?, ?)
        """,
        (body.nome, body.empresa, body.proximo_contato, criado_em),
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()

    return ContatoResponse(
        id=novo_id,
        nome=body.nome,
        empresa=body.empresa,
        proximo_contato=body.proximo_contato,
        criado_em=criado_em,
    )


@app.get("/contatos", response_model=list[ContatoResponse])
def listar_contatos():
    """Lista todos os contatos ordenados por data de follow-up."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM contatos ORDER BY proximo_contato ASC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/contatos/hoje")
def contatos_hoje():
    """Retorna contatos cujo follow-up é hoje — útil para notificações."""
    hoje = datetime.utcnow().strftime("%Y-%m-%d")
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM contatos WHERE proximo_contato = ?", (hoje,)
    ).fetchall()
    conn.close()
    return {"data": hoje, "total": len(rows), "contatos": [dict(r) for r in rows]}