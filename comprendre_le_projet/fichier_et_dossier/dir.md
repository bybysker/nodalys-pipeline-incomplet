# Carte du projet

## collect/

Collecteurs HTTP (httpx) : appelle l'API Nodalys, insère sessions/stagiaires/feedbacks en base.

## queries/

Requêtes SQL exposées à l'agent. Certaines sont incomplète

## assistant/

Agent LangChain + outils. Les outils appellent `queries/` pour répondre aux questions en langage naturel.

## migrations/

Schéma Alembic (versioning de la BDD PostgreSQL).

## mock_api/

Fausse API Nodalys (FastAPI) — remplace la prod le temps que l'accès soit ouvert.

## data/

Fixtures initiales : `contrats.json` + CSV feedbacks trimestriels.

## scripts/ + seed.py

`seed.py` charge les fixtures en base. `scripts/` contient les scripts ponctuels (ingest, chat…).

## docs/

Mémo RGPD — ce qui ne doit pas aller en base.

## tests/

Pas été voir
