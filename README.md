# 🧬 CyberMetric Hub - Web3 Measurement Ecosystem

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-ff4b4b.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An advanced interactive web application built with Python and Streamlit, designed as a multi-tool personal and academic measurement system. This project follows **Clean Code (SOLID)** principles and features a high-end **Cyberpunk/Glassmorphism** aesthetic.

---

## 🚀 Vision
To empower users with a fast, private, and visually stunning data dashboard. Every calculation is part of an **Immutable Ledger (Simulated Blockchain)**, ensuring a permanent historical record of your metrics during the session.

---

## 🛠️ Key Features

### 🏃 1. Bio-Metric Module (IMC)
- **Calculation**: BMI ($Weight / Height^2$).
- **Aura UX**: Dynamic color alerts based on category (Normal, Overweight, Underweight).
- **Responsive Visuals**: Real-time progress bars showing your position on the global BMI scale.

### 🎓 2. Academic Module (Report)
- **Student Stats**: Multi-input grade tracker (Grades 1-3).
- **Status Indicators**: Automatic "Aproved" or "Failed" status with status-based glowing effects.
- **Progress Tracking**: Visual health bars for each individual grade.

### 🕰️ 3. Chrono-Log Module
- **Time Analysis**: Calculates total months lived since birth.
- **Time Visualization**: High-impact counter showing the user's presence "in the network".

### ⛓️ 4. Transaction Ledger (Web3 Style)
- **Immutability**: Every calculation generates a unique 8-char Hash (ID) and timestamp.
- **Event History**: A scrollable visual chain displaying the most recent transactions first.

---

## 🏗️ Architecture (SOLID)
- **Single Responsibility (SRP)**: Each calculator class (`BMICalculator`, `AcademicCalculator`, `ChronoCalculator`) handles one specific logic.
- **Liskov Substitution (LSP)**: All calculators inherit from `BaseCalculator`.
- **Dependency Inversion (DIP)**: The UI interacts with the `LedgerManager` and `BaseCalculator` abstractions.

---

## 🎨 Visual Design System
- **Dark Mode**: Radial gradient background with deep navy tones.
- **Glassmorphism**: Translucent cards with `backdrop-filter` blur.
- **Neón UI**: Cyan and Magenta border accents with matching text shadows.
- **Responsiveness**: Fully fluid layout using CSS Media Queries for any device.

---

## 💻 Tech Stack
- **Frontend/Backend**: [Streamlit](https://streamlit.io/)
- **Data Handling**: [Pandas](https://pandas.pydata.org/), [Numpy](https://numpy.org/)
- **Styling**: [CSS3](https://developer.mozilla.org/en-US/docs/Web/CSS) (Glassmorphism + Flexbox)

---

## 📥 Installation

```bash
# Clone the repository
git clone https://github.com/joseberna/IMC-demo-python.git

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## 👨‍💻 Author
**Jose Berna** - [GitHub](https://github.com/joseberna)

---

> "Data is the new oil. Visualization is the engine." 🧬⚡
