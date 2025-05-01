SaaS Detection
=======================

Cette application permet de détecter les nouvelles applications SaaS utilisées par les membres d'une entreprise à l'aide de leurs données de navigation, en utilisant plusieurs sources de données (Crunchbase, Wikipedia, site web du SaaS) et en appliquant des heuristiques de correspondance de noms.

Elle doit permettre également d’identifier les changement de noms d’applications (ex : Facebook devient Meta) et d'éditeur.

L'objectif est de centraliser les données et de suivre l'évolution des SaaS dans une base de données fiable et à jour.

Table des matières
-------------------
- Fonctionnalités principales
- Architecture
- Installation
- Note Technique

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


# 📝 Note Technique

## 1. 👤 Utilisateurs cibles

**Cibles principales :**  
- **DSI**
- **Achats IT / Contrôle de gestion**
- **RSSI / Compliance**

**Typologie d’entreprise :** ETI / Grands comptes

**Objectifs :**  
- Monitorer les usages SaaS  
- Contrôler les coûts  
- Gérer les aspects de sécurité des données  

**Cas d’usage :**  
- Vue globale sur le parc SaaS de l’entreprise  
- Alertes sur les nouveaux outils détectés  
- Aide à la décision pour les achats IT  

---

## 2. 🛠️ Présentation de l’outil

L’outil exécute un **check programmé** (mensuel, hebdomadaire ou journalier) pour :

### A. Détection automatique de nouveaux SaaS
- Analyse des données de connexion utilisateurs
- Récupération des **URLs racines**
- Calcul de scores via des APIs (Wikipedia, Crunchbase, site web)
- Fusion des scores pour déterminer si l’outil est un SaaS
- Ajout automatique à la base si détection positive

### B. Détection de changements (nom ou éditeur)

**Hypothèses :**
- Pas besoin de checks temps réel (heure/seconde), décision prise à l’échelle de plusieurs jours
- Données d’entrée :  user_id, url, timestamp, duration
- les données de SaaS sont contenues dans une dict {root_url : {name, aliases, website} }

## 3. ⚙️ Fonctionnement détaillé

### A. Calcul des scores de détection

L’outil évalue plusieurs sources pour déterminer si une URL correspond à un SaaS :

#### a) Score Wikipedia
- Recherche d’une page Wikipédia liée à l’entreprise.
- Indice de confiance basé sur la présence de mots-clés.

#### b) Score Crunchbase
- Vérification de l’existence de la société sur Crunchbase.
- Analyse des tags.

#### c) Website Score

### Amélioration : chercher les pages “/login”, “/pricing”, “/signup”, et pas juste l’url root

---

## 4. 📈 KPIs à tracker

Voici les indicateurs clés pour mesurer et améliorer la performance du système :

- **Précision & Recall** de la détection  
  *(ex : annotations manuelles via une case à cocher dans l’extension web)*

- **Détail des scores utilisés**
  - Scores par source : Website, Crunchbase, Wikipedia

- **Corrélation des scores avec les détections correctes**
  - Permet d’ajuster dynamiquement la pondération du score global

- **Logs / erreurs**
  - Par exemple : sites inaccessibles (403, 404)  -> typiquement pour le calcul du Website Score

---

## 5. 🧠 Cas limites & pistes d’amélioration

### A. Fiabiliser le "SaaS Score"
- Intégrer de **nouvelles sources d’informations** :
  - LinkedIn, Clearbit, BuiltWith, Twitter
- Adapter dynamiquement les pondérations des scores de manière dynamique

### B. Intégration d’annotations manuelles
(Permet un apprentissage semi-supervisé du modèle de détection)

### C. Dashboard de visualisation
- **Liste des SaaS détectés** + métadonnées (éditeur, catégories…)
- **Données utilisateurs** :
  - Nombre de connexions
  - Durée moyenne par utilisateur / par SaaS
- **KPIs de détection** pour suivi opérationnel

### D. Architecture & structure technique

- **Lecture des données d’entrée :**
  - Dossier `/data`
    - `.csv` : fichier `URL_VISIT_DATA`
    - `.json` : dictionnaire SaaS existant

- **Écriture des sorties :**
  - Dossier `/output`
    - Dictionnaire SaaS mis à jour avec scores et timestamps

- **Logging :**
  - Intégration de `loggers` pour suivre toutes les étapes du pipeline

- **Traçabilité :**
  - Ajout de **dates de dernière mise à jour** dans chaque entrée du dictionnaire SaaS

