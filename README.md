


# 🚀 Project Name

## 📌 Table of Contents
- [Introduction](#introduction)
- [Demo](#demo)
- [Inspiration](#inspiration)
- [What It Does](#what-it-does)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [How to Run](#how-to-run)
- [Tech Stack](#tech-stack)
- [Team](#team)

---

## 🎯 Introduction
This project automates email classification and entity extraction for loan servicing requests. It processes incoming emails, classifies them into predefined request types, extracts key details, and detects duplicate requests using Pinecone vector embeddings.


## 🎥 Demo
🔗 [Live Demo](#) (if applicable)  
📹 [Video Demo](#) (if applicable)  
🖼️ Screenshots:

![Screenshot 1](link-to-image)

## 💡 Inspiration
Manual email processing in loan servicing leads to delays, errors, and inefficiencies. This project automates request classification and extracts structured data to improve response time and accuracy.


## ⚙️ What It Does
- Processes emails (.eml, .pdf, .doc, etc.)
- Classifies request types & sub-types (e.g., Money Movement, Closing Notice, Adjustments, etc.)
- Extracts key details (e.g., Loan ID, Amount, Expiry Date, etc.)
- Detects duplicate requests using Pinecone
- Displays results in an interactive UI


## 🛠️ How We Built It
🔹 LLM-based Classification: Mistral AI for intent detection  
🔹 Entity Extraction: Mistral API for extracting structured details  
🔹 Vector Embeddings: SentenceTransformers for creating and storing vevtor embeddings  
🔹 Duplicate Detection: Pinecone vector DB for similarity search  
🔹 Frontend UI: Tkinter-based Python desktop app  

## 🚧 Challenges We Faced
🔸 LLM Misclassifications: Adjusting prompt engineering for better request type identification  
🔸 Handling Attachments: Extracting data from PDF, DOC, XLSX files inside emails  
🔸 Embedding Mismatch: Ensuring vector dimensions match in Pinecone  
🔸 Duplicate Detection: Fine-tuning similarity thresholds for accurate matches  
🔸 Rate Limiters on free APIs  

## 🏃 How to Run
1. Clone the repository  
   ```sh
   git clone https://github.com/ewfx/gaied-ai-galaxy
   ```
2. Install dependencies  
   ```s
   pip install -r requirements.txt
   ```
3. Run the project  
   ```sh
   python FileUpload.py
   ```

## 🏗️ Tech Stack
🔹 LLM: Mistral AI  
🔹 Embeddings: SentenceTransformers / Pinecone  
🔹 UI: Tkinter (Python)  
🔹 Database: Pinecone (Vector DB)  
🔹 Backend: Python   

## 👥 Team
- **Yugandhar Konduri** - [GitHub](#) | [LinkedIn](#)
- **Appari Shanti** - [GitHub](#) | [LinkedIn](#)
- **Prabhakar Hechina** - [GitHub](#) | [LinkedIn](#)
