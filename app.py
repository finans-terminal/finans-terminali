dogus-finans-terminali
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from textblob import TextBlob
from datetime import datetime, timedelta

# Sayfa Ayarları
st.set_page_config(page_title="Doğuş Can Finans Terminali V2", layout="wide")

st.title("🚀 Profesyonel Finansal Analiz Terminali")
st.markdown("---")

# Yan Panel - Girişler
st.sidebar.header("⚙️ Analiz Ayarları")
ticker = st.sidebar.text_input("Hisse Sembolü (Örn: THYAO.IS, AAPL, BTC-USD)", "THYAO.IS")
period = st.sidebar.selectbox("Zaman Aralığı", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

# Veri Çekme
@st.cache_data
def get_data(symbol, p):
    df = yf.download(symbol, period=p)
    info = yf.Ticker(symbol).info
    return df, info

try:
    data, info = get_data(ticker, period)

    # Üst Bölüm: Özet Bilgiler
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Güncel Fiyat", f"{data['Close'].iloc[-1]:.2f}")
    with col2:
        change = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
        st.metric("Günlük Değişim", f"%{change:.2f}")
    with col3:
        st.metric("F/K Oranı", info.get('trailingPE', 'N/A'))
    with col4:
        st.metric("Temettü Verimi", f"%{info.get('dividendYield', 0)*100:.2f}")

    # Grafik Bölümü
    st.subheader(f"📈 {ticker} Teknik Analiz Grafiği")
    
    # Hareketli Ortalamalar Hesaplama
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    data['SMA50'] = data['Close'].rolling(window=50).mean()

    fig = go.Figure()
    # Mum Grafiği
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], 
                                low=data['Low'], close=data['Close'], name='Fiyat'))
    # SMA20 ve SMA50
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA20'], line=dict(color='orange', width=1), name='SMA 20'))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], line=dict(color='blue', width=1), name='SMA 50'))
    
    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # RSI Hesaplama ve Gösterimi
    st.subheader("📊 RSI (Göreceli Güç Endeksi)")
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=data.index, y=data['RSI'], line=dict(color='purple'), name='RSI'))
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
    fig_rsi.update_layout(height=250, template="plotly_dark")
    st.plotly_chart(fig_rsi, use_container_width=True)

    # Alt Bölüm: Haberler ve Temel Analiz
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("📰 Son Haber Analizi")
        news = yf.Ticker(ticker).news
        for item in news[:5]:
            sent = TextBlob(item['title']).sentiment.polarity
            mood = "🟢 Olumlu" if sent > 0 else "🔴 Olumsuz" if sent < 0 else "⚪ Nötr"
            st.write(f"**{item['title']}**")
            st.caption(f"Duygu: {mood} | Kaynak: {item['publisher']}")
            st.markdown("---")

    with c2:
        st.subheader("📊 Şirket Künyesi")
        summary_data = {
            "Metrik": ["Piyasa Değeri", "PD/DD", "Beta", "52 Haftalık Yüksek", "52 Haftalık Düşük"],
            "Değer": [
                f"{info.get('marketCap', 0):,}",
                info.get('priceToBook', 'N/A'),
                info.get('beta', 'N/A'),
                info.get('fiftyTwoWeekHigh', 'N/A'),
                info.get('fiftyTwoWeekLow', 'N/A')
            ]
        }
        st.table(pd.DataFrame(summary_data))

except Exception as e:
    st.error(f"Veri çekilirken bir hata oluştu: {e}")
