"""Collecteur — feedbacks de fin de session (CSV).

Source : fichiers CSV dans ``data/feedbacks/*.csv``.
Cible  : table ``feedbacks``.

Lancement :
    uv run python -m collect.feedbacks
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import text

from collect._common import (
    db_session,
    log,
)


class FeedbackPayload(BaseModel):
    """Schéma d'un feedback tel que présent dans les CSV d'export."""

    session_id: int = Field(ge=1)
    stagiaire_email: str | None = None
    date_saisie: date
    note_globale: int = Field(ge=1, le=5)
    commentaire: str | None = None
    source_csv: str

    @field_validator("stagiaire_email", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: object) -> object:
        return v if v != "" else None

    @field_validator("commentaire", mode="before")
    @classmethod
    def empty_comment_to_none(cls, v: object) -> object:
        return v if v != "" else None


def load_feedbacks() -> list[FeedbackPayload]:
    """Lit tous les CSV du dossier ``data/feedbacks/`` et valide via Pydantic.

    Les lignes invalides (note hors 1-5, champs manquants…) sont ignorées
    avec un log d'avertissement.
    """
    data_dir = Path(__file__).parent.parent / "data" / "feedbacks"
    if not data_dir.exists():
        raise FileNotFoundError(data_dir)

    items: list[FeedbackPayload] = []
    skipped = 0
    for csv_file in sorted(data_dir.glob("*.csv")):
        with csv_file.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                try:
                    items.append(
                        FeedbackPayload.model_validate(
                            {**row, "source_csv": csv_file.name}
                        )
                    )
                except Exception:
                    skipped += 1

    log.info("collect.feedbacks.loaded", count=len(items), skipped=skipped)
    return items


def upsert_feedbacks(session, feedbacks_payload: list[FeedbackPayload]) -> int:
    """Upsert idempotent — clé naturelle : ``(session_id, stagiaire_email, date_saisie)``."""
    inserted = 0
    for f in feedbacks_payload:
        result = session.execute(
            text(
                """
                INSERT INTO feedbacks (
                    session_id, stagiaire_email, date_saisie,
                    note_globale, commentaire, source_csv
                )
                VALUES (
                    :session_id, :stagiaire_email, :date_saisie,
                    :note_globale, :commentaire, :source_csv
                )
                ON CONFLICT (session_id, stagiaire_email, date_saisie) DO UPDATE
                  SET note_globale   = EXCLUDED.note_globale,
                      commentaire    = EXCLUDED.commentaire,
                      source_csv     = EXCLUDED.source_csv
                """
            ),
            f.model_dump(),
        )
        inserted += result.rowcount or 0
    return inserted


def run() -> None:
    log.info("collect.feedbacks.start")
    feedbacks_payload = load_feedbacks()
    with db_session() as session:
        nb = upsert_feedbacks(session, feedbacks_payload)
    log.info("collect.feedbacks.done", count=nb)


if __name__ == "__main__":
    run()
