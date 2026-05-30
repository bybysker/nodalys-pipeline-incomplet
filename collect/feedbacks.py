"""Collecteur — feedbacks de fin de session (CSV).

Source : fichiers CSV dans ``data/feedbacks/*.csv``.
Cible  : table ``feedbacks``.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from pydantic import BaseModel, Field
from sqlalchemy import text

from collect._common import (
    db_session,
    log,
)

FEEDBACKS_DIR = Path(__file__).parent.parent / "data" / "feedbacks"


class FeedbackPayload(BaseModel):
    session_id: int = Field(ge=1)
    stagiaire_email: str = Field(min_length=5, max_length=255)
    date_saisie: date
    note_globale: int = Field(ge=1, le=5)
    commentaire: str | None = Field(default=None, max_length=2000)
    source_csv: str = ""


def load_csv_feedbacks() -> list[FeedbackPayload]:
    feedbacks = []
    for csv_file in FEEDBACKS_DIR.glob("*.csv"):
        with csv_file.open(encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                try:
                    fb = FeedbackPayload.model_validate(row)
                    fb.source_csv = csv_file.name
                    feedbacks.append(fb)
                except Exception as e:
                    log.error("collect.feedbacks.validation_error", file=csv_file.name, error=str(e))
    log.info("collect.feedbacks.loaded", count=len(feedbacks))
    return feedbacks


def upsert_feedbacks(session, feedbacks: list[FeedbackPayload]) -> int:
    inserted = 0
    for fb in feedbacks:
        result = session.execute(
            text(
                """
                INSERT INTO feedbacks (
                    session_id, stagiaire_email, date_saisie, note_globale, commentaire, source_csv
                )
                VALUES (
                    :session_id, :stagiaire_email, :date_saisie, :note_globale, :commentaire, :source_csv
                )
                ON CONFLICT (session_id, stagiaire_email, date_saisie) DO UPDATE
                  SET note_globale = EXCLUDED.note_globale,
                      commentaire = EXCLUDED.commentaire,
                      source_csv = EXCLUDED.source_csv
                """
            ),
            fb.model_dump(),
        )
        inserted += result.rowcount or 0
    return inserted


def run() -> None:
    log.info("collect.feedbacks.start")
    feedbacks = load_csv_feedbacks()
    with db_session() as session:
        nb = upsert_feedbacks(session, feedbacks)
    log.info("collect.feedbacks.done", upserted=nb)


if __name__ == "__main__":
    run()
