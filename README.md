# PLAIDE: Google Maps Data Extraction and Analysis

## Table of Contents
- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Motivation](#motivation)
- [Key Features](#key-features)
- [Installation](#installation)
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
   
3. **Login to Docker Desktop**:

   - Login to Docker Desktop using your google email account. In Docker Desktop go to the Images tab and open the terminal window.
   - If you are running the codebase in WSL and running Docker Desktop on Windows ensure they are connected: Open Docker Desktop → Settings → Resources → WSL Integration

4. **Build and Run Images**:

   - Clone the github repo or download code zipfile. 
   - Using VSCODE and the integrated terminal navigate to the application parent directory "cd capstoneAI2C" or "cd capstoneAI2C-main"
   - Execute the below command to use docker-compose to build the frontend and backend Docker Images using the docker-compose.yaml and run the images
   ```sh
   docker-compose up -d --build
   ```
   - The above command take approximately 90 seconds to complete. The terminal output from this command will look like the below:
     
      ✔ backend                       Built                                                                                                          
      ✔ frontend                      Built                                                                                                                   
      ✔ Network capstoneai2c_default  Created                                                                                                                 
      ✔ Container backend             Started                                                                                                                
      ✔ Container frontend            Started
  
   - To verify the containters are running, execute the following command in the powershell terminal. Ensure the status is listed as "Up".
   
   ```sh
   docker ps
   ```

8. **Access the Application**:
   - To access the application open a browser and paste in the below URL:
     
   ```sh
   http://localhost/
   ```

9. **Stopping the Application**:
   - In the event there is a need stop the containers run the following command:

   ```sh
   docker-compose down --volumes
   ```
   - If the output of this command is “no such service -volumes”, ensure there are have two dashes (-) before volumes. The correct output from this command is, "container frontend removed, container backend removed, and network my-docker-project_default removed” each printed on their own separate line.
   - To ensure there are no containers running execute the following:
      
   ```sh
   docker ps
   ```

Admin Note: The docker engine needs to run to allow docker compose to run the containers. To ensure this occurs go to Docker Desktop and click on the settings gear in the upper right hand corner. Under the General tab ensure the box labeled “Start Docker Desktop when you sign in to your computer” is checked. 

## References

- **Google Maps API Documentation:** [Google Developers](https://developers.google.com/maps/documentation/places/web-service)
- **Azure Kubernetes Service (AKS):** [Microsoft Azure](https://azure.microsoft.com/en-us/products/kubernetes-service)
- **Azure Pricing Calculator:** [Azure Pricing](https://azure.microsoft.com/en-us/pricing/calculator/)
- **Streamlit:** [Streamlit.io](https://streamlit.io/)
