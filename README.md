# FollowUp SaaS — Backend v0.1

API para cadência de follow-up de SDRs.

## Setup (1x)

```bash
cd backend
pip install -r requirements.txt
```

## Rodar

```bash
uvicorn main:app --reload
```

Acesse: http://localhost:8000

Docs interativas: http://localhost:8000/docs

---

## Endpoints

| Método | Rota               | O que faz                              |
|--------|--------------------|----------------------------------------|
| GET    | `/`                | Health check                           |
| POST   | `/contatos`        | Cria contato com data de follow-up     |
| GET    | `/contatos`        | Lista todos os contatos                |
| GET    | `/contatos/hoje`   | Contatos com follow-up para hoje       |

---

## Exemplo de uso

### Criar contato
```bash
curl -X POST http://localhost:8000/contatos \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "empresa": "Empresa X",
    "proximo_contato": "2025-06-01"
  }'
```

### Resposta
```json
{
  "id": 1,
  "nome": "João Silva",
  "empresa": "Empresa X",
  "proximo_contato": "2025-06-01",
  "criado_em": "2025-05-15T10:00:00"
}
```