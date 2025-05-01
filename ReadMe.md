SaaS Detection
=======================

Cette application permet de détecter les nouvelles applications SaaS utilisées par les membres d'une entreprise à l'aide de leurs données de navigation, en utilisant plusieurs sources de données (Crunchbase, Wikipedia, site web du SaaS) et en appliquant des heuristiques de correspondance de noms.

Elle doit permettre également d’identifier les changement de noms d’applications (ex : Facebook devient Meta) et d'éditeur.

L'objectif est de centraliser les données et de suivre l'évolution des SaaS dans une base de données fiable et à jour.

Table des matières
-------------------
- Hypothèses
- Fonctionnalités principales
- Architecture
- Installation
- Utilisation
- Exemples
- Améliorations

Hypothèses
---------------------------
On suppose que l'on dispose de données de navigations d'utilisateurs d'une entreprise, contenant les user_ids, les urls visités, la date (et éventuellement la durée) de connexion.

Fonctionnalités principales
---------------------------
- Détection automatique des renommages : le système détecte les applications SaaS qui ont changé de nom, en comparant les domaines et les informations associées.
- Enrichissement des données : utilisation d'API (Crunchbase, Wikipedia) pour enrichir les informations de l'entreprise.
- Gestion des alias : permet de gérer les différentes versions d’un nom pour une même application (par exemple, Facebook → Meta).
- Historique des changements : garde une trace des anciens noms et des nouveaux noms pour chaque domaine identifié.
- Score de SaaS : calcule un score de probabilité qu'une URL soit un SaaS en se basant sur des mots-clés d’enrichissement et de contenu web.

Architecture
------------
Le projet repose sur une approche en 3 étapes :
1. Collecte de données : à partir de l'URL du domaine d’un SaaS, récupérer les informations liées à ce domaine (nom, URL, etc.).
2. Enrichissement des données : en utilisant les API Crunchbase, Wikipedia, et des mots-clés pour extraire des informations plus détaillées.
3. Analyse des changements de nom : détecter les changements de nom entre les différentes versions d’une application SaaS (via un identifiant unique comme le Crunchbase ID ou Wikipedia slug).

Installation
------------
1. Clonez le repository :
   ```bash
   git clone https://github.com/ShamRou/CasetStudyBeamy.git

2. Installez les dépendances :

   ```python
   pip install -r requirements.txt

3. Configuration de l'API : Assurez-vous d'avoir les clés d'API pour accéder aux services externes comme Crunchbase.


Améliorations
------------

## 1. Scoring

### A) Keywords
- Mots-clés SaaS présents dans le contenu des pages (login, pricing, free trial, etc.)

### B) Pages à visiter
- Page d’accueil
- Pages “/login”, “/pricing”, “/signup”

### C) Autres scores
- LinkedIn
- Clearbit
- BuiltWith
- Twitter


## 2. Données de test

- **URL_VISIT_DATA** : dataset représentatif sur 1 journée (URLs SaaS et non-SaaS)


## 3. KPIs

- **Précision & Recall** de la détection  
  - (ex : annotations manuelles via une case à cocher dans l’extension web)
- **Scores utilisés**  
  - Site Web, Crunchbase, Wikipedia
- **Corrélation** des scores avec les détections correctes  
  - Pour pondérer le score SaaS global
- **Logs / erreurs**  
  - Sites inaccessibles (ex : erreurs 403)

## 4. Front end

- **Liste des SaaS existants** et leurs métadonnées  
  - Alias, noms précédents
- **Données utilisateurs**  
  - Dashboard nombre et temps de connexion mensuel
- **KPIs** affichés en temps réel


## 5. Améliorations de code

- Ajouter des **loggers** pour tracer les différentes étapes
- Lire depuis le dossier `/data`  
  - (`.csv` URL_VISIT_DATA, `.json` SaaS dict)
- Écrire dans le dossier `/output`  
  - (dict mis à jour)
- Organiser les fonctions dans `identify_saas/`
- ruff pour le formatage 
