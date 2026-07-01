

# from sqlalchemy import create_engine, text, inspect
# from sqlalchemy.pool import NullPool
# from typing import List, Dict
# import json
# import re
# import os
# import logging
# import time
# from dotenv import load_dotenv

# load_dotenv()

# logger = logging.getLogger(__name__)

# PREAUTHORIZATION_SCHEMA = """
# Table: preauthorizations
# Columns:
#     - request_id: VARCHAR(50)              # Unique preauth request ID (Primary Key)
#     - policy_number: VARCHAR(50)           # Policy number (e.g., POL-776620) - Used for authentication
#     - emirates_id: VARCHAR(50)             # UAE Emirates ID (format: 784-YYYY-XXXXXXX-X)
#     - member_id: VARCHAR(50)               # Insurance member ID
#     - patient_name: VARCHAR(200)           # Patient full name
#     - patient_dob: DATE                    # Patient date of birth

#     - provider_id: VARCHAR(50)             # Healthcare provider ID
#     - provider_name: VARCHAR(200)          # Provider name and facility
#     - provider_license: VARCHAR(50)        # Provider license number

#     - payer_id: VARCHAR(50)                # Insurance payer ID (e.g., DAMAN, AXAGULF, MEDNET)
#     - payer_name: VARCHAR(200)             # Payer company name

#     - request_type: VARCHAR(50)            # Type: MEDICATION or PROCEDURE
#     - urgency: VARCHAR(20)                 # ROUTINE or URGENT

#     - requested_service: TEXT              # Service description (e.g., "Biologic Medication Authorization")
#     - procedure_details: JSON              # JSON with procedure info (procedure_code, procedure_name, type, site, anesthesia)
#     - medication_details: JSON             # JSON with medication info (drug_name, dosage, frequency, duration_weeks, condition, type)

#     - clinical_justification: TEXT         # Medical justification for request

#     - estimated_cost: DECIMAL(10,2)        # Estimated cost in AED per injection/procedure
#     - approved_cost: DECIMAL(10,2)         # Approved amount in AED

#     - status: VARCHAR(50)                  # PENDING, APPROVED, DENIED, PARTIALLY_APPROVED
#     - status_reason: TEXT                  # Reason for denial or partial approval
#     - approval_number: VARCHAR(100)        # Approval number if approved (format: APR-XXXXXX)

#     - requested_date: DATE                 # Date request was submitted
#     - decision_date: DATE                  # Date decision was made
#     - created_at: TIMESTAMP                # Record creation timestamp
# """

# class SQLDatabaseAgent:
#     def __init__(self, db_connection: str, llm):
#         # Create engine with connection pooling and health checks
#         self.engine = create_engine(
#             db_connection,
#             pool_pre_ping=True,  # Test connections before using them
#             pool_recycle=3600,   # Recycle connections after 1 hour
#             pool_size=5,         # Keep 5 connections in pool
#             max_overflow=10,     # Allow up to 10 overflow connections
#             connect_args={
#                 'connect_timeout': 10,  # 10 second connection timeout
#                 'options': '-c statement_timeout=30000'  # 30 second query timeout
#             }
#         )
#         self.llm = llm
#         self.db_schema = PREAUTHORIZATION_SCHEMA
#         self.last_sql_query = None
#         logger.info("SQL Database Agent initialized with connection pooling")

#     def _test_connection(self) -> bool:
#         """Test if database connection is healthy"""
#         try:
#             with self.engine.connect() as conn:
#                 conn.execute(text("SELECT 1"))
#             logger.debug("Database connection test: SUCCESS")
#             return True
#         except Exception as e:
#             logger.error(f"Database connection test: FAILED - {e}")
#             return False

#     def _reconnect(self, max_retries: int = 3) -> bool:
#         """Attempt to reconnect to database"""
#         for attempt in range(max_retries):
#             try:
#                 logger.info(f"Reconnection attempt {attempt + 1}/{max_retries}")
#                 self.engine.dispose()  # Close all connections
#                 time.sleep(1)  # Wait before retry

#                 if self._test_connection():
#                     logger.info("Reconnection successful")
#                     return True
#             except Exception as e:
#                 logger.error(f"Reconnection attempt {attempt + 1} failed: {e}")
#                 if attempt < max_retries - 1:
#                     time.sleep(2)  # Wait before next retry

#         logger.error("All reconnection attempts failed")
#         return False

#     def generate_sql(self, query: str) -> str:
#         """Generate SQL query from natural language using LLM intelligence"""

#         messages = [
#             {
#                 "role": "system",
#                 "content": f"""You are an expert SQL generator for an insurance preauthorization system. Your job is to convert natural language queries into precise PostgreSQL statements.

# DATABASE SCHEMA:
# {self.db_schema}

# IMPORTANT RULES:
# 1. Always use the EXACT column names from the schema above
# 2. Table name is 'preauthorizations' (plural)
# 3. When users say "my preauth" or "my request" → select relevant columns from preauthorizations
# 4. When users say "preauth status" or "request status" → use 'status' column (PENDING, APPROVED, DENIED, PARTIALLY_APPROVED)
# 5. When users say "procedure" → use 'procedure_details' JSON column
# 6. When users say "medication" → use 'medication_details' JSON column
# 7. When users say "cost" → use 'estimated_cost' or 'approved_cost' columns
# 8. When users say "my details" or "my information" → select ALL columns (*)
# 9. Always include WHERE policy_number = 'POLICY_NUMBER' to filter by authenticated policy
# 10. Add LIMIT 10 by default to prevent large result sets (unless user specifies otherwise)
# 11. For JSON columns, you can use PostgreSQL JSON operators like ->, ->>
# 12. Return ONLY the SQL query - no explanations, no markdown, no formatting

# EXAMPLES:
# Input: "For policy POL-776620: show my preauthorization requests"
# Output: SELECT request_id, patient_name, requested_service, status, estimated_cost, requested_date FROM preauthorizations WHERE policy_number = 'POL-776620' ORDER BY requested_date DESC LIMIT 10

# Input: "For policy POL-776620: what is my preauth status"
# Output: SELECT request_id, patient_name, status, status_reason, approval_number, approved_cost FROM preauthorizations WHERE policy_number = 'POL-776620' ORDER BY requested_date DESC LIMIT 10

# Input: "For policy POL-776620: show denied requests"
# Output: SELECT request_id, requested_service, status_reason, estimated_cost FROM preauthorizations WHERE policy_number = 'POL-776620' AND status = 'DENIED' LIMIT 10

# Input: "For policy POL-776620: show my medication preauths"
# Output: SELECT request_id, medication_details, status, estimated_cost, approved_cost FROM preauthorizations WHERE policy_number = 'POL-776620' AND request_type = 'MEDICATION' LIMIT 10

# Input: "For policy POL-776620: my latest request"
# Output: SELECT * FROM preauthorizations WHERE policy_number = 'POL-776620' ORDER BY requested_date DESC LIMIT 1

# Input: "For policy POL-776620: requests from last month"
# Output: SELECT request_id, requested_service, status, requested_date FROM preauthorizations WHERE policy_number = 'POL-776620' AND requested_date >= NOW() - INTERVAL '1 month' ORDER BY requested_date DESC LIMIT 10

# Input: "For policy POL-776620: show approved procedures"
# Output: SELECT request_id, procedure_details, approved_cost, approval_number FROM preauthorizations WHERE policy_number = 'POL-776620' AND request_type = 'PROCEDURE' AND status = 'APPROVED' LIMIT 10

# Now generate SQL for: {query}"""
#             }
#         ]

#         response = self.llm.invoke(messages)
#         sql_query = response.content.strip()

#         # Clean any potential markdown formatting
#         sql_query = sql_query.replace('```sql', '').replace('```', '').replace('```postgresql', '').strip()

#         self.last_sql_query = sql_query
#         return sql_query
    
#     def generate_sql_with_context(self, query: str, context: str) -> str:
#         """Generate SQL query with conversation context using LLM intelligence"""

#         messages = [
#             {
#                 "role": "system",
#                 "content": f"""You are an expert SQL generator for an insurance preauthorization system. Convert natural language queries into precise PostgreSQL statements using conversation context.

# DATABASE SCHEMA:
# {self.db_schema}

# CONVERSATION CONTEXT:
# {context}

# CURRENT QUERY: {query}

# IMPORTANT RULES:
# 1. Use the conversation context to understand the policy holder and what they're asking for
# 2. Always use EXACT column names from the schema
# 3. Table name is 'preauthorizations'
# 4. Map natural language to correct columns:
#    - "preauth", "request", "authorization" → preauthorizations table
#    - "status" → 'status' column (PENDING, APPROVED, DENIED, PARTIALLY_APPROVED)
#    - "procedure" → 'procedure_details' JSON column
#    - "medication" → 'medication_details' JSON column
#    - "cost" → 'estimated_cost', 'approved_cost'
#    - "details", "information" → all columns (*)
# 5. Always include WHERE policy_number = 'POLICY_NUMBER' when you can identify the policy
# 6. Add LIMIT 10 by default to prevent large result sets
# 7. Return ONLY the SQL query - no explanations, no markdown, no formatting

# Generate SQL for the current query considering the context."""
#             }
#         ]

#         response = self.llm.invoke(messages)
#         sql_query = response.content.strip()
#         sql_query = sql_query.replace('```sql', '').replace('```', '').replace('```postgresql', '').strip()
#         self.last_sql_query = sql_query
#         return sql_query
    
#     def execute_sql(self, sql_query: str) -> List[Dict]:
#         """Execute SQL query with retry logic and error handling"""
#         max_retries = 3

#         for attempt in range(max_retries):
#             try:
#                 logger.debug(f"Executing SQL query (attempt {attempt + 1}/{max_retries})")

#                 with self.engine.connect() as conn:
#                     result = conn.execute(text(sql_query))
#                     rows = [dict(row._mapping) for row in result]

#                     if not rows:
#                         logger.info("Query executed successfully but returned no results")
#                         return [{"message": "No preauthorization requests found for your account. If you recently submitted a request, it may take a few hours to appear in the system."}]

#                     logger.info(f"Query executed successfully, returned {len(rows)} row(s)")
#                     return rows

#             except Exception as e:
#                 error_str = str(e)
#                 logger.error(f"Database error on attempt {attempt + 1}: {error_str}")

#                 # Check if it's a connection error
#                 if "connection" in error_str.lower() or "server closed" in error_str.lower():
#                     if attempt < max_retries - 1:
#                         logger.info("Connection error detected, attempting to reconnect...")
#                         if self._reconnect():
#                             logger.info("Reconnection successful, retrying query...")
#                             continue  # Retry the query
#                         else:
#                             logger.error("Reconnection failed")

#                     # Final attempt failed or reconnection failed
#                     return [{"error": "Unable to connect to the database. Please try again in a moment or contact support if the issue persists."}]

#                 # For other database errors (syntax, permission, etc.)
#                 logger.error(f"Non-connection database error: {error_str}")
#                 return [{"error": "There was an issue retrieving your preauthorization information. Please try rephrasing your question or contact support."}]

#         # Should not reach here, but just in case
#         return [{"error": "Unable to process your request after multiple attempts. Please contact support."}]
    
#     def format_answer(self, query: str, sql_query: str, sql_result: List[Dict]) -> str:
#         """Format SQL results into natural language answer using LLM intelligence"""

#         # Handle error results with user-friendly messages
#         if len(sql_result) == 1:
#             if "error" in sql_result[0]:
#                 return sql_result[0]["error"]
#             if "message" in sql_result[0]:
#                 return sql_result[0]["message"]

#         # Use LLM to format the response intelligently
#         messages = [
#             {
#                 "role": "system",
#                 "content": f"""You are a helpful insurance preauthorization assistant. Convert SQL query results into clear, natural language responses.

# DATABASE SCHEMA:
# {self.db_schema}

# **ANTI-HALLUCINATION RULES** (CRITICAL):
# 1. ⚠️ ONLY present data from the QUERY RESULTS below - DO NOT add, modify, or invent any information
# 2. ⚠️ If a field is NULL or empty in results, say "not provided" or "not available" - NEVER make up values
# 3. ⚠️ DO NOT invent preauth details, procedure/medication names, dates, costs, or status information
# 4. ⚠️ Use EXACT values from the query results - do not paraphrase numbers, dates, statuses, or costs
# 5. ⚠️ If query results are empty, say "No preauthorization requests found" - do not suggest possible reasons

# FORMATTING RULES:
# 1. Be conversational and friendly
# 2. Format dates in readable format (e.g., "January 15, 2024") ONLY if date exists in results
# 3. Present preauthorization information clearly and organized
# 4. For status, use the EXACT status from database (PENDING, APPROVED, DENIED, PARTIALLY_APPROVED)
# 5. For procedure/medication details (JSON), format them as bullet points using ONLY the actual data from results
# 6. For costs, always show currency as AED (e.g., "AED 5,500.00")
# 7. If multiple requests, show them in numbered list with EXACT data from each row
# 8. Keep responses concise but informative
# 9. Always be helpful and professional
# 10. NEVER assume or add information not in the results

# USER'S ORIGINAL QUESTION: {query}
# SQL QUERY USED: {sql_query}
# QUERY RESULTS: {json.dumps(sql_result, default=str)}

# Provide a clear, helpful response using ONLY the data from query results above."""
#             }
#         ]

#         response = self.llm.invoke(messages)
#         return response.content.strip()

#     def get_schema_info(self) -> str:
#         """Return schema information for debugging"""
#         return self.db_schema
        
#     def get_last_query(self) -> str:
#         """Return the last generated SQL query for debugging"""
#         return self.last_sql_query or "No query generated yet"


from sqlalchemy import create_engine, text, inspect
from sqlalchemy.pool import NullPool
from typing import List, Dict
import json
import re
import os
import logging
import time
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

PREAUTHORIZATION_SCHEMA = """
Table: preauthorizations
Columns:
    - request_id: VARCHAR(50)              # Unique preauth request ID (Primary Key)
    - policy_number: VARCHAR(50)           # Policy number (e.g., POL-776620) - Used for authentication
    - emirates_id: VARCHAR(50)             # UAE Emirates ID (format: 784-YYYY-XXXXXXX-X)
    - member_id: VARCHAR(50)               # Insurance member ID
    - patient_name: VARCHAR(200)           # Patient full name
    - patient_dob: DATE                    # Patient date of birth

    - provider_id: VARCHAR(50)             # Healthcare provider ID
    - provider_name: VARCHAR(200)          # Provider name and facility
    - provider_license: VARCHAR(50)        # Provider license number

    - payer_id: VARCHAR(50)                # Insurance payer ID (e.g., DAMAN, AXAGULF, MEDNET)
    - payer_name: VARCHAR(200)             # Payer company name

    - request_type: VARCHAR(50)            # Type: MEDICATION or PROCEDURE
    - urgency: VARCHAR(20)                 # ROUTINE or URGENT

    - requested_service: TEXT              # Service description (e.g., "Biologic Medication Authorization")
    - procedure_details: JSON              # JSON with procedure info (procedure_code, procedure_name, type, site, anesthesia)
    - medication_details: JSON             # JSON with medication info (drug_name, dosage, frequency, duration_weeks, condition, type)

    - clinical_justification: TEXT         # Medical justification for request

    - estimated_cost: DECIMAL(10,2)        # Estimated cost in AED per injection/procedure
    - approved_cost: DECIMAL(10,2)         # Approved amount in AED

    - status: VARCHAR(50)                  # PENDING, APPROVED, DENIED, PARTIALLY_APPROVED
    - status_reason: TEXT                  # Reason for denial or partial approval
    - approval_number: VARCHAR(100)        # Approval number if approved (format: APR-XXXXXX)

    - requested_date: DATE                 # Date request was submitted
    - decision_date: DATE                  # Date decision was made
    - created_at: TIMESTAMP                # Record creation timestamp
"""

class SQLDatabaseAgent:
    def __init__(self, db_connection: str, llm):
        # Create engine with connection pooling and health checks
        self.engine = create_engine(
            db_connection,
            pool_pre_ping=True,  # Test connections before using them
            pool_recycle=3600,   # Recycle connections after 1 hour
            pool_size=5,         # Keep 5 connections in pool
            max_overflow=10,     # Allow up to 10 overflow connections
            connect_args={
                'connect_timeout': 10,  # 10 second connection timeout
                'options': '-c statement_timeout=30000'  # 30 second query timeout
            }
        )
        self.llm = llm
        self.db_schema = PREAUTHORIZATION_SCHEMA
        self.last_sql_query = None
        logger.info("SQL Database Agent initialized with connection pooling")

    def _test_connection(self) -> bool:
        """Test if database connection is healthy"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.debug("Database connection test: SUCCESS")
            return True
        except Exception as e:
            logger.error(f"Database connection test: FAILED - {e}")
            return False

    def _reconnect(self, max_retries: int = 3) -> bool:
        """Attempt to reconnect to database"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Reconnection attempt {attempt + 1}/{max_retries}")
                self.engine.dispose()  # Close all connections
                time.sleep(1)  # Wait before retry

                if self._test_connection():
                    logger.info("Reconnection successful")
                    return True
            except Exception as e:
                logger.error(f"Reconnection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before next retry

        logger.error("All reconnection attempts failed")
        return False

    def generate_sql(self, query: str) -> str:
        """Generate SQL query from natural language using LLM intelligence"""

        messages = [
            {
                "role": "system",
                "content": f"""You are an expert SQL generator for an insurance preauthorization system. Your job is to convert natural language queries into precise PostgreSQL statements.

DATABASE SCHEMA:
{self.db_schema}

IMPORTANT RULES:
1. Always use the EXACT column names from the schema above
2. Table name is 'preauthorizations' (plural)
3. When users say "my preauth" or "my request" → select relevant columns from preauthorizations
4. When users say "preauth status" or "request status" → use 'status' column (PENDING, APPROVED, DENIED, PARTIALLY_APPROVED)
5. When users say "procedure" → use 'procedure_details' JSON column
6. When users say "medication" → use 'medication_details' JSON column
7. When users say "cost" → use 'estimated_cost' or 'approved_cost' columns
8. When users say "my details" or "my information" → select ALL columns (*)
9. Always include WHERE policy_number = 'POLICY_NUMBER' to filter by authenticated policy
10. Add LIMIT 10 by default to prevent large result sets (unless user specifies otherwise)
11. For JSON columns, you can use PostgreSQL JSON operators like ->, ->>
12. Return ONLY the SQL query - no explanations, no markdown, no formatting

EXAMPLES:
Input: "For policy POL-776620: show my preauthorization requests"
Output: SELECT request_id, patient_name, requested_service, status, estimated_cost, requested_date FROM preauthorizations WHERE policy_number = 'POL-776620' ORDER BY requested_date DESC LIMIT 10

Input: "For policy POL-776620: what is my preauth status"
Output: SELECT request_id, patient_name, status, status_reason, approval_number, approved_cost FROM preauthorizations WHERE policy_number = 'POL-776620' ORDER BY requested_date DESC LIMIT 10

Input: "For policy POL-776620: show denied requests"
Output: SELECT request_id, requested_service, status_reason, estimated_cost FROM preauthorizations WHERE policy_number = 'POL-776620' AND status = 'DENIED' LIMIT 10

Input: "For policy POL-776620: show my medication preauths"
Output: SELECT request_id, medication_details, status, estimated_cost, approved_cost FROM preauthorizations WHERE policy_number = 'POL-776620' AND request_type = 'MEDICATION' LIMIT 10

Input: "For policy POL-776620: my latest request"
Output: SELECT * FROM preauthorizations WHERE policy_number = 'POL-776620' ORDER BY requested_date DESC LIMIT 1

Input: "For policy POL-776620: requests from last month"
Output: SELECT request_id, requested_service, status, requested_date FROM preauthorizations WHERE policy_number = 'POL-776620' AND requested_date >= NOW() - INTERVAL '1 month' ORDER BY requested_date DESC LIMIT 10

Input: "For policy POL-776620: show approved procedures"
Output: SELECT request_id, procedure_details, approved_cost, approval_number FROM preauthorizations WHERE policy_number = 'POL-776620' AND request_type = 'PROCEDURE' AND status = 'APPROVED' LIMIT 10

Now generate SQL for: {query}"""
            }
        ]

        response = self.llm.invoke(messages)
        sql_query = response.content.strip()

        # Clean any potential markdown formatting
        sql_query = sql_query.replace('```sql', '').replace('```', '').replace('```postgresql', '').strip()

        self.last_sql_query = sql_query
        return sql_query
    
    def generate_sql_with_context(self, query: str, context: str) -> str:
        """Generate SQL query with conversation context using LLM intelligence"""

        messages = [
            {
                "role": "system",
                "content": f"""You are an expert SQL generator for an insurance preauthorization system. Convert natural language queries into precise PostgreSQL statements using conversation context.

DATABASE SCHEMA:
{self.db_schema}

CONVERSATION CONTEXT:
{context}

CURRENT QUERY: {query}

IMPORTANT RULES:
1. Use the conversation context to understand the policy holder and what they're asking for
2. Always use EXACT column names from the schema
3. Table name is 'preauthorizations'
4. Map natural language to correct columns:
   - "preauth", "request", "authorization" → preauthorizations table
   - "status" → 'status' column (PENDING, APPROVED, DENIED, PARTIALLY_APPROVED)
   - "procedure" → 'procedure_details' JSON column
   - "medication" → 'medication_details' JSON column
   - "cost" → 'estimated_cost', 'approved_cost'
   - "details", "information" → all columns (*)
5. Always include WHERE policy_number = 'POLICY_NUMBER' when you can identify the policy
6. Add LIMIT 10 by default to prevent large result sets
7. Return ONLY the SQL query - no explanations, no markdown, no formatting

Generate SQL for the current query considering the context."""
            }
        ]

        response = self.llm.invoke(messages)
        sql_query = response.content.strip()
        sql_query = sql_query.replace('```sql', '').replace('```', '').replace('```postgresql', '').strip()
        self.last_sql_query = sql_query
        return sql_query
    
    def execute_sql(self, sql_query: str) -> List[Dict]:
        """Execute SQL query with retry logic and error handling"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                logger.debug(f"Executing SQL query (attempt {attempt + 1}/{max_retries})")

                with self.engine.connect() as conn:
                    result = conn.execute(text(sql_query))
                    rows = [dict(row._mapping) for row in result]

                    if not rows:
                        logger.info("Query executed successfully but returned no results")
                        return [{"message": "No preauthorization requests found for your account. If you recently submitted a request, it may take a few hours to appear in the system."}]

                    logger.info(f"Query executed successfully, returned {len(rows)} row(s)")
                    return rows

            except Exception as e:
                error_str = str(e)
                logger.error(f"Database error on attempt {attempt + 1}: {error_str}")

                # Check if it's a connection error
                if "connection" in error_str.lower() or "server closed" in error_str.lower():
                    if attempt < max_retries - 1:
                        logger.info("Connection error detected, attempting to reconnect...")
                        if self._reconnect():
                            logger.info("Reconnection successful, retrying query...")
                            continue  # Retry the query
                        else:
                            logger.error("Reconnection failed")

                    # Final attempt failed or reconnection failed
                    return [{"error": "Unable to connect to the database. Please try again in a moment or contact support if the issue persists."}]

                # For other database errors (syntax, permission, etc.)
                logger.error(f"Non-connection database error: {error_str}")
                return [{"error": "There was an issue retrieving your preauthorization information. Please try rephrasing your question or contact support."}]

        # Should not reach here, but just in case
        return [{"error": "Unable to process your request after multiple attempts. Please contact support."}]
    
    def format_answer(self, query: str, sql_query: str, sql_result: List[Dict]) -> str:
        """Format SQL results into natural language answer using LLM intelligence"""

        # Handle error results with user-friendly messages
        if len(sql_result) == 1:
            if "error" in sql_result[0]:
                return sql_result[0]["error"]
            if "message" in sql_result[0]:
                return sql_result[0]["message"]

        # Use LLM to format the response intelligently
        messages = [
            {
                "role": "system",
                "content": f"""You are a helpful insurance preauthorization assistant. Convert SQL query results into clear, natural language responses.

DATABASE SCHEMA:
{self.db_schema}

**ANTI-HALLUCINATION RULES** (CRITICAL):
1. ⚠️ ONLY present data from the QUERY RESULTS below - DO NOT add, modify, or invent any information
2. ⚠️ If a field is NULL or empty in results, say "not provided" or "not available" - NEVER make up values
3. ⚠️ DO NOT invent preauth details, procedure/medication names, dates, costs, or status information
4. ⚠️ Use EXACT values from the query results - do not paraphrase numbers, dates, statuses, or costs
5. ⚠️ If query results are empty, say "No preauthorization requests found" - do not suggest possible reasons

FORMATTING RULES:
1. Be conversational and friendly
2. Format dates in readable format (e.g., "January 15, 2024") ONLY if date exists in results
3. Present preauthorization information clearly and organized
4. For status, use the EXACT status from database (PENDING, APPROVED, DENIED, PARTIALLY_APPROVED)
5. For procedure/medication details (JSON), format them as bullet points using ONLY the actual data from results
6. For costs, always show currency as AED (e.g., "AED 5,500.00")
7. If multiple requests, show them in numbered list with EXACT data from each row
8. Keep responses concise but informative
9. Always be helpful and professional
10. NEVER assume or add information not in the results

USER'S ORIGINAL QUESTION: {query}
SQL QUERY USED: {sql_query}
QUERY RESULTS: {json.dumps(sql_result, default=str)}

Provide a clear, helpful response using ONLY the data from query results above."""
            }
        ]

        response = self.llm.invoke(messages)
        return response.content.strip()

    def get_schema_info(self) -> str:
        """Return schema information for debugging"""
        return self.db_schema
        
    def get_last_query(self) -> str:
        """Return the last generated SQL query for debugging"""
        return self.last_sql_query or "No query generated yet"