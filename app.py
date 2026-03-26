import streamlit as st
import datetime
import uuid
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="CyberMetric Hub v2.1",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- ESTILOS CYBERPUNK / GLASSMORPHISM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');

    :root {
        --neon-cyan: #00f3ff;
        --neon-magenta: #ff00ff;
        --neon-yellow: #f3ff00;
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
    }

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

    .neon-border-magenta { border-top: 3px solid var(--neon-magenta); }
    .neon-border-yellow { border-top: 3px solid var(--neon-yellow); }

    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: var(--neon-cyan);
    }

    .stButton>button {
        width: 100%;
        background: transparent !important;
        color: var(--neon-cyan) !important;
        border: 1px solid var(--neon-cyan) !important;
        border-radius: 5px;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
    }

    .stButton>button:hover {
        background: var(--neon-cyan) !important;
        color: black !important;
        box-shadow: 0 0 20px var(--neon-cyan);
    }

    .highlight-box {
        background: rgba(0, 243, 255, 0.1);
        border: 1px dashed var(--neon-cyan);
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin: 10px 0;
    }

    .kpi-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--glass-border);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
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
    def calculate(self, students_data: List[Dict]) -> Tuple[MeasurementResult, Dict]:
        results = []
        for s in students_data:
            avg = sum(s['grades']) / 3
            results.append({
                "name": s['name'],
                "avg": round(avg, 2),
                "status": "Aprobado" if avg >= 3.0 else "Reprobado"
            })
        
        # Sort to find highest
        sorted_res = sorted(results, key=lambda x: x['avg'], reverse=True)
        top = sorted_res[0]
        
        return MeasurementResult(
            f"Top Student: {top['name']}",
            top['avg'],
            {"details": results, "count": len(students_data)}
        ), top

class ChronoCalculator(BaseCalculator):
    def calculate(self, dob: datetime.date) -> MeasurementResult:
        today = datetime.date.today()
        
        # Months
        months = (today.year - dob.year) * 12 + today.month - dob.month
        
        # Days
        delta = today - dob
        total_days = delta.days
        
        # Saturdays (5 is Saturday in ISO weekday mapping where Mon=1, Sun=7? No, .weekday() Mon=0, Sun=6. Sat=5)
        # We find how many Saturdays between dob and today.
        # Quick mathematical estimation: total_days // 7 + 1 if check start/end
        # Accurate:
        num_saturdays = sum(1 for i in range(total_days + 1) if (dob + datetime.timedelta(days=i)).weekday() == 5)
        
        return MeasurementResult(
            "Life Summary",
            float(total_days),
            {
                "months": months,
                "days": total_days,
                "saturdays": num_saturdays,
                "birth": str(dob)
            }
        )

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
            "Status": res.category,
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
        st.info("No data in the ledger. Initialize modules to generate blocks.")
        return

    cols = st.columns(4)
    cols[0].metric("TOTAL BLOCKS", len(df))
    cols[1].metric("MODULES IN USE", df["Module"].nunique())
    
    # Trends Chart
    fig = px.area(df.sort_values("Timestamp"), x="Timestamp", y="Metric", color="Module", 
                  title="RED DE MÉTRICAS ACTIVAS", color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

def view_module_academic(ledger: LedgerManager):
    st.markdown("## 🎓 ACADÉMICO - GRUPO COLABORATIVO")
    
    st.markdown('<div class="glass-card neon-border-magenta">', unsafe_allow_html=True)
    st.write("Ingrese las 3 notas para cada uno de los 4 estudiantes:")
    
    students_input = []
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            st.markdown(f"**Estudiante {i+1}**")
            name = st.text_input(f"Nombre E{i+1}", f"Estudiante_{i+1}", key=f"name_{i}")
            n1 = st.number_input(f"Nota 1 (E{i+1})", 0.0, 5.0, 3.0, key=f"n1_{i}")
            n2 = st.number_input(f"Nota 2 (E{i+1})", 0.0, 5.0, 3.0, key=f"n2_{i}")
            n3 = st.number_input(f"Nota 3 (E{i+1})", 0.0, 5.0, 3.0, key=f"n3_{i}")
            students_input.append({"name": name, "grades": [n1, n2, n3]})
    
    if st.button("PROCESAR ESTADÍSTICAS DEL GRUPO"):
        calc = AcademicCalculator()
        res, top = calc.calculate(students_input)
        ledger.add(res, "ACADEMIC")
        
        st.markdown(f"""
            <div class="highlight-box">
                <h2 style="color:var(--neon-yellow); margin:0;">🥇 GANADOR: {top['name']}</h2>
                <h3 style="color:white; margin:0;">PROMEDIO: {top['avg']}</h3>
            </div>
        """, unsafe_allow_html=True)
        st.balloons()
    st.markdown('</div>', unsafe_allow_html=True)

    # Detailed Table
    df_a = ledger.get_df("ACADEMIC")
    if not df_a.empty:
        st.markdown("### HISTORIAL DE REPORTES GRUPALES")
        st.dataframe(df_a[["ID", "Timestamp", "Status", "Metric"]], use_container_width=True)

def view_module_chrono(ledger: LedgerManager):
    st.markdown("## 🕰️ CRONO-LOG AVANZADO")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="glass-card neon-border-yellow">', unsafe_allow_html=True)
        dob = st.date_input("Fecha de Nacimiento", value=datetime.date(2000, 1, 1), 
                            min_value=datetime.date(1960, 1, 1), max_value=datetime.date.today())
        
        if st.button("EJECUTAR ANÁLISIS TEMPORAL"):
            calc = ChronoCalculator()
            res = calc.calculate(dob)
            ledger.add(res, "CHRONO")
            
            # Show results in tiles
            r_months = res.metadata["months"]
            r_days = res.metadata["days"]
            r_sats = res.metadata["saturdays"]
            
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 20px;">
                <div class="kpi-card"><p>MESES</p><h2 style="color:var(--neon-cyan);">{r_months}</h2></div>
                <div class="kpi-card"><p>DÍAS</p><h2 style="color:var(--neon-magenta);">{r_days}</h2></div>
            </div>
            <div class="kpi-card" style="margin-top:10px; border-color:var(--neon-yellow);">
                <p>SÁBADOS VIVIDOS</p><h1 style="color:var(--neon-yellow);">{r_sats}</h1>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### HISTORIAL CRONO")
        df_c = ledger.get_df("CHRONO")
        if not df_c.empty:
            st.dataframe(df_c[["ID", "Timestamp", "months", "days", "saturdays"]], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def view_module_bmi(ledger: LedgerManager):
    st.markdown("## 🏃 BIO-METRICO (IMC)")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        w = st.number_input("Peso (kg)", 1.0, 300.0, 70.0)
        h = st.number_input("Estatura (m)", 0.5, 2.5, 1.75)
        if st.button("CALCULAR"):
            calc = BMICalculator()
            res = calc.calculate(w, h)
            ledger.add(res, "BIO-METRIC")
            st.success(f"IMC: {res.value} - {res.category}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        df_m = ledger.get_df("BIO-METRIC")
        if not df_m.empty:
            st.dataframe(df_m[["ID", "Timestamp", "Status", "Metric"]], use_container_width=True)

# --- MAIN RUNNER ---

def main():
    ledger = LedgerManager()
    
    with st.sidebar:
        st.markdown('<div class="sidebar-title">🧬 CYBER NAV v2.1</div>', unsafe_allow_html=True)
        choice = st.radio("SISTEMA DE CONTROL", 
                         ["🏠 Dashboard", "🏃 Bio-Metric", "🎓 Académico", "🕰️ Crono-Log"],
                         index=0)
        st.markdown("<br><hr>", unsafe_allow_html=True)
        st.image("https://img.icons8.com/neon/96/shield.png", width=50)
        st.caption("BLOCKCHAIN-SDK v12.5.0")

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
