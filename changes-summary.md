# Synthèse des changements

---

### Problème : la migration `005` crée un index sur la table `contrats` qui n'existe pas encore.
**Correction :** Ajout d'une migration `004` pour créer la table `contrats`.

---

### Problème : Le seed qui insérait des contrats ne fonctionnait pas sans les collecteurs (dépendance aux clients).
**Corrections :**
- Suppression totale du seed d'insertion des contrats, inutilisable sans les collecteurs.
- Ajout d'un collecteur pour les contrats (chargement depuis le fichier `contrats.json`) afin d'intégrer l'ensemble des données via le pipeline.

---

### Problème : L'ingestion des feedbacks depuis des fichiers CSV n'était pas branchée.
**Correction :** Implémentation du collecteur de feedbacks (chargement depuis les fichiers CSV).

---

### Problème : Plusieurs requêtes dans `queries/` étaient incomplètes ou incorrectes (`contrats_actifs.sql`, `stagiaires_par_session.sql`, `feedbacks_recents.sql`). Problèmes de jointures, de groupements et d'intervalles.
**Correction :** Correction et finalisation des requêtes SQL concernées.

---

### Problème : Le tool `query_feedbacks` n'était pas branché.
**Correction :** Correction et connexion du tool `query_feedbacks` avec l’agent.

---

### Problème : Le tool `query_db` n'avait pas de description rendant son usage peu clair.
**Correction :** Ajout d'une docstring descriptive au tool `query_db`.

---

### Problème : Le system prompt divulguait des informations sensibles à l'utilisateur.
**Correction :** Ajustement du prompt système pour ne plus mentionner de noms de fonctions ou de tables.

---
