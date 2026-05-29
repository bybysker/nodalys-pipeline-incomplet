-- Nombre de contrats actifs par stagiaire — appelée par l'assistant
-- pour répondre à « avec qui avons-nous des contrats actifs ? ».

SELECT
    st.prenom,
    st.nom,
    COUNT(c.id) AS nb_contrats_actifs
FROM sessions s
JOIN stagiaires st ON st.session_id = s.id
JOIN contrats c on c.session_id = s.id
WHERE c.statut = 'actif'
GROUP BY st.prenom, st.nom
ORDER BY nb_contrats_actifs DESC;
