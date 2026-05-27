"""Seed des tables ``contrats`` (et clients/sessions au besoin).

À lancer APRÈS ``make migrate`` :
    uv run python seed.py

Le seed est idempotent : ON CONFLICT DO UPDATE sur l'id.
"""

import json
from pathlib import Path

from sqlalchemy import text

from collect._common import db_session, log


def seed_contrats():
    fixture = Path(__file__).parent / "data" / "contrats.json"
    if not fixture.exists():
        raise FileNotFoundError(fixture)
    contrats = json.loads(fixture.read_text(encoding="utf-8"))
    inserted = 0
    with db_session() as session:
        for c in contrats:
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
                      SET client_id = EXCLUDED.client_id,
                          session_id = EXCLUDED.session_id,
                          statut = EXCLUDED.statut,
                          montant_ht = EXCLUDED.montant_ht,
                          date_signature = EXCLUDED.date_signature
                    """
                ),
                c,
            )
            inserted += result.rowcount or 0
    log.info("seed.contrats.done", count=inserted)


if __name__ == "__main__":
    seed_contrats()
