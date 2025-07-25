# School Database RAG QA System

A Retrieval-Augmented Generation (RAG) Question Answering system over a MySQL school database using Langchain, Ollama (Llama-3 7B), and MySQL connector. This project allows users to ask natural language questions and get accurate, context-aware answers based on the underlying relational data.

---

## Features
- Natural language to SQL query generation using Llama-3 7B via Ollama
- SQL execution on a MySQL database
- Natural language answer generation from SQL results
- Modern chat interface (Streamlit)
- Robust error handling and logging in terminal
- Memory Blueprint added (Not Functionally stable)

---

## Prerequisites
- **Python**: 3.8 or higher
- **MySQL**: 8.x recommended
- **Ollama**: For running Llama-3 locally ([Ollama install guide](https://ollama.com/download))
- **Git** (optional, for cloning)

---

## 1. Clone the Repository

```bash
# Linux/macOS
 git clone <your-repo-url>
 cd RAG-solution

# Windows PowerShell
git clone <your-repo-url>
cd RAG-solution
```

---

## 2. MySQL Database Setup

### a. Start MySQL Server
- **Windows**: Use MySQL Notifier or run `net start mysql` in PowerShell.
- **Linux/macOS**: `sudo service mysql start` or `sudo systemctl start mysql`

### b. Import the SQL Files (in order)

**Order:**
1. sections
2. scholarships
3. classes
4. subjects
5. students
6. bankdetails
7. parents
8. marks

**Windows PowerShell:**
```powershell
mysql -u root -p < .\mysql_db\school_db_sections.sql
mysql -u root -p < .\mysql_db\school_db_scholarships.sql
mysql -u root -p < .\mysql_db\school_db_classes.sql
mysql -u root -p < .\mysql_db\school_db_subjects.sql
mysql -u root -p < .\mysql_db\school_db_students.sql
mysql -u root -p < .\mysql_db\school_db_bankdetails.sql
mysql -u root -p < .\mysql_db/school_db_parents.sql
mysql -u root -p < .\mysql_db/school_db_marks.sql
```

**Linux/macOS:**
```bash
mysql -u root -p < ./mysql_db/school_db_sections.sql
mysql -u root -p < ./mysql_db/school_db_scholarships.sql
mysql -u root -p < ./mysql_db/school_db_classes.sql
mysql -u root -p < ./mysql_db/school_db_subjects.sql
mysql -u root -p < ./mysql_db/school_db_students.sql
mysql -u root -p < ./mysql_db/school_db_bankdetails.sql
mysql -u root -p < ./mysql_db/school_db_parents.sql
mysql -u root -p < ./mysql_db/school_db_marks.sql
```

---

## 3. Python Environment Setup

### a. Create and Activate a Virtual Environment

**Windows PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### b. Install Requirements
```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in the `RAG-solution` directory with the following content:

```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=yourpassword
MYSQL_DATABASE=school_db

# Ollama configuration
BASE_URL=http://localhost:11434
MODEL_NAME=llama3:7b
```

Replace `yourpassword` with your actual MySQL password. Change `BASE_URL` and `MODEL_NAME` if you use a different port or model.

---

## 5. Ollama Model Setup

### a. Install Ollama
- Download and install from [Ollama](https://ollama.com/download)

### b. Pull the Llama-3 Model
```bash
ollama pull llama3:7b
```

### c. Start the Ollama Server

**Windows PowerShell:**
```powershell
ollama serve
```

**Linux/macOS:**
```bash
ollama serve
```

If you want to use a different port:
```powershell
$env:OLLAMA_PORT=12345
ollama serve
```
```bash
export OLLAMA_PORT=12345
ollama serve
```
Update `BASE_URL` in your `.env` accordingly.

---

## 6. Run the Streamlit App

**Windows PowerShell:**
```powershell
streamlit run main.py
```

**Linux/macOS:**
```bash
streamlit run main.py
```

The app will open in your browser at [http://localhost:8501](http://localhost:8501).

---

## 7. Example Usage
- Type questions like:
  - Who are the students in section A?
  - Which students have a scholarship?
  - What are the average marks in Mathematics?
  - hi (for small talk)
- Follow-up questions are supported (e.g., "Which of them have a scholarship?").

---

## 8. Troubleshooting
- **MySQL connection errors:** Check your `.env` and that MySQL is running.
- **Ollama errors:** Ensure the server is running and the port matches `BASE_URL`.
- **Module not found:** Make sure your virtual environment is activated and requirements are installed.
- **Permission errors:** Try running your terminal as administrator (Windows) or with `sudo` (Linux/macOS).
- **Port conflicts:** Change the port for Ollama or Streamlit if needed.

---

## 9. Project Structure
```
RAG-solution/
├── main.py                # Main entry point
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── .env                   # Environment variables (create this)
├── rag_sql/
│   ├── __init__.py
│   ├── sql_generator.py   # NL to SQL via Llama-3
│   ├── sql_executor.py    # SQL execution (MySQL)
│   ├── nl_answer.py       # SQL result to NL answer
│   └── memory.py          # Conversation memory
└── mysql_db/              # SQL dump files
```

---

## 10. Contact & Help
- For issues, open an issue on the repository or contact the maintainer.
- For help with MySQL or Ollama, see their official documentation.

---

Enjoy your School Database RAG QA System!

Feel free to reach out to me at dev.priyanshup@gmail.com