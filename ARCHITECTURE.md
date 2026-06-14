# 🏗️ Architecture du Projet

Ce document détaille la structure technique pour faciliter la maintenance et l'évolution de l'assistant.

## 📁 Structure des Fichiers

### `src/app.py` (Interface Utilisateur)
- **Rôle** : Point d'entrée principal (Streamlit).
- **Logique** : Gère l'affichage des tableaux de bord, les graphiques Plotly et l'interface de chat. Il contient également les fonctions de mise à jour du fichier `portfolio.json`.

### `src/openai_agent.py` (Cerveau / Orchestrateur)
- **Rôle** : Gère la logique agentique via GPT-4o.
- **Concepts clés** : Utilise le **Function Calling**. L'IA a accès à une liste d'outils (`tools`) qu'elle appelle selon le besoin de l'utilisateur.
- **Outils inclus** : `get_portfolio_status`, `search_financial_news`, `deep_financial_analysis`.

### `src/gemini_agent.py` (Analyste de Fond)
- **Rôle** : Interface avec Google Gemini 1.5 Pro.
- **Usage** : Appelé spécifiquement pour des analyses nécessitant une grande fenêtre de contexte ou une réflexion fondamentale plus poussée.

### `src/data_fetch.py` (Moteur de Données)
- **Rôle** : Extraction des données brutes.
- **Fonctions** :
    - `get_current_data` : Prix et variations via `yfinance`.
    - `search_financial_news` : Recherche web via `tavily`.

### `src/portfolio.json` (Base de Données)
- **Rôle** : Stockage persistant de vos positions (Ticker, Quantité, Prix d'achat).

## 🔄 Flux de Données Typique
1. L'utilisateur pose une question dans `app.py`.
2. `openai_agent.py` reçoit la question et identifie les outils nécessaires.
3. L'agent appelle `data_fetch.py` pour les prix et les news.
4. Si la question est complexe, l'agent sollicite `gemini_agent.py`.
5. Une synthèse finale est renvoyée à l'interface.

## 🛠️ Maintenance
- **Ajouter un outil** : Créer la fonction dans `data_fetch.py` et la déclarer dans la liste `tools` de `openai_agent.py`.
- **Changer de modèle** : Modifier le paramètre `model` dans les appels de `openai_agent.py` ou `gemini_agent.py`.
