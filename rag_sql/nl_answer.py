import os
from dotenv import load_dotenv
from langchain_community.llms.ollama import Ollama
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import BaseMemory
from typing import Any, Optional
import orjson
import logging

# Load environment variables
load_dotenv()

SYSTEM_PROMPT = """You are a helpful assistant that explains SQL query results in natural language for a school database. Use the schema and examples provided."""

def generate_nl_answer(user_query: str, sql_query: str, sql_result: Any, memory: Optional[BaseMemory] = None) -> str:
    """
    Generate a natural language answer from the SQL result using Llama-3 via Ollama and Langchain.
    Args:
        user_query (str): The user's original question.
        sql_query (str): The SQL query that was run.
        sql_result (Any): The result of the SQL query (list of dicts).
        memory (BaseMemory, optional): Conversation memory for context.
    Returns:
        str: The generated natural language answer.
    """
    base_url = os.getenv("BASE_URL", "http://localhost:11434")
    model_name = os.getenv("MODEL_NAME", "llama3:latest")
    llm = Ollama(model=model_name, base_url=base_url)
    sql_result_str = orjson.dumps(sql_result).decode()
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(
            "User question: {user_query}\nSQL query: {sql_query}\nSQL result: {sql_result_str}\nPlease answer in natural language.")
    ])
    chain = prompt | llm
    logging.info(f"[generate_nl_answer] Invoking LLM for NL answer generation.")
    result = chain.invoke({
        "user_query": user_query,
        "sql_query": sql_query,
        "sql_result_str": sql_result_str
    })
    # Handle both string and object with .content
    if hasattr(result, 'content'):
        answer = result.content.strip()
    elif isinstance(result, str):
        answer = result.strip()
    else:
        logging.error(f"[generate_nl_answer] Unexpected result type: {type(result)}")
        answer = str(result)
    logging.info(f"[generate_nl_answer] NL answer generated: {answer}")
    return answer 