import streamlit as st
import datetime
import uuid
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="CyberMetric Hub v2.0",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- ESTILOS CYBERPUNK / GLASSMORPHISM (V2) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');

    :root {
        --neon-cyan: #00f3ff;
        --neon-magenta: #ff00ff;
        --bg-dark: #0a0b1e;
        --glass-bg: rgba(255, 255, 255, 0.05);
        --glass-border: rgba(255, 255, 255, 0.1);
    }

    .stApp {
        background: radial-gradient(circle at 50% 50%, #1a1b3a 0%, #0a0b1e 100%);
        color: white;
        font-family: 'Rajdhani', sans-serif;
        overflow-x: hidden;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: rgba(10, 11, 30, 0.95) !important;
        border-right: 1px solid var(--neon-cyan);
        backdrop-filter: blur(15px);
    }

    .sidebar-title {
        font-family: 'Orbitron', sans-serif;
        color: var(--neon-cyan);
        text-align: center;
        padding: 20px 0;
        border-bottom: 1px solid var(--glass-border);
        margin-bottom: 20px;
    }

    /* Glassmorphism Containers */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s ease;
    }

    .glass-card:hover {
        border-color: var(--neon-cyan);
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
    }

    .neon-border-cyan { border-left: 5px solid var(--neon-cyan); }
    .neon-border-magenta { border-left: 5px solid var(--neon-magenta); }

    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: var(--neon-cyan);
        text-shadow: 0 0 10px rgba(0, 243, 255, 0.5);
    }

    /* Custom Buttons */
    .stButton>button {
        width: 100%;
        background: transparent !important;
        color: var(--neon-cyan) !important;
        border: 1px solid var(--neon-cyan) !important;
        border-radius: 5px;
        padding: 8px 20px;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        background: var(--neon-cyan) !important;
        color: black !important;
        box-shadow: 0 0 20px var(--neon-cyan);
    }

    /* KPI Cards */
    .kpi-container {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 25px;
        flex-wrap: wrap;
    }

    .kpi-card {
        flex: 1;
        min-width: 200px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--glass-border);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }

    .kpi-value {
        font-size: 2rem;
        font-family: 'Orbitron';
        color: var(--neon-magenta);
    }

    /* Responsive */
    @media (max-width: 768px) {
        .glass-card { padding: 15px; }
        h1 { font-size: 1.8rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- MODELS & LOGIC (SOLID) ---

class MeasurementResult:
    def __init__(self, category: str, value: float, metadata: Dict):
        self.id = str(uuid.uuid4())[:8]
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.category = category
        self.value = value
        self.metadata = metadata

class BaseCalculator(ABC):
    @abstractmethod
    def calculate(self, *args, **kwargs) -> MeasurementResult:
        pass

class BMICalculator(BaseCalculator):
    def calculate(self, weight: float, height: float) -> MeasurementResult:
        bmi = weight / (height ** 2)
        if bmi < 18.5: cat = "Bajo Peso"
        elif 18.5 <= bmi < 25: cat = "Normal"
        elif 25 <= bmi < 30: cat = "Sobrepeso"
        else: cat = "Obesidad"
        return MeasurementResult(cat, round(bmi, 2), {"input": f"{weight}kg/{height}m"})

class AcademicCalculator(BaseCalculator):
    def calculate(self, name: str, grades: List[float]) -> MeasurementResult:
        avg = sum(grades) / len(grades)
        status = "Aprobado" if avg >= 3.0 else "Reprobado"
        return MeasurementResult(status, round(avg, 2), {"student": name})

class ChronoCalculator(BaseCalculator):
    def calculate(self, dob: datetime.date) -> MeasurementResult:
        diff = (datetime.date.today().year - dob.year) * 12 + datetime.date.today().month - dob.month
        return MeasurementResult("Life Duration", float(diff), {"birth": str(dob)})

# --- STATE MANAGER (LEDGER) ---

class LedgerManager:
    def __init__(self):
        if 'ledger' not in st.session_state:
            st.session_state.ledger = []
    
    def add(self, res: MeasurementResult, module: str):
        st.session_state.ledger.insert(0, {
            "ID": res.id,
            "Timestamp": res.timestamp,
            "Module": module,
            "Status/Value": res.category,
            "Metric": res.value,
            **res.metadata
        })
    
    def get_df(self, module: Optional[str] = None):
        if not st.session_state.ledger: return pd.DataFrame()
        df = pd.DataFrame(st.session_state.ledger)
        if module:
            return df[df["Module"] == module]
        return df

# --- UI VIEWS ---

def view_dashboard(ledger: LedgerManager):
    st.markdown("## 📊 SYSTEM DASHBOARD")
    df = ledger.get_df()
    
    if df.empty:
        st.info("No data in the ledger yet. Start by using any module on the sidebar!")
        return

    # KPI Layout
    kpis = st.columns(4)
    with kpis[0]:
        st.markdown(f'<div class="kpi-card"><p>TOTAL BLOCKS</p><div class="kpi-value">{len(df)}</div></div>', unsafe_allow_html=True)
    with kpis[1]:
        avg_bmi = df[df["Module"] == "BIO-METRIC"]["Metric"].mean()
        st.markdown(f'<div class="kpi-card"><p>AVG BMI</p><div class="kpi-value">{round(avg_bmi,1) if not pd.isna(avg_bmi) else "0"}</div></div>', unsafe_allow_html=True)
    with kpis[2]:
        avg_pts = df[df["Module"] == "ACADEMIC"]["Metric"].mean()
        st.markdown(f'<div class="kpi-card"><p>GRADES AVG</p><div class="kpi-value">{round(avg_pts,1) if not pd.isna(avg_pts) else "0"}</div></div>', unsafe_allow_html=True)
    with kpis[3]:
        max_months = df[df["Module"] == "CHRONO"]["Metric"].max()
        st.markdown(f'<div class="kpi-card"><p>MAX MONTHS</p><div class="kpi-value">{int(max_months) if not pd.isna(max_months) else "0"}</div></div>', unsafe_allow_html=True)

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_pie = px.pie(df, names="Module", title="DISTRIBUCIÓN DE REGISTROS", color_discrete_sequence=px.colors.sequential.Electric)
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_line = px.line(df.sort_values("Timestamp"), x="Timestamp", y="Metric", color="Module", title="TENDENCIA DE MÉTRICAS", markers=True)
        fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def view_module_bmi(ledger: LedgerManager):
    st.markdown("## 🏃 BIO-METRICO (IMC)")
    
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown('<div class="glass-card neon-border-cyan">', unsafe_allow_html=True)
            w = st.number_input("Peso (kg)", 1.0, 300.0, 70.0)
            h = st.number_input("Estatura (m)", 0.5, 2.5, 1.75)
            if st.button("CALCULAR E INDEXAR"):
                calc = BMICalculator()
                res = calc.calculate(w, h)
                ledger.add(res, "BIO-METRIC")
                st.balloons()
                st.success(f"BLOCK {res.id} GENERATED: {res.category} ({res.value})")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### HISTORIAL FILTRADO")
            df_m = ledger.get_df("BIO-METRIC")
            if not df_m.empty:
                st.dataframe(df_m[["ID", "Timestamp", "Status/Value", "Metric"]], use_container_width=True)
            else:
                st.write("Sin registros en este módulo.")
            st.markdown('</div>', unsafe_allow_html=True)

def view_module_academic(ledger: LedgerManager):
    st.markdown("## 🎓 ACADÉMICO")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="glass-card neon-border-magenta">', unsafe_allow_html=True)
        name = st.text_input("ID del Estudiante", "USER_0x1")
        g1 = st.slider("Nota Parcial 1", 0.0, 5.0, 3.5)
        g2 = st.slider("Nota Parcial 2", 0.0, 5.0, 4.0)
        g3 = st.slider("Examen Final", 0.0, 5.0, 2.5)
        if st.button("CALCULAR PROMEDIO"):
            calc = AcademicCalculator()
            res = calc.calculate(name, [g1, g2, g3])
            ledger.add(res, "ACADEMIC")
            st.toast(f"Student: {res.category} with {res.value}", icon='🎓')
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### HISTORIAL ACADÉMICO")
        df_a = ledger.get_df("ACADEMIC")
        if not df_a.empty:
            st.dataframe(df_a[["ID", "Timestamp", "Status/Value", "Metric", "student"]], use_container_width=True)
        else:
            st.write("Esperando datos...")
        st.markdown('</div>', unsafe_allow_html=True)

def view_module_chrono(ledger: LedgerManager):
    st.markdown("## 🕰️ CRONO-LOG")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        dob = st.date_input("Fecha de Nacimiento", value=datetime.date(2000, 1, 1), 
                            min_value=datetime.date(1960, 1, 1), max_value=datetime.date.today())
        if st.button("ANALIZAR TIEMPO"):
            calc = ChronoCalculator()
            res = calc.calculate(dob)
            ledger.add(res, "CHRONO")
            st.success(f"Total meses en la red: {int(res.value)}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### HISTORIAL CRONO")
        df_c = ledger.get_df("CHRONO")
        if not df_c.empty:
            st.dataframe(df_c[["ID", "Timestamp", "Metric", "birth"]], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN RUNNER ---

def main():
    ledger = LedgerManager()
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-title">🧬 CYBER NAV v2</div>', unsafe_allow_html=True)
        choice = st.radio("MÓDULOS DE RED", 
                         ["🏠 Dashboard", "🏃 Bio-Metric", "🎓 Académico", "🕰️ Crono-Log"],
                         index=0)
        
        st.markdown("<br><hr>", unsafe_allow_html=True)
        st.caption("BLOCKCHAIN-SDK v12.4.0 (SIMULATED)")

    # Routing
    if choice == "🏠 Dashboard":
        view_dashboard(ledger)
    elif choice == "🏃 Bio-Metric":
        view_module_bmi(ledger)
    elif choice == "🎓 Académico":
        view_module_academic(ledger)
    elif choice == "🕰️ Crono-Log":
        view_module_chrono(ledger)

if __name__ == "__main__":
    main()
