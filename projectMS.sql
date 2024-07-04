SELECT SUM(prix * qte) AS le_chiffre_daffaires FROM ventes;
SELECT produit, SUM(prix * qte) AS ventes_par_produit FROM ventes GROUP BY produit;
SELECT region, SUM(qte) AS ventes_par_region FROM ventes GROUP BY region;