import streamlit as st
import datetime
import uuid
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="CyberMetric Hub - Web3 Analytics",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- ESTILOS CYBERPUNK / GLASSMORPHISM ---
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
        background: transparent;
        color: var(--neon-cyan);
        border: 1px solid var(--neon-cyan);
        border-radius: 5px;
        padding: 10px 20px;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        transition: all 0.4s ease;
        text-transform: uppercase;
    }

    .stButton>button:hover {
        background: var(--neon-cyan);
        color: black;
        box-shadow: 0 0 20px var(--neon-cyan);
    }

    /* Hide Streamlit Header/Footer */
    header, footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }

    /* Blockchain List Styling */
    .block-item {
        font-size: 0.8rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding: 5px 0;
        font-family: 'Courier New', monospace;
    }
    
    .status-badge {
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        background: rgba(0, 243, 255, 0.1);
        color: var(--neon-cyan);
        border: 1px solid var(--neon-cyan);
    }
    /* Responsive Adjustments */
    @media (max-width: 768px) {
        .glass-card {
            padding: 15px;
            margin-bottom: 10px;
        }
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.4rem !important; }
    }

    /* Container Spacing */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 10px;
    }

    /* Prevent Scroll */
    .stApp {
        overflow-x: hidden;
    }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE NEGOCIO (SOLID PRINCIPLES) ---

class MeasurementResult:
    def __init__(self, category: str, value: float, metadata: Dict):
        self.id = str(uuid.uuid4())[:8]
        self.timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.category = category
        self.value = value
        self.metadata = metadata

class BaseCalculator(ABC):
    @abstractmethod
    def calculate(self, *args, **kwargs) -> MeasurementResult:
        pass

class BMICalculator(BaseCalculator):
    def calculate(self, weight: float, height: float) -> MeasurementResult:
        if height <= 0: return None
        bmi = weight / (height ** 2)
        
        if bmi < 18.5: category = "Bajo Peso"
        elif 18.5 <= bmi < 25: category = "Normal"
        elif 25 <= bmi < 30: category = "Sobrepeso"
        else: category = "Obesidad"
        
        return MeasurementResult(category, round(bmi, 2), {"input": f"{weight}kg, {height}m"})

class AcademicCalculator(BaseCalculator):
    def calculate(self, name: str, grades: List[float]) -> MeasurementResult:
        avg = sum(grades) / len(grades)
        status = "Aprobado" if avg >= 3.0 else "Reprobado"
        return MeasurementResult(status, round(avg, 2), {"student": name})

class ChronoCalculator(BaseCalculator):
    def calculate(self, birth_date: datetime.date) -> MeasurementResult:
        today = datetime.date.today()
        months = (today.year - birth_date.year) * 12 + today.month - birth_date.month
        return MeasurementResult("Tiempo de Vida", float(months), {"birth": str(birth_date)})

# --- BLOCKCHAIN SIMULATION (STATE MANAGEMENT) ---

class LedgerManager:
    def __init__(self):
        if 'ledger' not in st.session_state:
            st.session_state.ledger = []
    
    def add_entry(self, result: MeasurementResult, module_type: str):
        entry = {
            "hash": result.id,
            "timestamp": result.timestamp,
            "module": module_type,
            "metric": result.category,
            "value": result.value
        }
        st.session_state.ledger.insert(0, entry) # Newest first

# --- UI COMPONENTS ---

def render_header():
    cols = st.columns([1, 4, 1])
    with cols[1]:
        st.markdown("<h1 style='text-align: center;'>🧬 CYBERMETRIC <span style='color:#ff00ff'>HUB</span></h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; opacity: 0.7; letter-spacing: 1px;'>IMMUTABLE DATA MEASUREMENT SYSTEM v1.0</p>", unsafe_allow_html=True)

def main():
    ledger = LedgerManager()
    
    # Header logic
    render_header()
    
    # Main Dashboard Columns
    col1, col2, col3 = st.columns(3)
    
    # --- MODULO BIO-METRICO ---
    with col1:
        st.markdown('<div class="glass-card neon-border-cyan">', unsafe_allow_html=True)
        st.markdown("### 🏃 BIO-METRIC (IMC)")
        weight = st.number_input("Peso (kg)", min_value=1.0, max_value=300.0, value=70.0)
        height = st.number_input("Estatura (m)", min_value=0.5, max_value=2.5, value=1.75)
        
        if st.button("CALCULAR IMC"):
            calc = BMICalculator()
            res = calc.calculate(weight, height)
            ledger.add_entry(res, "BIO-METRIC")
            
            # Aura UX Colors
            color = "#00f3ff" if res.category == "Normal" else "#ff00ff" if "Peso" in res.category else "#f3ff00"
            st.markdown(f"""
                <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-top: 10px; text-align: center; border: 1px solid {color}'>
                    <h4 style='color: {color}; margin: 0;'>{res.category}</h4>
                    <h2 style='color: white; margin: 5px 0;'>{res.value}</h2>
                </div>
            """, unsafe_allow_html=True)
            
            # BMI Scale visualization
            progress = min(max((res.value - 15) / (40 - 15), 0.0), 1.0)
            st.progress(progress)
            st.caption("15 (Bajo) ----------------- 25 (Normal) ----------------- 40 (Obesidad)")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # --- MODULO ACADEMICO ---
    with col2:
        st.markdown('<div class="glass-card neon-border-magenta">', unsafe_allow_html=True)
        st.markdown("### 🎓 ACADÉMICO")
        name = st.text_input("Nombre del Estudiante", "USER_0x1")
        g1 = st.slider("Nota 1", 0.0, 5.0, 3.5)
        g2 = st.slider("Nota 2", 0.0, 5.0, 4.0)
        g3 = st.slider("Nota 3", 0.0, 5.0, 2.5)
        
        if st.button("GENERAR REPORTE"):
            calc = AcademicCalculator()
            res = calc.calculate(name, [g1, g2, g3])
            ledger.add_entry(res, "ACADEMIC")
            
            status_color = "#00ff00" if res.category == "Aprobado" else "#ff0000"
            st.markdown(f"""
                <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-top: 10px; text-align: center;'>
                    <p style='margin:0; opacity: 0.6;'>Promedio Final</p>
                    <h2 style='color: white; margin: 0;'>{res.value}</h2>
                    <h3 style='color: {status_color}; text-shadow: 0 0 10px {status_color}55;'>{res.category}</h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Multi-progress bar view
            st.write("Distribution:")
            st.progress(g1/5, text=f"Grade 1: {g1}")
            st.progress(g2/5, text=f"Grade 2: {g2}")
            st.progress(g3/5, text=f"Grade 3: {g3}")

        st.markdown('</div>', unsafe_allow_html=True)

    # --- MODULO CRONOLOGICO ---
    with col3:
        st.markdown('<div class="glass-card neon-border-cyan">', unsafe_allow_html=True)
        st.markdown("### 🕰️ CRONO-LOG")
        dob = st.date_input("Fecha de Nacimiento", datetime.date(2000, 1, 1))
        
        if st.button("CRONOMETRAR"):
            calc = ChronoCalculator()
            res = calc.calculate(dob)
            ledger.add_entry(res, "CHRONO")
            
            st.markdown(f"""
                <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-top: 10px; text-align: center; border-bottom: 2px solid var(--neon-magenta)'>
                    <p style='margin:0; opacity: 0.6;'>Has vivido aproximadamente</p>
                    <h1 style='color: var(--neon-cyan); margin: 10px 0;'>{int(res.value)}</h1>
                    <p style='margin:0; font-family: Orbitron;'>MESES EN LA RED</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://img.icons8.com/neon/96/time.png") # Simulated asset
        st.markdown('</div>', unsafe_allow_html=True)

    # --- LEDGER INMUTABLE (HISTORIAL) ---
    st.markdown("### ⛓️ LEDGER DE TRANSACCIONES (HISTORIAL INMUTABLE)")
    if st.session_state.ledger:
        # Create a more visual history
        cols_hist = st.columns(4)
        for i, entry in enumerate(st.session_state.ledger[:4]): # Show last 4 in grid
             with cols_hist[i]:
                st.markdown(f"""
                <div class="glass-card" style="padding: 10px; font-size: 0.8rem; border-color: rgba(0,243,255, 0.3)">
                    <span class="status-badge">{entry['module']}</span>
                    <p style="margin: 5px 0 0 0; color: #aaa;">ID: {entry['hash']}</p>
                    <p style="margin: 0; font-weight: bold;">{entry['metric']}: {entry['value']}</p>
                    <p style="margin: 0; font-size: 0.7rem; opacity: 0.5;">TS: {entry['timestamp']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Table view for the rest
        if len(st.session_state.ledger) > 4:
            with st.expander("VER CADENA COMPLETA"):
                df = pd.DataFrame(st.session_state.ledger)
                st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay registros en el Ledger. Comienza a calcular para generar la cadena.")

if __name__ == "__main__":
    main()
