import yfinance as yf
import pandas as pd
import os
from typing import List, Dict
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

def get_current_data(tickers: List[str]) -> Dict:
    """Récupère les prix actuels et gère les devises."""
    results = {}
    if not tickers:
        return results
        
    try:
        # Récupérer le taux EUR/USD pour la conversion
        fx = yf.Ticker("EURUSD=X").history(period="1d")
        eur_usd = fx['Close'].iloc[-1] if not fx.empty else 1.08

        data = yf.download(tickers, period="5d", progress=False)
        
        for t in tickers:
            try:
                if isinstance(data.columns, pd.MultiIndex):
                    hist = data.xs(t, level='Ticker', axis=1)
                else:
                    hist = data
                
                hist = hist.dropna(subset=['Close'])
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    change_pct = ((current_price - prev_price) / prev_price) * 100
                    
                    currency = "EUR" if t.endswith(".PA") else "USD"
                    # Prix converti en EUR si c'est de l'USD
                    price_eur = current_price / eur_usd if currency == "USD" else current_price
                    
                    results[t] = {
                        "price": round(float(current_price), 2),
                        "price_eur": round(float(price_eur), 2),
                        "change_pct": round(float(change_pct), 2),
                        "currency": currency,
                        "longName": t,
                        "volatility": round(hist['Close'].pct_change().std() * 100, 2) # Volatilité simplifiée
                    }
                else:
                    results[t] = {"price": 0, "price_eur": 0, "change_pct": 0, "currency": "?", "longName": t, "volatility": 0}
            except Exception:
                results[t] = {"price": 0, "price_eur": 0, "change_pct": 0, "currency": "?", "longName": t, "volatility": 0}
    except Exception as e:
        print(f"Erreur globale download: {e}")
            
    return results

def get_historical_prices(ticker: str, period="1mo"):
    """Récupère l'historique pour les graphiques."""
    try:
        return yf.download(ticker, period=period, progress=False)
    except Exception:
        return pd.DataFrame()

def search_financial_news(query: str):
    """Recherche via Perplexity (Premium) ou Tavily (Standard)."""
    pplx_key = os.getenv("PERPLEXITY_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")

    # OPTION 1 : PERPLEXITY (Recherche intelligente & structurée)
    if pplx_key:
        try:
            import requests
            url = "https://api.perplexity.ai/chat/completions"
            payload = {
                "model": "sonar-pro", # Ou "sonar" selon les besoins
                "messages": [
                    {"role": "system", "content": "Tu es un analyste financier qui cherche des news précises et sourcées."},
                    {"role": "user", "content": f"Recherche les dernières actualités financières pour : {query}"}
                ],
                "max_tokens": 1000
            }
            headers = {
                "Authorization": f"Bearer {pplx_key}",
                "Content-Type": "application/json"
            }
            response = requests.post(url, json=payload, headers=headers)
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"Erreur Perplexity: {e}. Bascule sur Tavily...")

    # OPTION 2 : TAVILY (Moteur de recherche IA standard)
    if tavily_key:
        try:
            tavily = TavilyClient(api_key=tavily_key)
            search_result = tavily.search(query=f"financial news: {query}", search_depth="advanced", max_results=3)
            return str(search_result['results'])
        except Exception as e:
            print(f"Erreur Tavily: {e}")
            return "La recherche d'actualités est temporairement indisponible."
            
    return "Aucune clé API (Perplexity ou Tavily) n'est configurée pour la recherche web."

