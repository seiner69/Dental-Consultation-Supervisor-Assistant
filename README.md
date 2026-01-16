# Dental Consultation Supervisor Assistant (DCSA)

> **Empowering Dental Clinics with AI-Driven Compliance & Sales Intelligence.**

![Architecture](https://img.shields.io/badge/Architecture-Hexagonal-blue)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green)



## 📖 Introduction
DCSA is a vertical AI solution designed to audit dental consultations. It leverages **ASR** (SenseVoice) and **LLM** (Qwen-Plus) to turn unstructured audio into structured business insights, focusing on compliance, pain point detection, and sales conversion analysis.

## 🚀 Key Features
* **Automated QA**: Scores every consultation against gold-standard medical sales protocols.
* **Structured DataFlow**: Transforms voice data into actionable SQL-ready records.
* **Privacy First**: Local deployment friendly with strict data separation.

## 🛠️ Quick Start
1.  Setup env: `cp .env.example .env`
2.  Install: `pip install -r requirements.txt`
3.  Run: `streamlit run src/ui/dashboard.py`