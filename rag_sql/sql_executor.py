import mysql.connector
import os
import pandas as pd
from typing import List, Dict

def execute_sql_query(sql_query: str) -> List[Dict]:
    """
    Execute the given SQL query on the MySQL database and return the result as a list of dictionaries.
    If an error occurs, log it and return None.
    Args:
        sql_query (str): The SQL query to execute.
    Returns:
        List[Dict]: The query result as a list of dictionaries.
    """
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "school_db")
    )
    try:
        df = pd.read_sql(sql_query, conn)
        return df.to_dict(orient="records")
    except Exception as e:
        logging.error(f"[SQL EXECUTION ERROR] {e}", exc_info=True)
        return None
    finally:
        conn.close() 