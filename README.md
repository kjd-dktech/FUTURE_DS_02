# 📊 Customer Retention & Churn Analysis (SaaS / Télécom)

## Contexte Métier
Dans un modèle d'abonnement (SaaS / Télécom), l'acquisition d'un nouveau client coûte beaucoup plus cher que sa rétention. <br>
L'objectif de ce projet est d'analyser le comportement d'une base de clients télécoms (~7000 observations) afin d'identifier les leviers majeurs de l'attrition ("Churn") et d'établir un plan de redressement actionnable.

## Impact Financier & Découvertes Clés
L'analyse exploratoire a mis en exergue les points de friction critiques suivants :
- **Hémorragie Financière :** Taux de Churn de **26.5%**, représentant une perte sèche de **139 000 $ de MRR** (Revenu Mensuel Récurrent).
- **Le Paradoxe de la Fibre Optique :** Produit Premium le plus cher, mais générant le plus de départs (42%). En cause : une prestation sans accès systématique au support technique.
- **Risque d'Onboarding :** Près de la moitié (47%) des résiliations interviennent durant les **12 premiers mois**. L'effort de fidélisation doit être précoce.
- **Effet d'Enfermement (Vendor Lock-in) :** Un client souscrivant à de multiples services de l'écosystème voit sa probabilité de fuite s'effondrer (de 52% à moins de 10%).

## Architecture du Projet
- `app/` : Dashboard analytique développé sous Streamlit (Restitution C-Level). Disponible sur [*mayal-telcochurn.streamlit.app*](mayal-telcochurn.streamlit.app)
- `notebook/` : Exploratory Data Analysis (EDA) et démarche analytique.
- `src/` : Pipeline de nettoyage et de feature engineering reproductible.
- `data/` : Données brutes et optimisées pour le Dashboard.

<br>

---

Kodjo Jean DEGBEVI — [LinkedIn](https://www.linkedin.com/in/kodjo-jean-degbevi-ba5170369) — [GitHub](https://github.com/kjd-dktech) — [Portfolio](https://mayal.tech)
