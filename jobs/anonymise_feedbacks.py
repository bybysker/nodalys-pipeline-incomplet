"""Job RGPD — anonymisation des feedbacks à J+180.

À J+180 après la fin de session, le champ ``stagiaire_email`` est remplacé
par un hash SHA-256 tronqué.

Lancement :
    uv run python -m jobs.anonymise_feedbacks
"""

from __future__ import annotations

import hashlib
from datetime import date, timedelta

from sqlalchemy import text

from collect._common import db_session, log

DELAI_ANONYMISATION_JOURS = 180  # conformité RGPD : mémo DPO §feedbacks anonymisés


def _hash_email(email: str) -> str:
    """SHA-256 tronqué à 16 caractères """
    return hashlib.sha256(email.encode()).hexdigest()[:16]  # conformité RGPD


def run() -> None:
    log.info("jobs.anonymise_feedbacks.start")

    seuil = date.today() - timedelta(days=DELAI_ANONYMISATION_JOURS)  # conformité RGPD

    with db_session() as session:
        # Récupère les feedbacks à anonymiser : session terminée depuis > 180 jours
        # et email non encore hashé (les hashs font exactement 16 chars)
        rows = session.execute(
            text(
                """
                SELECT f.id, f.stagiaire_email
                FROM feedbacks f
                JOIN sessions s ON s.id = f.session_id
                WHERE s.date_fin <= :seuil          -- conformité RGPD
                  AND f.stagiaire_email IS NOT NULL  -- conformité RGPD
                  AND length(f.stagiaire_email) > 16 -- déjà hashé si 16 chars
                """
            ),
            {"seuil": seuil},
        ).fetchall()

        nb = 0
        for row in rows:
            hashed = _hash_email(row.stagiaire_email)  # conformité RGPD
            session.execute(
                text(
                    "UPDATE feedbacks SET stagiaire_email = :hash WHERE id = :id"  # conformité RGPD
                ),
                {"hash": hashed, "id": row.id},
            )
            nb += 1

    log.info("jobs.anonymise_feedbacks.done", anonymises=nb)


if __name__ == "__main__":
    run()
