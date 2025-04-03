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

### Setup Docker Desktop
1. **Download Docker Desktop**:
   Download Docker Desktop to your local computer using the following link:
   ```sh
   https://www.docker.com/products/docker-desktop/
   ```
   
2. **Login to Docker Desktop**:
   Login to Docker Desktop using your google email account. In Docker Desktop go to the Images tab and open the terminal window.

3. **Download Image**:
   
   Option A: Complete a docker pull command to download the image. Observe the names of the images being populated in the Image Tab. The syntax for this command is “docker pull <image name>".

   Option B: Complete the setup steps below. If you are running the codebase in WSL and running Docker Desktop on Windows ensure they are connected: Open Docker Desktop → Settings → Resources → WSL Integration

   NOTE: Do not continue to the next step until you have completed steps 1-4 of the Setup Steps. These steps should populate Docker Images in your Docker Desktop.

4. **Docker Image Configuration**:
   - Open up powershell in Admin mode on your computer.
   - run the following commands to create a directory named "my-docker-project" and change directory into the newly created directory
   ```sh
   mkdir my-docker-project
   ```
   ```sh
   cd my-docker-project
   ```
   - create the docker-compose.yaml in the my-docker-project directory using notepad via the below command
   ```sh
   notepad docker-compose.yaml 
   ```
   - You should see a notepad pop up. Copy the contents of the docker-compose.yaml within this repo into the notepad document and save it.
  
5. **Start Docker Images**:
   - In the powershell terminal execute the below command to start the Docker Images. This command was successful if the terminal returned "Started" or "Running".
   ```sh
   docker-compose up -d
   ```
   - To verify the containters are running, execute the following command in the powershell terminal. Ensure the status is listed as "Up".
   ```sh
   docker ps
   ```

6. **Access the Application**:
   - To access the application open a browser and paste in the below URL:
   ```sh
   http://localhost/
   ```

### Setup Steps
1. **Clone the repository or Import Zip File**:
   ```sh
   git clone https://github.com/kalinchenko23/capstoneAI2C.git
   capstoneAI2C
   ```

2. **Set up a virtual environment**:
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # MacOS/Linux
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Create Docker Images**:
   ```sh
   cd frontend
   docker build -t frontend:latest .
   cd ..
   cd backend
   docker build -t backend:latest .
   ```





## References

- **Google Maps API Documentation:** [Google Developers](https://developers.google.com/maps/documentation/places/web-service)
- **Azure Kubernetes Service (AKS):** [Microsoft Azure](https://azure.microsoft.com/en-us/products/kubernetes-service)
- **Azure Pricing Calculator:** [Azure Pricing](https://azure.microsoft.com/en-us/pricing/calculator/)
- **Streamlit:** [Streamlit.io](https://streamlit.io/)
