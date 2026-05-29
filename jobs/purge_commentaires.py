"""Job RGPD — purge des commentaires libres à J+30.

Tout commentaire libre est purgé 30 jours après la fin de session car il
peut contenir des informations ré-identifiantes (noms de managers, prénoms
tiers, etc.).

Lancement :
    uv run python -m jobs.purge_commentaires
"""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import text

from collect._common import db_session, log

DELAI_PURGE_JOURS = 30  # conformité RGPD : mémo DPO §feedbacks anonymisés


def run() -> None:
    log.info("jobs.purge_commentaires.start")

    seuil = date.today() - timedelta(days=DELAI_PURGE_JOURS)  # conformité RGPD

    with db_session() as session:
        result = session.execute(
            text(
                """
                UPDATE feedbacks
                SET commentaire = NULL          -- conformité RGPD
                FROM sessions s
                WHERE s.id = feedbacks.session_id
                  AND s.date_fin <= :seuil      -- conformité RGPD
                  AND feedbacks.commentaire IS NOT NULL
                """
            ),
            {"seuil": seuil},
        )
        nb = result.rowcount or 0 # l'erreur est juste pas de soucis

    log.info("jobs.purge_commentaires.done", purges=nb)


if __name__ == "__main__":
    run()
