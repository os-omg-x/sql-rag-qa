import os
from dotenv import load_dotenv
from langchain_community.llms.ollama import Ollama
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import BaseMemory
from typing import Optional
import logging
import re

# Load environment variables
load_dotenv()

# Placeholder for the actual prompt, to be provided by user
SYSTEM_PROMPT = """
You are an expert SQL generator. Use the following MySQL database schema named `school_db` to generate syntactically correct and optimized SQL queries.

Respond ONLY with the final SQL query. Do NOT explain or format your response in any other way.

Schema:

1. students (
    roll_no INT PRIMARY KEY,
    first_name VARCHAR,
    last_name VARCHAR,
    age TINYINT UNSIGNED,
    class_id INT,           -- FK → classes.class_id
    section_id INT,         -- FK → sections.section_id
    scholarship_id INT,     -- Nullable, FK → scholarships.scholarship_id
    bank_account_id INT     -- Nullable, FK → bankdetails.bank_account_id
)

2. bankdetails (
    bank_account_id INT PRIMARY KEY,
    student_roll_no INT,    -- FK → students.roll_no
    bank_name VARCHAR,
    account_number VARCHAR,
    ifsc_code VARCHAR
)

3. parents (
    parent_id INT PRIMARY KEY,
    student_roll_no INT,    -- FK → students.roll_no
    parent_name VARCHAR,
    relation VARCHAR
)

4. marks (
    mark_id INT PRIMARY KEY,
    student_roll_no INT,    -- FK → students.roll_no
    subject_id INT,         -- FK → subjects.subject_id
    marks_obtained DECIMAL
)

5. classes (
    class_id INT PRIMARY KEY,
    class_name VARCHAR,
    section_id INT          -- FK → sections.section_id
)

6. sections (
    section_id INT PRIMARY KEY,
    section_name CHAR
)

7. scholarships (
    scholarship_id INT PRIMARY KEY,
    scholarship_name VARCHAR,
    amount DECIMAL
)

8. subjects (
    subject_id INT PRIMARY KEY,
    subject_name VARCHAR
)

Relationships:
- students.class_id → classes.class_id
- students.section_id → sections.section_id
- students.scholarship_id → scholarships.scholarship_id
- students.bank_account_id → bankdetails.bank_account_id
- bankdetails.student_roll_no → students.roll_no
- parents.student_roll_no → students.roll_no
- marks.student_roll_no → students.roll_no
- marks.subject_id → subjects.subject_id
- classes.section_id → sections.section_id

Instructions:
- Return only a valid MySQL query. No explanation.
- Use table aliases where appropriate.
- Always obey foreign key relationships.
- Keep query format minimal and SQL-compliant.
- Do not use JOINs that violate schema constraints.

Examples:

Question: Get total number of students in each section.
Answer:
SELECT sec.section_name, COUNT(*) AS total_students
FROM students s
JOIN sections sec ON s.section_id = sec.section_id
GROUP BY s.section_id;

Question: Retrieve scholarship name and amount for students who have any scholarship.
Answer:
SELECT s.first_name, s.last_name, sc.scholarship_name, sc.amount
FROM students s
JOIN scholarships sc ON s.scholarship_id = sc.scholarship_id;

Question: Get full bank details of students.
Answer:
SELECT s.first_name, s.last_name, b.bank_name, b.account_number, b.ifsc_code
FROM students s
JOIN bankdetails b ON s.bank_account_id = b.bank_account_id;
"""

# Example function

def clean_sql(sql: str) -> str:
    # Remove markdown code block markers and leading/trailing whitespace
    sql = re.sub(r"^```sql\\s*|```$", "", sql.strip(), flags=re.IGNORECASE | re.MULTILINE)
    return sql.strip()

def generate_sql_query(user_query: str, memory: Optional[BaseMemory] = None) -> str:
    """
    Generate an SQL query from a natural language question using Llama-3 via Ollama and Langchain.
    Args:
        user_query (str): The user's natural language question.
        memory (BaseMemory, optional): Conversation memory for context.
    Returns:
        str: The generated SQL query.
    """
    base_url = os.getenv("BASE_URL", "http://localhost:11434")
    model_name = os.getenv("MODEL_NAME", "llama3:latest")
    llm = Ollama(model=model_name, base_url=base_url)
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template("{user_query}")
    ])
    chain = prompt | llm
    logging.info(f"[generate_sql_query] Invoking LLM for SQL generation.")
    result = chain.invoke({"user_query": user_query})
    # Handle both string and object with .content
    if hasattr(result, 'content'):
        sql = result.content.strip()
    elif isinstance(result, str):
        sql = result.strip()
    else:
        logging.error(f"[generate_sql_query] Unexpected result type: {type(result)}")
        sql = str(result)
    sql = clean_sql(sql)
    logging.info(f"[generate_sql_query] SQL generated: {sql}")
    return sql 