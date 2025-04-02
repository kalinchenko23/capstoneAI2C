# PLAIDE: Google Maps Data Extraction and Analysis

## Table of Contents
- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Motivation](#motivation)
- [Key Features](#key-features)
- [Installation](#installation)
- [Roadmap](#roadmap)
- [Acknowledgments](#acknowledgments)
- [References](#references)

---

## Project Overview

The **PLAIDE Application** automates the process of extracting and analyzing Google Maps data. The toolkit reduces the time a users spends gathering and formatting location data from **days** to **minutes** by leveraging **Google Maps API**, **Large Language Models (LLM)**, and **Vision Language Models (VLM)**.

This cloud-native application, deployed on **Azure Kubernetes Service (AKS)** as well as local hosted variation via Docker Desktop, provides a user interface for analysts to retrieve structured and georeferenced reports with crucial location information.

---

## Problem Statement

Users manually extract location-based information from **Google Maps**, requiring **8-40 hours** per request. The process is inefficient, with users manually gathering **names, locations, hours of operation, summaries of reviews, and descriptions of photos**.

### Key challenges:
- No automated way to extract and analyze Google Maps data.
- Manual data entry is error-prone and time-consuming.
- The process does not scale well for multiple analysts or urgent requests.

---

## Motivation

**Why build this?**
- Reduce information-gathering time by **90%**.
- Enable real-time, structured data analysis.
- Provide AI-enhanced insights for faster decision-making.
- Improve operational effectiveness with **Excel and geospatial reports**.

---

## Key Features

✅ **Automated Google Maps Data Extraction** – Uses **Google Maps API** to retrieve places, reviews, and photos.

✅ **AI-Powered Analysis** – Uses **LLMs** to summarize reviews and **VLMs** to generate image descriptions.

✅ **Excel & Geospatial Reports** – Outputs data in **Excel** (tabular format) and **KMZ** (georeferenced) formats.

✅ **User-Friendly Web Interface** – Simple UI for analysts to input locations, bounding boxes, and desired data fields.

✅ **Secure & Scalable Cloud Deployment** – Hosted on **Azure Kubernetes Service (AKS)** with **Azure OpenAI services**.

✅ **Optimized API Calls** – Reduces Google API costs by optimizing query requests using text search parameters.

---

## Installation

### Prerequisites
Ensure you have the following installed:
- **Python 3.9+**
- **Docker**
- **Azure CLI**
- **Kubernetes (kubectl)**
- **Google Cloud API Key**

### Setup Steps
1. **Clone the repository**:
   ```sh
   git clone https://github.com/kalinchenko23/capstoneAI2C.git
   capstoneAI2C
   ```

2. **Set up a virtual environment**:
   ```sh
   python -m venv venv
   source venv/bin/activate  # MacOS/Linux
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Create a `.secrets.json` file and configure the following:
     ```
     GOOGLE_API_KEY=your_google_maps_api_key
     AZURE_OPENAI_KEY=your_azure_openai_key
     ```
---

## References

- **Google Maps API Documentation:** [Google Developers](https://developers.google.com/maps/documentation/places/web-service)
- **Azure Kubernetes Service (AKS):** [Microsoft Azure](https://azure.microsoft.com/en-us/products/kubernetes-service)
- **Azure Pricing Calculator:** [Azure Pricing](https://azure.microsoft.com/en-us/pricing/calculator/)
- **Streamlit:** [Streamlit.io](https://streamlit.io/)
