"""Collecteur — contrats de formation Nodalys.

Source : fichier JSON dans ``data/contrats.json``.
Cible  : table ``contrats``.

Lancement :
    uv run python -m collect.contrats
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field
import json
from pathlib import Path
from collect._common import (
    db_session,
    log,
)

class ContratPayload(BaseModel):
    """Schéma d'un contrat telle que la renvoie l'API Nodalys."""

    id: int
    client_id: int
    session_id: int = Field(ge=1)
    statut: str = Field(min_length=3, max_length=50)
    montant_ht: float = Field(ge=0)
    date_signature: date = Field(ge=date(2024, 1, 1))


def load_contracts() -> list[ContratPayload]:
    """Récupère les contrats depuis le fichier JSON et les valide avec pydantic"""
    
    fixture = Path(__file__).parent.parent / "data" / "contrats.json"
    if not fixture.exists():
        raise FileNotFoundError(fixture)
    contrats = json.loads(fixture.read_text(encoding="utf-8"))
    items = [ContratPayload.model_validate(item) for item in contrats]
    log.info("collect.contrats.loaded", count=len(items))
    return items

def upsert_contrats(session, contrats_payload: list[ContratPayload]) -> int:
    """Upsert idempotent — clé naturelle : ``id``."""
    from sqlalchemy import text

    inserted = 0
    for c in contrats_payload:
        result = session.execute(
            text(
                """
                INSERT INTO contrats (
                    id, client_id, session_id, statut, montant_ht, date_signature
                )
                VALUES (
                    :id, :client_id, :session_id, :statut, :montant_ht, :date_signature
                )
                ON CONFLICT (id) DO UPDATE
                  SET client_id       = EXCLUDED.client_id,
                      session_id      = EXCLUDED.session_id,
                      statut          = EXCLUDED.statut,
                      montant_ht      = EXCLUDED.montant_ht,
                      date_signature  = EXCLUDED.date_signature
                """
            ),
            c.model_dump(),
        )
        inserted += result.rowcount or 0
    return inserted


def run() -> None:
    """Lance la collecte des contrats."""
    contrats_payload = load_contracts()
    with db_session() as session:
        upsert_contrats(session, contrats_payload)
    log.info("collect.contrats.done", count=len(contrats_payload))

if __name__ == "__main__":
    run()
