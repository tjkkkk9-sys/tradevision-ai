
import os, json, re, base64
from io import BytesIO
import requests
import streamlit as st
from PIL import Image

st.set_page_config(page_title="TradeVision AI", page_icon="📈", layout="wide")

MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

st.markdown("""
<style>
.block-container {max-width: 1200px; padding-top: 1rem;}
h1 {letter-spacing:-1px;}
@media (max-width: 700px) {
  .block-container {padding: .7rem .55rem;}
  h1 {font-size: 1.55rem;}
  .stButton button {width:100%; min-height:3rem;}
}
.signal {padding:18px;border-radius:18px;text-align:center;border:1px solid #333;background:#111;}
.buy {border-color:#00b894}.sell {border-color:#ff5252}.wait {border-color:#f0b429}
.metric {background:#111;border:1px solid #2b2b2b;border-radius:14px;padding:12px;margin:4px 0;}
.small {color:#aaa;font-size:.85rem}
</style>
""", unsafe_allow_html=True)

st.title("📈 TradeVision AI")
st.caption("Analisi di screenshot TradingView — versione online ottimizzata per smartphone / Z Fold 7")

with st.sidebar:
    st.header("Impostazioni")
    timeframe = st.selectbox("Timeframe", ["1m","5m","15m","30m","1H","4H","1D","1W"], index=4)
    market = st.selectbox("Mercato", ["Azioni","Indici","Forex","Crypto","Materie prime","Futures"], index=1)
    risk = st.number_input("Rischio per trade (%)", 0.1, 10.0, 1.0, 0.1)
    capital = st.number_input("Capitale", 0.0, 10000000.0, 5000.0, 100.0)
    st.divider()
    st.info("La chiave API non viene salvata nel browser. Configurala come variabile GEMINI_API_KEY nel servizio di hosting.")

uploaded = st.file_uploader("📸 Carica uno screenshot del grafico", type=["png","jpg","jpeg","webp"])

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    st.image(img, caption="Grafico da analizzare", use_container_width=True)

def clean_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)

def analyze(image_bytes, mime, timeframe, market):
    if not API_KEY:
        raise RuntimeError("GEMINI_API_KEY non configurata sul server.")
    prompt = f"""
Sei un analizzatore tecnico di grafici. Analizza SOLO ciò che è visibile nello screenshot.
Mercato: {market}. Timeframe: {timeframe}.
Non inventare prezzi, pattern o livelli non leggibili. Se un dato non è leggibile, usa "N/D".
Restituisci SOLO JSON valido con queste chiavi:
signal (uno tra COMPRARE, VENDERE, ATTENDERE),
confidence (0-100),
trend,
entry,
stopLoss,
tp1,
tp2,
rrRatio,
patterns (array),
resistances,
supports,
summary,
tradePlan,
invalidation,
dataQuality (ALTA, MEDIA, BASSA).
Il segnale è un'analisi informativa, non una garanzia di risultato.
"""
    b64 = base64.b64encode(image_bytes).decode()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    payload = {
        "contents":[{"role":"user","parts":[
            {"text":prompt},
            {"inlineData":{"mimeType":mime,"data":b64}}
        ]}],
        "generationConfig":{"responseMimeType":"application/json","temperature":0.1}
    }
    r = requests.post(url, json=payload, timeout=90)
    if not r.ok:
        raise RuntimeError(f"Gemini API {r.status_code}: {r.text[:500]}")
    data = r.json()
    txt = data["candidates"][0]["content"]["parts"][0]["text"]
    return clean_json(txt)

if uploaded and st.button("🚀 ANALIZZA GRAFICO", type="primary", use_container_width=True):
    with st.spinner("Analisi AI in corso..."):
        try:
            result = analyze(uploaded.getvalue(), uploaded.type, timeframe, market)
            st.session_state["result"] = result
        except Exception as e:
            st.error(str(e))
            st.stop()

result = st.session_state.get("result")
if result:
    signal = str(result.get("signal","ATTENDERE")).upper()
    cls = "buy" if "COMPRA" in signal else "sell" if "VEND" in signal else "wait"
    st.markdown(f'<div class="signal {cls}"><div class="small">SEGNALE AI</div><h2>{signal}</h2><b>Confidenza: {result.get("confidence","N/D")}%</b></div>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    for col, label, key in [(c1,"Entry","entry"),(c2,"Stop Loss","stopLoss"),(c3,"TP1","tp1"),(c4,"TP2","tp2")]:
        with col:
            st.markdown(f'<div class="metric"><div class="small">{label}</div><b>{result.get(key,"N/D")}</b></div>', unsafe_allow_html=True)
    st.write("**Trend:**", result.get("trend","N/D"))
    st.write("**R/R:**", result.get("rrRatio","N/D"))
    st.write("**Qualità dati:**", result.get("dataQuality","N/D"))
    st.subheader("Analisi")
    st.write(result.get("summary","N/D"))
    st.write("**Pattern:**", ", ".join(result.get("patterns",[])) if isinstance(result.get("patterns"),list) else result.get("patterns","N/D"))
    st.write("**Supporti:**", result.get("supports","N/D"))
    st.write("**Resistenze:**", result.get("resistances","N/D"))
    st.subheader("Piano")
    st.write(result.get("tradePlan","N/D"))
    st.warning("Invalidazione: " + str(result.get("invalidation","N/D")))
    st.caption("Il sistema non garantisce profitti. Verifica sempre il grafico e usa una gestione del rischio adeguata.")

st.divider()
st.caption("TradeVision AI Online V2 • Backend server-side • Nessun segnale casuale")
