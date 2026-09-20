# TradeVision AI Online V2

## Avvio
1. Installa Python 3.11+
2. `pip install -r requirements.txt`
3. Imposta `GEMINI_API_KEY`
4. `streamlit run app.py`

## Online
Puoi pubblicare questa cartella su un hosting compatibile con Streamlit.
La chiave API va inserita nelle **Secrets/Environment Variables del server**, NON nel codice e NON nel browser.

## Funzioni
- Screenshot TradingView
- Analisi Gemini server-side
- COMPRARE / VENDERE / ATTENDERE
- Entry, SL, TP1, TP2
- Trend, pattern, supporti/resistenze
- Qualità dei dati
- Interfaccia responsive per Z Fold 7

Il sistema non usa più un fallback casuale: se l'AI non è configurata o fallisce, mostra un errore.
