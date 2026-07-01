import os
# from typing import TypedDict, List, Optional, Dict, Any, Annotated
# from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
# from langgraph.graph import StateGraph, END
# import re
# import operator
# import os
# import logging
# from langchain_groq import ChatGroq
# from langchain_community.vectorstores import FAISS
# from sqlagent.sqldatabaseagent import SQLDatabaseAgent
# from chatbot.chat_bot import *

# # Set up logging with UTF-8 encoding for Windows compatibility
# import sys
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('./chatbot.log', encoding='utf-8'),
#         logging.StreamHandler(sys.stdout)
#     ]
# )
# # Force stdout to use UTF-8 encoding on Windows
# if sys.platform == 'win32':
#     sys.stdout.reconfigure(encoding='utf-8')
# logger = logging.getLogger(__name__)

# # Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
# MODEL_NAME = "llama-3.1-8b-instant"

# # PostgreSQL connection from environment variables
# DATABASE_URL = os.getenv('DATABASE_URL')
# if not DATABASE_URL:
#     # Fallback: construct from individual env vars
#     POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
#     POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
#     POSTGRES_DB = os.getenv('POSTGRES_DB', 'aidevdb')
#     POSTGRES_USER = os.getenv('POSTGRES_USER', 'aidev')
#     POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'aidev123')
#     DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# DB_CONNECTION = DATABASE_URL

# # Policy credentials database (Policy Number → Email mapping)
# POLICY_CREDENTIALS = {
#     "POL-776620": "maria.santos@email.com",
#     "POL-445521": "fatima.shamsi@email.com",
#     "POL-667788": "ali.hammadi@email.com",
#     "POL-889900": "aisha.mazrouei@email.com",
#     "POL-112233": "khalid.qasemi@email.com"
# }

# # Static OTP for authentication
# STATIC_OTP = "12345"

# # Constants for intent classification
# PERSONAL_KEYWORDS = [
#     'my preauth', 'my preauthorization', 'my authorization', 'my request', 'my requests',
#     'my status', 'preauth status', 'authorization status', 'request status',
#     'my procedure', 'my medication', 'my treatment',
#     'my approval', 'my denial', 'approval number', 'my details', 'my information',
#     'my account', 'personal information', 'customer id', 'existing customer',
#     'authenticate', 'verify my identity',
#     'my cost', 'approved cost', 'estimated cost'
# ]

# GENERAL_KEYWORDS = [
#     'policies', 'insurance', 'coverage', 'premium', 'benefits',
#     'what is', 'how does', 'explain', 'tell me about', 'information about',
#     'available', 'types of', 'kinds of', 'options', 'plans', 'products',
#     'help', 'assist', 'support', 'hello', 'hi', 'greet',
#     'preauthorization process', 'how to get preauth', 'preauth requirements'
# ]

# DB_KEYWORDS = [
#     'my preauth', 'my preauthorization', 'my request', 'my requests',
#     'preauth status', 'authorization status', 'request status',
#     'my procedure', 'my medication', 'procedure details', 'medication details',
#     'my approval', 'approval number', 'denied request', 'denied requests',
#     'my details', 'my information', 'request details', 'request information',
#     'my history', 'request history', 'authorization history',
#     'latest request', 'recent requests', 'pending requests', 'approved requests',
#     'my cost', 'approved cost', 'estimated cost', 'partial approval'
# ]

# # Keywords that indicate process/how-to questions (should NOT trigger DB, use RAG instead)
# PROCESS_KEYWORDS = [
#     'how to', 'how can i', 'how do i', 'how does', 'how should i', 'how would i',
#     'apply for', 'apply new', 'submit new', 'file new', 'create new', 'make new',
#     'start new', 'begin new', 'initiate new', 'open new',
#     'steps to', 'process for', 'procedure for', 'requirements for', 'process of',
#     'what documents', 'which documents', 'documents needed', 'documents required',
#     'what do i need', 'what should i', 'what are the steps', 'what is the process',
#     'eligibility', 'eligible for', 'qualify for', 'can i get', 'am i eligible',
#     'where to', 'where can i', 'where do i', 'when to', 'when can i', 'when do i'
# ]
# # State definitions
# class AuthenticationState(TypedDict):
#     customer_id: Optional[str]
#     email: Optional[str]
#     otp_sent: bool
#     otp_verified: bool
#     auth_attempts: int
#     auth_step: str  # 'none', 'waiting_customer_id', 'waiting_otp', 'completed'

# class ChatState(TypedDict):
#     messages: Annotated[List[AnyMessage], operator.add]
#     user_input: str
#     intent: str
#     user_authenticated: bool
#     user_id: Optional[str]
#     session_data: Dict[str, Any]
#     requires_db: bool
#     needs_authentication: bool
#     response: str
#     context: str
#     sql_query: str
#     query: str
#     sql_result: str
#     final_answer: str
#     auth_state: AuthenticationState
#     auth_needs_response: bool
#     auth_completed: bool

# class ChatApp:
#     def __init__(self, vector_store=None, vector_store1=None, temp=0.7):
#         logger.info("Initializing ChatApp...")
        
#         if not GROQ_API_KEY:
#             raise ValueError("GROQ_API_KEY not found")
        
#         self.vector_store = vector_store
#         self.vector_store1 = vector_store1
#         self.temp = temp
        
#         # Initialize LLM and SQL agent
#         try:
#             self.llm = ChatGroq(api_key=GROQ_API_KEY, model_name=MODEL_NAME)
#             self.sql_agent = SQLDatabaseAgent(DB_CONNECTION, self.llm)
#         except Exception as e:
#             logger.error(f"Failed to initialize LLM or SQL agent: {e}")
#             self.llm = None
#             self.sql_agent = None
        
#         # Initialize clean session state
#         self._reset_session_state()
        
#         # Initialize workflow
#         self._build_workflow()
#         logger.info("ChatApp initialized successfully")

#     def _reset_session_state(self):
#         """Initialize/reset session state to clean defaults"""
#         self.session_state = {
#             'user_authenticated': False,
#             'user_id': None,
#             'auth_state': {
#                 'customer_id': None,
#                 'email': None,
#                 'otp_sent': False,
#                 'otp_verified': False,
#                 'auth_attempts': 0,
#                 'auth_step': 'none'
#             },
#             'conversation_history': []
#         }

#     def _build_workflow(self):
#         """Build the conversation workflow with proper error handling"""
#         try:
#             workflow = StateGraph(ChatState)
            
#             # Add nodes
#             workflow.add_node('intent_classifier', self.intent_classifier)
#             workflow.add_node('authentication_layer', self.authentication_layer)
#             workflow.add_node('database_connection_layer', self.database_connection_layer)
#             workflow.add_node('general_chat', self.general_chat)
#             workflow.add_node('generate_sql', self.generate_sql)
#             workflow.add_node('execute_sql', self.execute_sql)
#             workflow.add_node('format_answer', self.format_answer)
#             workflow.add_node('generate_direct_answer', self.generate_direct_answer)
#             workflow.add_node('auth_response', self.auth_response)
            
#             # Add conditional edges with proper routing
#             workflow.add_conditional_edges(
#                 'intent_classifier', 
#                 self.route_intent,
#                 {
#                     "personal_details": 'authentication_layer', 
#                     "general_details": 'general_chat'
#                 }
#             )
            
#             workflow.add_conditional_edges(
#                 'authentication_layer', 
#                 self.route_authentication,
#                 {
#                     'authenticated': 'database_connection_layer', 
#                     'need_auth_response': 'auth_response'
#                 }
#             )
            
#             workflow.add_conditional_edges(
#                 'database_connection_layer', 
#                 self.route_database_query,
#                 {
#                     "sql_needed": "generate_sql",
#                     "direct_answer": "generate_direct_answer"
#                 }
#             )
            
#             # Add edges to END
#             workflow.add_edge('generate_sql', 'execute_sql')
#             workflow.add_edge('execute_sql', 'format_answer')
#             workflow.add_edge('format_answer', END)
#             workflow.add_edge('generate_direct_answer', END)
#             workflow.add_edge('general_chat', END)
#             workflow.add_edge('auth_response', END)
            
#             workflow.set_entry_point('intent_classifier')
#             self.graph = workflow.compile()
            
#         except Exception as e:
#             logger.error(f"Failed to build workflow: {e}")
#             raise

#     def _is_policy_number_format(self, text: str) -> bool:
#         """Check if text contains policy number format (POL-XXXXXX)"""
#         return bool(re.search(r'POL-\d{6}', text.upper()))

#     def _extract_policy_number(self, text: str) -> Optional[str]:
#         """Extract policy number from text"""
#         match = re.search(r'POL-\d{6}', text.upper())
#         return match.group().upper() if match else None

#     def _is_otp_format(self, text: str) -> bool:
#         """Check if text is in OTP format"""
#         return bool(re.match(r'^\d{5}$', text.strip()))

#     def _extract_otp(self, text: str) -> Optional[str]:
#         """Extract OTP from text"""
#         # Try exact match first
#         if re.match(r'^\d{5}$', text.strip()):
#             return text.strip()
#         # Try to find 5 digits in the text
#         match = re.search(r'\b(\d{5})\b', text)
#         return match.group(1) if match else None

#     def _has_personal_keywords(self, text: str) -> bool:
#         """Check if text contains personal data keywords"""
#         text_lower = text.lower()
#         return any(keyword in text_lower for keyword in PERSONAL_KEYWORDS)

#     def _has_general_keywords(self, text: str) -> bool:
#         """Check if text contains general query keywords"""
#         text_lower = text.lower()
#         return any(keyword in text_lower for keyword in GENERAL_KEYWORDS)

#     def _has_db_keywords(self, text: str) -> bool:
#         """Check if text requires database access"""
#         text_lower = text.lower()
#         return any(keyword in text_lower for keyword in DB_KEYWORDS)

#     def _is_process_question(self, text: str) -> bool:
#         """Check if text is asking about a process/how-to (should use RAG, not DB)"""
#         text_lower = text.lower()
#         return any(keyword in text_lower for keyword in PROCESS_KEYWORDS)

#     def _classify_with_llm(self, query: str, is_authenticated: bool) -> str:
#         """Use LLM to classify ambiguous queries (slow path)"""
#         try:
#             auth_context = "The user is authenticated" if is_authenticated else "The user is NOT authenticated"

#             messages = [
#                 {
#                     "role": "system",
#                     "content": f"""You are an intent classifier for an insurance preauthorization chatbot. Classify the user's query into ONE of these intents:

# 1. **personal_details**: User wants their personal preauthorization data from database
#    - Examples: "my preauth", "my request status", "show my procedures", "my account", "my details", "my approvals"
#    - Requires authentication

# 2. **general_details**: User wants general information (uses RAG knowledge base)
#    - Examples: "how to get preauth", "what is preauthorization", "preauth process", "eligibility criteria"
#    - Does NOT require authentication

# CONTEXT: {auth_context}

# CLASSIFICATION RULES (STRICT - DO NOT DEVIATE):
# - If query contains "my", "show my", "get my" → classify as personal_details
# - If query contains "how to", "what is", "process for" → classify as general_details
# - If user is authenticated and asks about preauth/requests WITHOUT "my" → classify as personal_details
# - If user is NOT authenticated and asks about preauth/requests → classify as general_details
# - DO NOT make assumptions beyond these rules
# - When in doubt, default to general_details

# USER QUERY: {query}

# ⚠️ CRITICAL: Respond with EXACTLY ONE of these two words (nothing else): "personal_details" OR "general_details"
# """
#                 }
#             ]

#             response = self.llm.invoke(messages)
#             intent = response.content.strip().lower()

#             # Remove any extra whitespace, quotes, or punctuation
#             intent = intent.replace('"', '').replace("'", '').replace('.', '').strip()

#             # Strict validation - only allow exact matches
#             if intent == 'personal_details':
#                 logger.debug(f"LLM classified intent as: personal_details")
#                 return 'personal_details'
#             elif intent == 'general_details':
#                 logger.debug(f"LLM classified intent as: general_details")
#                 return 'general_details'
#             else:
#                 # If LLM hallucinated or returned invalid response, log and fallback
#                 logger.warning(f"LLM returned invalid/hallucinated intent '{intent}', defaulting to general_details (safe fallback)")
#                 return 'general_details'

#         except Exception as e:
#             logger.error(f"Error in LLM classification: {e}, defaulting to general_details")
#             return 'general_details'


#     def intent_classifier(self, state: ChatState) -> ChatState:
#         """Classify user intent with clear, logical rules"""
#         logger.debug("=== INTENT CLASSIFIER START ===")
        
#         try:
#             # Get and clean current query
#             current_query = state.get('user_input', '').strip()
#             if not current_query:
#                 state['intent'] = 'general_details'
#                 return state
                
#             state['query'] = current_query
            
#             logger.debug(f"Current query: '{current_query}'")
#             logger.debug(f"User authenticated: {state.get('user_authenticated', False)}")
            
#             # Initialize auth_state if missing
#             if 'auth_state' not in state or state['auth_state'] is None:
#                 state['auth_state'] = {
#                     'customer_id': None,
#                     'email': None,
#                     'otp_sent': False,
#                     'otp_verified': False,
#                     'auth_attempts': 0,
#                     'auth_step': 'none'
#                 }
            
#             auth_state = state['auth_state']
#             is_authenticated = state.get('user_authenticated', False)
            
#             # Rule 1: If user is actively in authentication process
#             if auth_state.get('auth_step') == 'waiting_policy_number':
#                 if self._is_policy_number_format(current_query):
#                     logger.debug("User providing policy number during auth process")
#                     state['intent'] = 'personal_details'
#                     return state
#                 else:
#                     # User didn't provide policy number, treat as general query
#                     logger.debug("User didn't provide policy number, treating as general")
#                     state['intent'] = 'general_details'
#                     auth_state['auth_step'] = 'none'  # Reset auth
#                     return state
            
#             # Rule 2: If user is waiting for OTP
#             if auth_state.get('auth_step') == 'waiting_otp':
#                 if self._is_otp_format(current_query):
#                     logger.debug("User providing OTP during auth process")
#                     state['intent'] = 'personal_details'
#                     return state
#                 else:
#                     # User didn't provide OTP, treat as general query
#                     logger.debug("User didn't provide OTP, treating as general")
#                     state['intent'] = 'general_details'
#                     auth_state['auth_step'] = 'none'  # Reset auth
#                     return state
            
#             # Check for keywords
#             has_policy_number = self._is_policy_number_format(current_query)
#             has_personal_request = self._has_personal_keywords(current_query)
#             has_general_request = self._has_general_keywords(current_query)
#             is_process_question = self._is_process_question(current_query)

#             # Rule 3: If already authenticated, use HYBRID smart routing
#             if is_authenticated:
#                 logger.debug(f"User already authenticated as {state.get('user_id', 'unknown')}")

#                 # FAST PATH: Check obvious patterns first (keyword-based)

#                 # PRIORITY 1: Process/how-to questions always go to general (RAG)
#                 if is_process_question:
#                     state['intent'] = 'general_details'
#                     logger.debug("[FAST PATH] Process/how-to question → general_details")
#                     return state

#                 # PRIORITY 2: Explicit personal data requests (strong signals)
#                 if (has_policy_number or
#                     any(keyword in current_query.lower() for keyword in
#                         ['my preauth', 'my request', 'my requests', 'show my', 'get my', 'my details', 'my information', 'my account', 'my policy'])):
#                     state['intent'] = 'personal_details'
#                     logger.debug("[FAST PATH] Explicit personal request → personal_details")
#                     return state

#                 # PRIORITY 3: Strong general keywords (no personal indicators)
#                 if has_general_request and not has_personal_request:
#                     state['intent'] = 'general_details'
#                     logger.debug("[FAST PATH] General request detected → general_details")
#                     return state

#                 # SLOW PATH: Ambiguous case - use LLM for intelligent classification
#                 logger.debug("[SLOW PATH] Ambiguous query, using LLM classification")
#                 state['intent'] = self._classify_with_llm(current_query, is_authenticated=True)
#                 logger.debug(f"[SLOW PATH] LLM classified as: {state['intent']}")
#                 return state

#             # Rule 4: For unauthenticated users - also use HYBRID approach

#             # FAST PATH: Check obvious patterns
#             if has_policy_number or has_personal_request:
#                 logger.debug("[FAST PATH] Personal data request (unauthenticated) → personal_details")
#                 state['intent'] = 'personal_details'
#                 return state

#             if has_general_request or is_process_question:
#                 logger.debug("[FAST PATH] General request (unauthenticated) → general_details")
#                 state['intent'] = 'general_details'
#                 return state

#             # SLOW PATH: Ambiguous query for unauthenticated user
#             logger.debug("[SLOW PATH] Ambiguous query (unauthenticated), using LLM classification")
#             state['intent'] = self._classify_with_llm(current_query, is_authenticated=False)
#             logger.debug(f"[SLOW PATH] LLM classified as: {state['intent']}")
            
#         except Exception as e:
#             logger.error(f"Error in intent classifier: {e}")
#             state['intent'] = 'general_details'  # Safe fallback
            
#         logger.debug("=== INTENT CLASSIFIER END ===")
#         return state

   
#     def authentication_layer(self, state: ChatState) -> ChatState:
#         """Handle authentication with clear state management"""
#         logger.debug("=== AUTHENTICATION LAYER START ===")
        
#         try:
#             current_message = state.get('user_input', '').strip()
#             auth_state = state['auth_state']
            
#             logger.debug(f"Current message: '{current_message}'")
#             logger.debug(f"Auth step: {auth_state['auth_step']}")
            
#             # Check if already authenticated
#             if state.get('user_authenticated', False):
#                 logger.debug("User already authenticated, proceeding")
#                 return state
            
#             # Start authentication process if needed
#             if auth_state['auth_step'] == 'none':
#                 # Check if user provided policy number directly
#                 if self._is_policy_number_format(current_message):
#                     auth_state['auth_step'] = 'waiting_policy_number'
#                 else:
#                     # Request policy number
#                     auth_state['auth_step'] = 'waiting_policy_number'
#                     state['response'] = "To access your preauthorization information, please provide your Policy Number (format: POL-776620)."
#                     state['auth_needs_response'] = True
#                     return state

#             # Handle policy number input
#             if auth_state['auth_step'] == 'waiting_policy_number':
#                 extracted_policy = self._extract_policy_number(current_message)

#                 if extracted_policy:
#                     logger.debug(f"Extracted policy number: {extracted_policy}")

#                     if extracted_policy in POLICY_CREDENTIALS:
#                         # Valid policy number
#                         auth_state['customer_id'] = extracted_policy  # Store as customer_id for backward compatibility
#                         auth_state['email'] = POLICY_CREDENTIALS[extracted_policy]
#                         auth_state['auth_step'] = 'waiting_otp'
#                         auth_state['otp_sent'] = True

#                         state['response'] = f"Thank you! I found your policy. An OTP has been sent to your registered email {auth_state['email']}. Please enter the 5-digit OTP to complete authentication."
#                         state['auth_needs_response'] = True
#                         logger.debug("Policy number validated, requesting OTP")
#                         return state
#                     else:
#                         # Invalid policy number
#                         auth_state['auth_attempts'] += 1
#                         if auth_state['auth_attempts'] >= 3:
#                             self._reset_auth_state(auth_state)
#                             state['response'] = "Too many failed attempts. Please contact customer service for assistance."
#                             state['auth_needs_response'] = True
#                             return state

#                         state['response'] = f"Policy Number {extracted_policy} not found. Please check and try again. (Attempt {auth_state['auth_attempts']} of 3)"
#                         state['auth_needs_response'] = True
#                         return state
#                 else:
#                     # No valid policy number found
#                     state['response'] = "Please provide a valid Policy Number in the format POL-776620."
#                     state['auth_needs_response'] = True
#                     return state
            
#             # Handle OTP input
#             elif auth_state['auth_step'] == 'waiting_otp':
#                 extracted_otp = self._extract_otp(current_message)
                
#                 if extracted_otp:
#                     logger.debug(f"Validating OTP: '{extracted_otp}' against '{STATIC_OTP}'")
                    
#                     if extracted_otp == STATIC_OTP:
#                         # Successful authentication
#                         auth_state['otp_verified'] = True
#                         auth_state['auth_step'] = 'completed'
#                         state['user_authenticated'] = True
#                         state['user_id'] = auth_state['customer_id']
#                         state['auth_completed'] = True

#                         # Welcome message after successful authentication
#                         state['response'] = f"Authentication successful! Welcome, {state['user_id']}. You can now ask me about your preauthorization requests, status, costs, or any other details. How can I help you today?"
#                         state['auth_needs_response'] = True

#                         # Use ASCII instead of Unicode checkmark
#                         logger.info(f"[SUCCESS] User {state['user_id']} authenticated successfully")
#                         return state
#                     else:
#                         # Wrong OTP
#                         auth_state['auth_attempts'] += 1
#                         if auth_state['auth_attempts'] >= 3:
#                             self._reset_auth_state(auth_state)
#                             state['response'] = "Too many failed OTP attempts. Please contact customer service."
#                             state['auth_needs_response'] = True
#                             return state
                        
#                         state['response'] = f"Incorrect OTP '{extracted_otp}'. Please try again. (Attempt {auth_state['auth_attempts']} of 3)"
#                         state['auth_needs_response'] = True
#                         return state
#                 else:
#                     # No valid OTP found
#                     state['response'] = f"Please enter the 5-digit OTP sent to {auth_state['email']}."
#                     state['auth_needs_response'] = True
#                     return state
            
#             # Fallback
#             state['response'] = "Authentication process error. Please provide your Customer ID to start over."
#             state['auth_needs_response'] = True
#             self._reset_auth_state(auth_state)
            
#         except Exception as e:
#             logger.error(f"Error in authentication layer: {e}")
#             state['response'] = "Authentication error occurred. Please try again."
#             state['auth_needs_response'] = True
#             self._reset_auth_state(state['auth_state'])
            
#         logger.debug("=== AUTHENTICATION LAYER END ===")
#         return state

#     def _reset_auth_state(self, auth_state: dict):
#         """Reset authentication state to initial values"""
#         auth_state.update({
#             'customer_id': None,
#             'email': None,
#             'otp_sent': False,
#             'otp_verified': False,
#             'auth_attempts': 0,
#             'auth_step': 'none'
#         })

#     def auth_response(self, state: ChatState) -> ChatState:
#         """Handle authentication responses"""
#         logger.debug("=== AUTH RESPONSE ===")
#         state['final_answer'] = state.get('response', 'Please provide your authentication details.')
#         return state

    
#     def database_connection_layer(self, state: ChatState) -> ChatState:
#         """Determine if query needs database access with smart routing"""
#         logger.debug("=== DATABASE CONNECTION LAYER ===")

#         try:
#             current_query = state.get('query', '').lower()
#             user_authenticated = state.get('user_authenticated', False)

#             logger.debug(f"Analyzing query for DB requirement: '{current_query}'")
#             logger.debug(f"User authenticated: {user_authenticated}")

#             # For authenticated users - full privilege access with smart routing
#             if user_authenticated:
#                 # PRIORITY 1: Check if this is a process/how-to question (should use RAG, not DB)
#                 if self._is_process_question(current_query):
#                     requires_db = False
#                     logger.debug("Process/how-to question detected - routing to general chat (RAG)")
#                     state['requires_db'] = requires_db
#                     return state

#                 # PRIORITY 2: Check if this is a greeting or help request
#                 general_only_keywords = [
#                     'hello', 'hi', 'help', 'what can you do', 'how can you help',
#                     'what is insurance', 'types of policies', 'available policies'
#                 ]

#                 if any(keyword in current_query for keyword in general_only_keywords):
#                     requires_db = False
#                     logger.debug("General greeting/help detected - routing to general chat")
#                     state['requires_db'] = requires_db
#                     return state

#                 # PRIORITY 3: Check if this is a personal data request (needs DB)
#                 # Use more specific keywords to avoid false positives
#                 personal_db_keywords = [
#                     'show my preauth', 'get my preauth', 'my preauth', 'my preauthorization',
#                     'show my request', 'my request', 'my requests',
#                     'show my procedure', 'my procedure', 'my medication',
#                     'show my details', 'my details', 'my information',
#                     'my history', 'my status', 'authorization history',
#                     'request history', 'latest request', 'recent requests',
#                     'what is my', 'show me my', 'get my', 'find my',
#                     'my approval', 'my denial', 'approved cost', 'my cost'
#                 ]

#                 requires_db = any(keyword in current_query for keyword in personal_db_keywords)

#                 if requires_db:
#                     logger.debug("Personal data request detected - routing to database")
#                 else:
#                     logger.debug("No personal data request detected - routing to general chat (RAG)")

#             else:
#                 # For unauthenticated users, no DB access
#                 requires_db = False
#                 logger.debug("User not authenticated - no DB access")

#             state['requires_db'] = requires_db
#             logger.debug(f"Final decision - Database required: {requires_db}")

#         except Exception as e:
#             logger.error(f"Error in database connection layer: {e}")
#             state['requires_db'] = False

#         return state

#     def general_chat(self, state: ChatState) -> ChatState:
#         """Handle general chat queries with personalized responses for authenticated users"""
#         logger.debug("=== GENERAL CHAT ===")

#         try:
#             current_query = state.get('query', '')
#             user_id = state.get('user_id', None)
#             user_authenticated = state.get('user_authenticated', False)

#             logger.debug(f"Processing general query: '{current_query}'")
#             logger.debug(f"User authenticated: {user_authenticated}, User ID: {user_id}")

#             # Personalized greeting for authenticated users
#             greeting_prefix = f"Hello {user_id}! " if user_authenticated and user_id else ""

#             # Handle common insurance queries

#             # PRIORITY: Check if asking about submitting new preauthorization
#             if any(phrase in current_query.lower() for phrase in [
#                 'submit new preauth', 'new preauthorization', 'submit preauth', 'submit authorization',
#                 'apply for preauth', 'request preauth', 'get preauth', 'need preauth',
#                 'how can i get', 'how do i get', 'how to get', 'how can i submit',
#                 'how do i submit', 'how to submit', 'how can i apply', 'how do i apply',
#                 'how to apply', 'start new request', 'new request', 'submit request'
#             ]):
#                 preauth_submission_info = self._get_preauth_submission_info()
#                 state['final_answer'] = greeting_prefix + preauth_submission_info if greeting_prefix else preauth_submission_info
#             elif any(word in current_query.lower() for word in ['policies', 'policy', 'available', 'types']):
#                 state['final_answer'] = greeting_prefix + self._get_policies_info() if greeting_prefix else self._get_policies_info()
#             elif any(word in current_query.lower() for word in ['help', 'assist', 'support']):
#                 state['final_answer'] = greeting_prefix + self._get_help_info() if greeting_prefix else self._get_help_info()
#             elif any(word in current_query.lower() for word in ['hello', 'hi', 'greet']):
#                 if user_authenticated and user_id:
#                     state['final_answer'] = f"Hello {user_id}! Welcome back to CAN Insurance (UAE). I can help you with information about our insurance policies, coverage options, preauthorization requests, and more. You also have access to your personal preauthorization information. How can I assist you today?"
#                 else:
#                     state['final_answer'] = "Hello! Welcome to CAN Insurance (UAE). I can help you with information about our insurance policies, coverage options, preauthorization process, and more. How can I assist you today?"
#             else:
#                 # Use RAG if available, otherwise provide general response
#                 if self.vector_store:
#                     try:
#                         # Import the function from chat_bot module
#                         from chatbot.chat_bot import initialize_qa_chain

#                         rag_chain = initialize_qa_chain(self.vector_store, self.vector_store1, self.temp)
#                         if rag_chain:
#                             logger.debug("RAG chain initialized, invoking with query")
#                             response = rag_chain.invoke({
#                                 "input": current_query,
#                                 "chat_history": []
#                             })

#                             if isinstance(response, dict) and 'answer' in response:
#                                 answer = response['answer']
#                             else:
#                                 answer = str(response)

#                             # Add personalized prefix for authenticated users
#                             if greeting_prefix and not answer.startswith(user_id if user_id else ""):
#                                 state['final_answer'] = greeting_prefix + answer
#                             else:
#                                 state['final_answer'] = answer
#                             logger.debug("RAG response generated successfully")
#                         else:
#                             logger.warning("RAG chain returned None")
#                             state['final_answer'] = greeting_prefix + self._get_default_response() if greeting_prefix else self._get_default_response()
#                     except Exception as e:
#                         logger.error(f"RAG error: {e}", exc_info=True)
#                         state['final_answer'] = greeting_prefix + self._get_default_response() if greeting_prefix else self._get_default_response()
#                 else:
#                     logger.warning("Vector store not available, using default response")
#                     state['final_answer'] = greeting_prefix + self._get_default_response() if greeting_prefix else self._get_default_response()

#             logger.debug("General chat response generated")

#         except Exception as e:
#             logger.error(f"Error in general chat: {e}")
#             state['final_answer'] = "I apologize, but I encountered an error. How can I help you with insurance information?"

#         return state

#     def _get_policies_info(self) -> str:
#         """Get information about available policies"""
#         return """We offer various insurance policies including:

# • **Life Insurance** - Term and Whole Life policies to protect your family's future
# • **Health Insurance** - Comprehensive individual and family health plans
# • **Auto Insurance** - Complete vehicle protection with liability and comprehensive coverage
# • **Home Insurance** - Property protection for your home and belongings
# • **Travel Insurance** - Coverage for domestic and international travel

# Each policy comes with flexible terms and competitive rates. For specific details about any policy or to get a personalized quote, please let me know what interests you!

# To access your existing policy details, please provide your Policy Number for authentication."""

#     def _get_help_info(self) -> str:
#         """Get help information"""
#         return """I'm here to help you with:

# • **Policy Information** - Details about our insurance products
# • **Coverage Options** - Understanding what's covered under each policy
# • **Preauthorization Process** - How to submit and track authorization requests
# • **Medical Procedures** - Understanding coverage for surgeries and treatments
# • **Medications** - High-cost medication authorization process
# • **Account Access** - View your personal preauthorization status (requires Policy Number)

# What specific information would you like to know about?"""

#     def _get_preauth_submission_info(self) -> str:
#         """Get information about submitting new preauthorization requests"""
#         return """To submit a new preauthorization request, please contact:

# 📧 **Email:** canvendor1@gmail.com
# 📞 **Phone:** 1-800-UAE-PREAUTH

# Required information:
# • Policy Number
# • Emirates ID
# • Procedure/Medication details (codes, names, dosages)
# • Clinical justification from your provider
# • Provider details and license number
# • Estimated cost

# Our team will review your request and respond within 2-5 business days. Track your request status by logging in with your Policy Number.

# For urgent requests, please mark as URGENT in your submission."""

#     def _get_default_response(self) -> str:
#         """Get default response for general queries"""
#         return "I'm here to help you with insurance-related questions. You can ask me about our policies, coverage options, preauthorization process, or any other insurance topics. For personal account information, please provide your Policy Number. How can I assist you today?"

#     def generate_sql(self, state: ChatState) -> ChatState:
#         """Generate SQL query with error handling"""
#         logger.debug("=== GENERATE SQL ===")

#         try:
#             if not self.sql_agent:
#                 state["sql_query"] = "SELECT 'SQL agent not available' as error"
#                 return state

#             query = state.get('query', '').strip()
#             policy_number = state.get('user_id', '')  # user_id stores the policy number

#             # Prepend policy number to query for SQL generation
#             if policy_number:
#                 query_with_policy = f"For policy {policy_number}: {query}"
#                 logger.debug(f"Generating SQL for: '{query_with_policy}'")
#                 state["sql_query"] = self.sql_agent.generate_sql(query_with_policy)
#             else:
#                 logger.warning("No policy_number found in state, generating SQL without policy filter")
#                 state["sql_query"] = self.sql_agent.generate_sql(query)

#             logger.debug(f"Generated SQL: {state['sql_query']}")

#         except Exception as e:
#             logger.error(f"Error generating SQL: {e}")
#             state["sql_query"] = f"SELECT 'Error generating SQL: {str(e)}' as error"

#         return state
        
#     def execute_sql(self, state: ChatState) -> ChatState:
#         """Execute SQL query with error handling"""
#         logger.debug("=== EXECUTE SQL ===")
        
#         try:
#             if not self.sql_agent:
#                 state["sql_result"] = [{"error": "SQL agent not available"}]
#                 return state
                
#             sql_query = state.get("sql_query", "")
#             logger.debug(f"Executing SQL: {sql_query}")
            
#             state["sql_result"] = self.sql_agent.execute_sql(sql_query)
#             logger.debug("SQL execution completed")
            
#         except Exception as e:
#             logger.error(f"Error executing SQL: {e}")
#             state["sql_result"] = [{"error": f"Error executing query: {str(e)}"}]
            
#         return state
    
#     def format_answer(self, state: ChatState) -> ChatState:
#         """Format SQL results into final answer"""
#         logger.debug("=== FORMAT ANSWER ===")
        
#         try:
#             if not self.sql_agent:
#                 state["final_answer"] = "Database service is currently unavailable."
#                 return state
                
#             state["final_answer"] = self.sql_agent.format_answer(
#                 state.get("query", ""),
#                 state.get("sql_query", ""),
#                 state.get("sql_result", [])
#             )
#             logger.debug("SQL answer formatted")
            
#         except Exception as e:
#             logger.error(f"Error formatting answer: {e}")
#             state["final_answer"] = "I apologize, but I encountered an error while processing your request."
            
#         return state
    
#     def generate_direct_answer(self, state: ChatState) -> ChatState:
#         """Generate direct answer for authenticated users"""
#         logger.debug("=== GENERATE DIRECT ANSWER ===")
        
#         try:
#             current_query = state.get('query', '')
#             user_id = state.get('user_id', 'valued customer')
            
#             logger.debug(f"Generating direct answer for {user_id}: '{current_query}'")
            
#             # Provide personalized response for authenticated user
#             if self.vector_store and hasattr(self, 'initialize_qa_chain'):
#                 try:
#                     rag_chain = initialize_qa_chain(self.vector_store, self.vector_store1, self.temp)
#                     if rag_chain:
#                         prompt = f"You are helping an authenticated customer ({user_id}). Respond to: {current_query}"
#                         response = rag_chain.invoke({
#                             "input": prompt, 
#                             "chat_history": []
#                         })
                        
#                         if isinstance(response, dict) and 'answer' in response:
#                             state['final_answer'] = response['answer']
#                         else:
#                             state['final_answer'] = str(response)
#                     else:
#                         state['final_answer'] = f"Hello {user_id}! I'm here to help with your insurance needs. How can I assist you today?"
#                 except Exception as e:
#                     logger.error(f"RAG error: {e}")
#                     state['final_answer'] = f"Hello {user_id}! I'm here to help with your insurance questions."
#             else:
#                 state['final_answer'] = f"Hello {user_id}! I can help you with your insurance information and general queries."
            
#             logger.debug("Direct answer generated")
            
#         except Exception as e:
#             logger.error(f"Error in direct answer: {e}")
#             state['final_answer'] = "I'm here to help with your insurance questions."
            
#         return state

#     # Routing functions with simplified logic
#     def route_intent(self, state: ChatState) -> str:
#         """Route based on intent classification"""
#         intent = state.get('intent', 'general_details')
#         logger.debug(f"Routing intent: {intent}")
#         return intent

#     def route_authentication(self, state: ChatState) -> str:
#         """Route based on authentication status"""
#         try:
#             user_auth = state.get('user_authenticated', False)
#             auth_state = state.get('auth_state', {})
#             auth_needs_response = state.get('auth_needs_response', False)
#             otp_verified = auth_state.get('otp_verified', False)
            
#             logger.debug(f"Routing auth: user_auth={user_auth}, otp_verified={otp_verified}, needs_response={auth_needs_response}")
            
#             if user_auth and otp_verified:
#                 return 'authenticated'
#             else:
#                 return 'need_auth_response'
                
#         except Exception as e:
#             logger.error(f"Error in auth routing: {e}")
#             return 'need_auth_response'

#     def route_database_query(self, state: ChatState) -> str:
#         """Route based on database requirement"""
#         try:
#             route = "sql_needed" if state.get('requires_db', False) else "direct_answer"
#             logger.debug(f"Routing database query: {route}")
#             return route
#         except Exception as e:
#             logger.error(f"Error in database routing: {e}")
#             return "direct_answer"

#     def chat(self, user_input: str, messages: List[AnyMessage] = None) -> str:
#         """Main chat interface with robust error handling"""
#         try:
#             # Validate input
#             if not user_input or not user_input.strip():
#                 return "Please provide a valid question or message."
            
#             user_input = user_input.strip()
            
#             logger.info(f"\n{'='*60}")
#             logger.info(f"CHAT START - User: '{user_input}'")
#             logger.info(f"Session Auth: {self.session_state['user_authenticated']}")
#             logger.info(f"Auth Step: {self.session_state['auth_state']['auth_step']}")
#             logger.info(f"{'='*60}")
            
#             # Create state for this interaction
#             current_state = {
#                 'messages': [],
#                 'user_input': user_input,
#                 'query': user_input,
#                 'intent': "",
#                 'user_authenticated': self.session_state['user_authenticated'],
#                 'user_id': self.session_state['user_id'],
#                 'session_data': {},
#                 'requires_db': False,
#                 'needs_authentication': False,
#                 'response': "",
#                 'context': "",
#                 'sql_query': "",
#                 'sql_result': "",
#                 'final_answer': "",
#                 'auth_state': self.session_state['auth_state'].copy(),
#                 'auth_needs_response': False,
#                 'auth_completed': False
#             }
            
#             logger.debug(f"State before workflow: user_auth={current_state['user_authenticated']}, auth_step={current_state['auth_state']['auth_step']}")
            
#             # Run the workflow
#             if not hasattr(self, 'graph') or self.graph is None:
#                 return "System error: Workflow not properly initialized."
                
#             result = self.graph.invoke(current_state)
            
#             logger.debug(f"State after workflow: user_auth={result.get('user_authenticated', False)}, auth_step={result.get('auth_state', {}).get('auth_step', 'unknown')}")
            
#             # Update session state if authentication status changed
#             if result.get('user_authenticated', False) and not self.session_state['user_authenticated']:
#                 self.session_state['user_authenticated'] = True
#                 self.session_state['user_id'] = result.get('user_id')
#                 # Use ASCII instead of Unicode
#                 logger.info(f"[SUCCESS] User authenticated: {result.get('user_id')}")
            
#             # Update auth state
#             if result.get('auth_state'):
#                 self.session_state['auth_state'] = result['auth_state'].copy()
#                 logger.debug(f"Auth state updated: step={self.session_state['auth_state']['auth_step']}")
            
#             # Get final response
#             bot_response = ""
#             if result.get('final_answer'):
#                 bot_response = result['final_answer']
#             elif result.get('response'):
#                 bot_response = result['response']
#             else:
#                 bot_response = "I'm here to help. How can I assist you today?"
            
#             # Update conversation history
#             try:
#                 self.session_state['conversation_history'].append(HumanMessage(content=user_input))
#                 self.session_state['conversation_history'].append(AIMessage(content=bot_response))
                
#                 # Keep history manageable (last 20 messages)
#                 if len(self.session_state['conversation_history']) > 20:
#                     self.session_state['conversation_history'] = self.session_state['conversation_history'][-20:]
#             except Exception as e:
#                 logger.warning(f"Error updating conversation history: {e}")
            
#             logger.info(f"CHAT END - Bot: '{bot_response[:100]}{'...' if len(bot_response) > 100 else ''}'")
#             logger.info(f"{'='*60}\n")
            
#             return bot_response
                
#         except Exception as e:
#             logger.error(f"Critical error in chat: {e}", exc_info=True)
#             return "I apologize, but I encountered an error. Please try again or contact support if the issue persists."

#     def reset_session(self):
#         """Reset the session state"""
#         logger.info("Resetting session state")
#         self._reset_session_state()

#     def get_session_info(self) -> dict:
#         """Get current session information for debugging"""
#         return {
#             'authenticated': self.session_state['user_authenticated'],
#             'user_id': self.session_state['user_id'],
#             'auth_step': self.session_state['auth_state']['auth_step'],
#             'conversation_length': len(self.session_state['conversation_history'])
#         }

# # Test function for development
# def test_chatapp():
#     """Test function to verify ChatApp functionality"""
#     try:
#         # Initialize with None values for testing
#         chatbot = ChatApp(vector_store=None, vector_store1=None, temp=0.7)
        
#         print("=== Testing General Queries ===")
#         response1 = chatbot.chat("what policies are available")
#         print(f"Q: what policies are available")
#         print(f"A: {response1}\n")
        
#         response2 = chatbot.chat("tell me about insurance")
#         print(f"Q: tell me about insurance")
#         print(f"A: {response2}\n")
        
#         print("=== Testing Authentication Flow ===")
#         response3 = chatbot.chat("I want to see my account details")
#         print(f"Q: I want to see my account details")
#         print(f"A: {response3}\n")
        
#         response4 = chatbot.chat("CUS000001")
#         print(f"Q: CUS000001")
#         print(f"A: {response4}\n")
        
#         response5 = chatbot.chat("12345")
#         print(f"Q: 12345")
#         print(f"A: {response5}\n")
        
#         print("=== Session Info ===")
#         print(chatbot.get_session_info())
        
#     except Exception as e:
#         print(f"Test error: {e}")

# if __name__ == "__main__":
#     import sys
    
#     if len(sys.argv) > 1 and sys.argv[1] == "test":
#         test_chatapp()
#     else:
#         print('Welcome to CAN Insurance')
#         print('Type "quit" to end the chat, "reset" to reset session, "info" for session info')
        
#         try:
#             # Initialize the chatbot - you may need to provide actual vector stores
#             chatbot = ChatApp(vector_store=None, vector_store1=None, temp=0.7)
            
#             while True:
#                 try:
#                     query = input('User: ').strip()
                    
#                     if query.lower() == 'quit':
#                         break
#                     elif query.lower() == 'reset':
#                         chatbot.reset_session()
#                         print("Session reset successfully!")
#                         continue
#                     elif query.lower() == 'info':
#                         print(f"Session Info: {chatbot.get_session_info()}")
#                         continue
#                     elif not query:
#                         print("Please enter a valid question.")
#                         continue
                    
#                     # Get response
#                     response = chatbot.chat(query)
#                     print(f"Bot: {response}\n")
                    
#                 except KeyboardInterrupt:
#                     print("\nGoodbye!")
#                     break
#                 except Exception as e:
#                     print(f"Error: {e}")
#                     print("Please try again.")
                    
#         except Exception as e:
#             print(f"Failed to initialize chatbot: {e}")
#             print("Please check your configuration and dependencies.")

from typing import TypedDict, List, Optional, Dict, Any, Annotated
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
import re
import operator
import os
import logging
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from sqlagent.sqldatabaseagent import SQLDatabaseAgent
from chatbot.chat_bot import *

# Set up logging with UTF-8 encoding for Windows compatibility
import sys
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./chatbot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
# Force stdout to use UTF-8 encoding on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
logger = logging.getLogger(__name__)

# Configuration
import os
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.1-8b-instant"

# PostgreSQL connection from environment variables
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    # Fallback: construct from individual env vars
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'aidevdb')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'aidev')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'aidev123')
    DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

DB_CONNECTION = DATABASE_URL

# Policy credentials database (Policy Number → Email mapping)
POLICY_CREDENTIALS = {
    "POL-776620": "maria.santos@email.com",
    "POL-445521": "fatima.shamsi@email.com",
    "POL-667788": "ali.hammadi@email.com",
    "POL-889900": "aisha.mazrouei@email.com",
    "POL-112233": "khalid.qasemi@email.com"
}

# Static OTP for authentication
STATIC_OTP = "12345"

# Constants for intent classification
PERSONAL_KEYWORDS = [
    'my preauth', 'my preauthorization', 'my authorization', 'my request', 'my requests',
    'my status', 'preauth status', 'authorization status', 'request status',
    'my procedure', 'my medication', 'my treatment',
    'my approval', 'my denial', 'approval number', 'my details', 'my information',
    'my account', 'personal information', 'customer id', 'existing customer',
    'authenticate', 'verify my identity',
    'my cost', 'approved cost', 'estimated cost'
]

GENERAL_KEYWORDS = [
    'policies', 'insurance', 'coverage', 'premium', 'benefits',
    'what is', 'how does', 'explain', 'tell me about', 'information about',
    'available', 'types of', 'kinds of', 'options', 'plans', 'products',
    'help', 'assist', 'support', 'hello', 'hi', 'greet',
    'preauthorization process', 'how to get preauth', 'preauth requirements'
]

DB_KEYWORDS = [
    'my preauth', 'my preauthorization', 'my request', 'my requests',
    'preauth status', 'authorization status', 'request status',
    'my procedure', 'my medication', 'procedure details', 'medication details',
    'my approval', 'approval number', 'denied request', 'denied requests',
    'my details', 'my information', 'request details', 'request information',
    'my history', 'request history', 'authorization history',
    'latest request', 'recent requests', 'pending requests', 'approved requests',
    'my cost', 'approved cost', 'estimated cost', 'partial approval'
]

# Keywords that indicate process/how-to questions (should NOT trigger DB, use RAG instead)
PROCESS_KEYWORDS = [
    'how to', 'how can i', 'how do i', 'how does', 'how should i', 'how would i',
    'apply for', 'apply new', 'submit new', 'file new', 'create new', 'make new',
    'start new', 'begin new', 'initiate new', 'open new',
    'steps to', 'process for', 'procedure for', 'requirements for', 'process of',
    'what documents', 'which documents', 'documents needed', 'documents required',
    'what do i need', 'what should i', 'what are the steps', 'what is the process',
    'eligibility', 'eligible for', 'qualify for', 'can i get', 'am i eligible',
    'where to', 'where can i', 'where do i', 'when to', 'when can i', 'when do i'
]
# State definitions
class AuthenticationState(TypedDict):
    customer_id: Optional[str]
    email: Optional[str]
    otp_sent: bool
    otp_verified: bool
    auth_attempts: int
    auth_step: str  # 'none', 'waiting_customer_id', 'waiting_otp', 'completed'

class ChatState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]
    user_input: str
    intent: str
    user_authenticated: bool
    user_id: Optional[str]
    session_data: Dict[str, Any]
    requires_db: bool
    needs_authentication: bool
    response: str
    context: str
    sql_query: str
    query: str
    sql_result: str
    final_answer: str
    auth_state: AuthenticationState
    auth_needs_response: bool
    auth_completed: bool

class ChatApp:
    def __init__(self, vector_store=None, vector_store1=None, temp=False):
        logger.info("Initializing ChatApp...")
        
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found")
        
        self.vector_store = vector_store
        self.vector_store1 = vector_store1
        self.temp = temp
        
        # Initialize LLM and SQL agent
        try:
            self.llm = ChatGroq(api_key=GROQ_API_KEY, model_name=MODEL_NAME)
            self.sql_agent = SQLDatabaseAgent(DB_CONNECTION, self.llm)
        except Exception as e:
            logger.error(f"Failed to initialize LLM or SQL agent: {e}")
            self.llm = None
            self.sql_agent = None
        
        # Initialize clean session state
        self._reset_session_state()
        
        # Initialize workflow
        self._build_workflow()
        logger.info("ChatApp initialized successfully")

    def _reset_session_state(self):
        """Initialize/reset session state to clean defaults"""
        self.session_state = {
            'user_authenticated': False,
            'user_id': None,
            'auth_state': {
                'customer_id': None,
                'email': None,
                'otp_sent': False,
                'otp_verified': False,
                'auth_attempts': 0,
                'auth_step': 'none'
            },
            'conversation_history': []
        }

    def _build_workflow(self):
        """Build the conversation workflow with proper error handling"""
        try:
            workflow = StateGraph(ChatState)
            
            # Add nodes
            workflow.add_node('intent_classifier', self.intent_classifier)
            workflow.add_node('authentication_layer', self.authentication_layer)
            workflow.add_node('database_connection_layer', self.database_connection_layer)
            workflow.add_node('general_chat', self.general_chat)
            workflow.add_node('generate_sql', self.generate_sql)
            workflow.add_node('execute_sql', self.execute_sql)
            workflow.add_node('format_answer', self.format_answer)
            workflow.add_node('generate_direct_answer', self.generate_direct_answer)
            workflow.add_node('auth_response', self.auth_response)
            
            # Add conditional edges with proper routing
            workflow.add_conditional_edges(
                'intent_classifier', 
                self.route_intent,
                {
                    "personal_details": 'authentication_layer', 
                    "general_details": 'general_chat'
                }
            )
            
            workflow.add_conditional_edges(
                'authentication_layer', 
                self.route_authentication,
                {
                    'authenticated': 'database_connection_layer', 
                    'need_auth_response': 'auth_response'
                }
            )
            
            workflow.add_conditional_edges(
                'database_connection_layer', 
                self.route_database_query,
                {
                    "sql_needed": "generate_sql",
                    "direct_answer": "generate_direct_answer"
                }
            )
            
            # Add edges to END
            workflow.add_edge('generate_sql', 'execute_sql')
            workflow.add_edge('execute_sql', 'format_answer')
            workflow.add_edge('format_answer', END)
            workflow.add_edge('generate_direct_answer', END)
            workflow.add_edge('general_chat', END)
            workflow.add_edge('auth_response', END)
            
            workflow.set_entry_point('intent_classifier')
            self.graph = workflow.compile()
            
        except Exception as e:
            logger.error(f"Failed to build workflow: {e}")
            raise

    def _is_policy_number_format(self, text: str) -> bool:
        """Check if text contains policy number format (POL-XXXXXX)"""
        return bool(re.search(r'POL-\d{6}', text.upper()))

    def _extract_policy_number(self, text: str) -> Optional[str]:
        """Extract policy number from text"""
        match = re.search(r'POL-\d{6}', text.upper())
        return match.group().upper() if match else None

    def _is_otp_format(self, text: str) -> bool:
        """Check if text is in OTP format"""
        return bool(re.match(r'^\d{5}$', text.strip()))

    def _extract_otp(self, text: str) -> Optional[str]:
        """Extract OTP from text"""
        # Try exact match first
        if re.match(r'^\d{5}$', text.strip()):
            return text.strip()
        # Try to find 5 digits in the text
        match = re.search(r'\b(\d{5})\b', text)
        return match.group(1) if match else None

    def _has_personal_keywords(self, text: str) -> bool:
        """Check if text contains personal data keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in PERSONAL_KEYWORDS)

    def _has_general_keywords(self, text: str) -> bool:
        """Check if text contains general query keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in GENERAL_KEYWORDS)

    def _has_db_keywords(self, text: str) -> bool:
        """Check if text requires database access"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in DB_KEYWORDS)

    def _is_process_question(self, text: str) -> bool:
        """Check if text is asking about a process/how-to (should use RAG, not DB)"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in PROCESS_KEYWORDS)

    def _classify_with_llm(self, query: str, is_authenticated: bool) -> str:
        """Use LLM to classify ambiguous queries (slow path)"""
        try:
            policy_context = f"Policy: {self.session_state.get('user_id')}" if is_authenticated else "Not authenticated"

            messages = [
                {
                    "role": "system",
                    "content": f"""You are an intent classifier for an insurance preauthorization chatbot. Classify the query into ONE intent:

**personal_details**: User wants THEIR personal preauthorization data (requires DB)
- Must include: "my", "show my", "get my", "what is my", "where is my"
- Examples: "my preauth", "my requests", "show my status", "my approval", "my cost"

**general_details**: User wants general info (uses RAG)
- Examples: "how to submit preauth", "what is preauthorization", "policies", "process"

AUTHENTICATION STATUS: {policy_context}

CLASSIFICATION RULES:
- If user is authenticated AND says "my" → personal_details
- If user is authenticated AND mentions "request/status/approval" → personal_details
- If query has "how to/what is/process" → general_details
- Default to general_details (safer)

QUERY: {query}

Respond with EXACTLY ONE WORD: personal_details OR general_details"""
                }
            ]

            response = self.llm.invoke(messages)
            intent = response.content.strip().lower().replace('"', '').replace("'", '').replace('.', '').strip()
            
            return intent if intent in ['personal_details', 'general_details'] else 'general_details'

        except Exception as e:
            logger.error(f"LLM classification error: {e}")
            return 'general_details'


    def intent_classifier(self, state: ChatState) -> ChatState:
        """Classify user intent with clear, logical rules"""
        logger.debug("=== INTENT CLASSIFIER START ===")
        
        try:
            # Get and clean current query
            current_query = state.get('user_input', '').strip()
            if not current_query:
                state['intent'] = 'general_details'
                return state
                
            state['query'] = current_query
            
            logger.debug(f"Current query: '{current_query}'")
            logger.debug(f"User authenticated: {state.get('user_authenticated', False)}")
            
            # Initialize auth_state if missing
            if 'auth_state' not in state or state['auth_state'] is None:
                state['auth_state'] = {
                    'customer_id': None,
                    'email': None,
                    'otp_sent': False,
                    'otp_verified': False,
                    'auth_attempts': 0,
                    'auth_step': 'none'
                }
            
            auth_state = state['auth_state']
            is_authenticated = state.get('user_authenticated', False)
            
            # Rule 1: If user is actively in authentication process
            if auth_state.get('auth_step') == 'waiting_policy_number':
                if self._is_policy_number_format(current_query):
                    logger.debug("User providing policy number during auth process")
                    state['intent'] = 'personal_details'
                    return state
                else:
                    # User didn't provide policy number, treat as general query
                    logger.debug("User didn't provide policy number, treating as general")
                    state['intent'] = 'general_details'
                    auth_state['auth_step'] = 'none'  # Reset auth
                    return state
            
            # Rule 2: If user is waiting for OTP
            if auth_state.get('auth_step') == 'waiting_otp':
                if self._is_otp_format(current_query):
                    logger.debug("User providing OTP during auth process")
                    state['intent'] = 'personal_details'
                    return state
                else:
                    # User didn't provide OTP, treat as general query
                    logger.debug("User didn't provide OTP, treating as general")
                    state['intent'] = 'general_details'
                    auth_state['auth_step'] = 'none'  # Reset auth
                    return state
            
            # Check for keywords
            has_policy_number = self._is_policy_number_format(current_query)
            has_personal_request = self._has_personal_keywords(current_query)
            has_general_request = self._has_general_keywords(current_query)
            is_process_question = self._is_process_question(current_query)

            # Rule 3: If already authenticated, use HYBRID smart routing
            if is_authenticated:
                logger.debug(f"User already authenticated as {state.get('user_id', 'unknown')}")

                # FAST PATH: Check obvious patterns first (keyword-based)

                # PRIORITY 1: Process/how-to questions always go to general (RAG)
                if is_process_question:
                    state['intent'] = 'general_details'
                    logger.debug("[FAST PATH] Process/how-to question → general_details")
                    return state

                # PRIORITY 2: Explicit personal data requests (strong signals)
                if (has_policy_number or
                    any(keyword in current_query.lower() for keyword in
                        ['my preauth', 'my request', 'my requests', 'show my', 'get my', 'my details', 'my information', 'my account', 'my policy'])):
                    state['intent'] = 'personal_details'
                    logger.debug("[FAST PATH] Explicit personal request → personal_details")
                    return state

                # PRIORITY 3: Strong general keywords (no personal indicators)
                if has_general_request and not has_personal_request:
                    state['intent'] = 'general_details'
                    logger.debug("[FAST PATH] General request detected → general_details")
                    return state

                # SLOW PATH: Ambiguous case - use LLM for intelligent classification
                logger.debug("[SLOW PATH] Ambiguous query, using LLM classification")
                state['intent'] = self._classify_with_llm(current_query, is_authenticated=True)
                logger.debug(f"[SLOW PATH] LLM classified as: {state['intent']}")
                return state

            # Rule 4: For unauthenticated users - also use HYBRID approach

            # FAST PATH: Check obvious patterns
            if has_policy_number or has_personal_request:
                logger.debug("[FAST PATH] Personal data request (unauthenticated) → personal_details")
                state['intent'] = 'personal_details'
                return state

            if has_general_request or is_process_question:
                logger.debug("[FAST PATH] General request (unauthenticated) → general_details")
                state['intent'] = 'general_details'
                return state

            # SLOW PATH: Ambiguous query for unauthenticated user
            logger.debug("[SLOW PATH] Ambiguous query (unauthenticated), using LLM classification")
            state['intent'] = self._classify_with_llm(current_query, is_authenticated=False)
            logger.debug(f"[SLOW PATH] LLM classified as: {state['intent']}")
            
        except Exception as e:
            logger.error(f"Error in intent classifier: {e}")
            state['intent'] = 'general_details'  # Safe fallback
            
        logger.debug("=== INTENT CLASSIFIER END ===")
        return state

   
    def authentication_layer(self, state: ChatState) -> ChatState:
        """Handle authentication with clear state management"""
        logger.debug("=== AUTHENTICATION LAYER START ===")
        
        try:
            current_message = state.get('user_input', '').strip()
            auth_state = state['auth_state']
            
            logger.debug(f"Current message: '{current_message}'")
            logger.debug(f"Auth step: {auth_state['auth_step']}")
            
            # Check if already authenticated
            if state.get('user_authenticated', False):
                logger.debug("User already authenticated, proceeding")
                return state
            
            # Start authentication process if needed
            if auth_state['auth_step'] == 'none':
                # Check if user provided policy number directly
                if self._is_policy_number_format(current_message):
                    auth_state['auth_step'] = 'waiting_policy_number'
                else:
                    # Request policy number
                    auth_state['auth_step'] = 'waiting_policy_number'
                    state['response'] = "To access your preauthorization information, please provide your Policy Number (format: POL-776620)."
                    state['auth_needs_response'] = True
                    return state

            # Handle policy number input
            if auth_state['auth_step'] == 'waiting_policy_number':
                extracted_policy = self._extract_policy_number(current_message)

                if extracted_policy:
                    logger.debug(f"Extracted policy number: {extracted_policy}")

                    if extracted_policy in POLICY_CREDENTIALS:
                        # Valid policy number
                        auth_state['customer_id'] = extracted_policy  # Store as customer_id for backward compatibility
                        auth_state['email'] = POLICY_CREDENTIALS[extracted_policy]
                        auth_state['auth_step'] = 'waiting_otp'
                        auth_state['otp_sent'] = True

                        state['response'] = f"Thank you! I found your policy. An OTP has been sent to your registered email {auth_state['email']}. Please enter the 5-digit OTP to complete authentication."
                        state['auth_needs_response'] = True
                        logger.debug("Policy number validated, requesting OTP")
                        return state
                    else:
                        # Invalid policy number
                        auth_state['auth_attempts'] += 1
                        if auth_state['auth_attempts'] >= 3:
                            self._reset_auth_state(auth_state)
                            state['response'] = "Too many failed attempts. Please contact customer service for assistance."
                            state['auth_needs_response'] = True
                            return state

                        state['response'] = f"Policy Number {extracted_policy} not found. Please check and try again. (Attempt {auth_state['auth_attempts']} of 3)"
                        state['auth_needs_response'] = True
                        return state
                else:
                    # No valid policy number found
                    state['response'] = "Please provide a valid Policy Number in the format POL-776620."
                    state['auth_needs_response'] = True
                    return state
            
            # Handle OTP input
            elif auth_state['auth_step'] == 'waiting_otp':
                extracted_otp = self._extract_otp(current_message)
                
                if extracted_otp:
                    logger.debug(f"Validating OTP: '{extracted_otp}' against '{STATIC_OTP}'")
                    
                    if extracted_otp == STATIC_OTP:
                        # Successful authentication
                        auth_state['otp_verified'] = True
                        auth_state['auth_step'] = 'completed'
                        state['user_authenticated'] = True
                        state['user_id'] = auth_state['customer_id']
                        state['auth_completed'] = True

                        # Welcome message after successful authentication
                        state['response'] = f"Authentication successful! Welcome, {state['user_id']}. You can now ask me about your preauthorization requests, status, costs, or any other details. How can I help you today?"
                        state['auth_needs_response'] = True

                        # Use ASCII instead of Unicode checkmark
                        logger.info(f"[SUCCESS] User {state['user_id']} authenticated successfully")
                        return state
                    else:
                        # Wrong OTP
                        auth_state['auth_attempts'] += 1
                        if auth_state['auth_attempts'] >= 3:
                            self._reset_auth_state(auth_state)
                            state['response'] = "Too many failed OTP attempts. Please contact customer service."
                            state['auth_needs_response'] = True
                            return state
                        
                        state['response'] = f"Incorrect OTP '{extracted_otp}'. Please try again. (Attempt {auth_state['auth_attempts']} of 3)"
                        state['auth_needs_response'] = True
                        return state
                else:
                    # No valid OTP found
                    state['response'] = f"Please enter the 5-digit OTP sent to {auth_state['email']}."
                    state['auth_needs_response'] = True
                    return state
            
            # Fallback
            state['response'] = "Authentication process error. Please provide your Customer ID to start over."
            state['auth_needs_response'] = True
            self._reset_auth_state(auth_state)
            
        except Exception as e:
            logger.error(f"Error in authentication layer: {e}")
            state['response'] = "Authentication error occurred. Please try again."
            state['auth_needs_response'] = True
            self._reset_auth_state(state['auth_state'])
            
        logger.debug("=== AUTHENTICATION LAYER END ===")
        return state

    def _reset_auth_state(self, auth_state: dict):
        """Reset authentication state to initial values"""
        auth_state.update({
            'customer_id': None,
            'email': None,
            'otp_sent': False,
            'otp_verified': False,
            'auth_attempts': 0,
            'auth_step': 'none'
        })

    def auth_response(self, state: ChatState) -> ChatState:
        """Handle authentication responses"""
        logger.debug("=== AUTH RESPONSE ===")
        state['final_answer'] = state.get('response', 'Please provide your authentication details.')
        return state

    
    def database_connection_layer(self, state: ChatState) -> ChatState:
        """Determine if query needs database access with smart routing"""
        logger.debug("=== DATABASE CONNECTION LAYER ===")

        try:
            current_query = state.get('query', '').lower()
            user_authenticated = state.get('user_authenticated', False)

            logger.debug(f"Analyzing query for DB requirement: '{current_query}'")
            logger.debug(f"User authenticated: {user_authenticated}")

            requires_db = False
            
            # For authenticated users - full privilege access with smart routing
            if user_authenticated and state.get('user_id'):
                # PRIORITY 1: Check if this is a process/how-to question (should use RAG, not DB)
                if self._is_process_question(current_query):
                    requires_db = False
                    logger.debug("Process/how-to question detected - routing to general chat (RAG)")
                else:
                    # Strong signals for personal data
                    # personal_keywords = [
                    #     'my preauth', 'my request', 'show my', 'get my', 'what is my',
                    #     'my status', 'my approval', 'my denial', 'my cost', 'latest request'
                    # ]
                    personal_keywords = [
                                    'my preauth', 'my preauthorization', 'my request', 'my requests',
                                    'show my', 'get my', 'what is my', 'my recent', 'my pending',
                                    'my status', 'my approval', 'my denial', 'my cost', 'latest request',
                                    'recent request', 'pending request', 'my history', 'my account'
                                ]
                    # Check for personal data requests
                    requires_db = any(keyword in current_query for keyword in personal_keywords)
                    
                    # Ambiguous but authenticated - assume personal
                    if not requires_db and any(word in current_query for word in ['preauth', 'request', 'authorization']):
                        requires_db = True

                if requires_db:
                    logger.debug("Personal data request detected - routing to database")
                else:
                    logger.debug("No personal data request detected - routing to general chat (RAG)")

            else:
                # For unauthenticated users, no DB access
                requires_db = False
                logger.debug("User not authenticated - no DB access")

            state['requires_db'] = requires_db
            logger.debug(f"Final decision - Database required: {requires_db}")

        except Exception as e:
            logger.error(f"Error in database connection layer: {e}")
            state['requires_db'] = False

        return state

    def general_chat(self, state: ChatState) -> ChatState:
        """Handle general chat queries with personalized responses for authenticated users"""
        logger.debug("=== GENERAL CHAT ===")

        try:
            current_query = state.get('query', '')
            user_id = state.get('user_id', None)
            user_authenticated = state.get('user_authenticated', False)

            logger.debug(f"Processing general query: '{current_query}'")
            logger.debug(f"User authenticated: {user_authenticated}, User ID: {user_id}")

            # Personalized greeting for authenticated users
            greeting_prefix = f"Hello {user_id}! " if user_authenticated and user_id else ""

            # Handle common insurance queries

            # PRIORITY: Check if asking about submitting new preauthorization
            if any(phrase in current_query.lower() for phrase in [
                'submit new preauth', 'new preauthorization', 'submit preauth', 'submit authorization',
                'apply for preauth', 'request preauth', 'get preauth', 'need preauth',
                'how can i get', 'how do i get', 'how to get', 'how can i submit',
                'how do i submit', 'how to submit', 'how can i apply', 'how do i apply',
                'how to apply', 'start new request', 'new request', 'submit request'
            ]):
                preauth_submission_info = self._get_preauth_submission_info()
                state['final_answer'] = greeting_prefix + preauth_submission_info if greeting_prefix else preauth_submission_info
            elif any(word in current_query.lower() for word in ['policies', 'policy', 'available', 'types']):
                state['final_answer'] = greeting_prefix + self._get_policies_info() if greeting_prefix else self._get_policies_info()
            elif any(word in current_query.lower() for word in ['help', 'assist', 'support']):
                state['final_answer'] = greeting_prefix + self._get_help_info() if greeting_prefix else self._get_help_info()
            elif any(word in current_query.lower() for word in ['hello', 'hi', 'greet']):
                if user_authenticated and user_id:
                    state['final_answer'] = f"Hello {user_id}! Welcome back to CAN Insurance (UAE). I can help you with information about our insurance policies, coverage options, preauthorization requests, and more. You also have access to your personal preauthorization information. How can I assist you today?"
                else:
                    state['final_answer'] = "Hello! Welcome to CAN Insurance (UAE). I can help you with information about our insurance policies, coverage options, preauthorization process, and more. How can I assist you today?"
            else:
                # Use RAG if available, otherwise provide general response
                if self.vector_store:
                    try:
                        # Import the function from chat_bot module
                        from chatbot.chat_bot import initialize_qa_chain

                        rag_chain = initialize_qa_chain(self.vector_store, self.vector_store1, self.temp)
                        if rag_chain:
                            logger.debug("RAG chain initialized, invoking with query")
                            response = rag_chain.invoke({
                                "input": current_query,
                                "chat_history": []
                            })

                            if isinstance(response, dict) and 'answer' in response:
                                answer = response['answer']
                            else:
                                answer = str(response)

                            # Add personalized prefix for authenticated users
                            if greeting_prefix and not answer.startswith(user_id if user_id else ""):
                                state['final_answer'] = greeting_prefix + answer
                            else:
                                state['final_answer'] = answer
                            logger.debug("RAG response generated successfully")
                        else:
                            logger.warning("RAG chain returned None")
                            state['final_answer'] = greeting_prefix + self._get_default_response() if greeting_prefix else self._get_default_response()
                    except Exception as e:
                        logger.error(f"RAG error: {e}", exc_info=True)
                        state['final_answer'] = greeting_prefix + self._get_default_response() if greeting_prefix else self._get_default_response()
                else:
                    logger.warning("Vector store not available, using default response")
                    state['final_answer'] = greeting_prefix + self._get_default_response() if greeting_prefix else self._get_default_response()

            logger.debug("General chat response generated")

        except Exception as e:
            logger.error(f"Error in general chat: {e}")
            state['final_answer'] = "I apologize, but I encountered an error. How can I help you with insurance information?"

        return state

    def _get_policies_info(self) -> str:
        """Get information about available policies"""
        return """We offer various insurance policies including:

• **Life Insurance** - Term and Whole Life policies to protect your family's future
• **Health Insurance** - Comprehensive individual and family health plans
• **Auto Insurance** - Complete vehicle protection with liability and comprehensive coverage
• **Home Insurance** - Property protection for your home and belongings
• **Travel Insurance** - Coverage for domestic and international travel

Each policy comes with flexible terms and competitive rates. For specific details about any policy or to get a personalized quote, please let me know what interests you!

To access your existing policy details, please provide your Policy Number for authentication."""

    def _get_help_info(self) -> str:
        """Get help information"""
        return """I'm here to help you with:

• **Policy Information** - Details about our insurance products
• **Coverage Options** - Understanding what's covered under each policy
• **Preauthorization Process** - How to submit and track authorization requests
• **Medical Procedures** - Understanding coverage for surgeries and treatments
• **Medications** - High-cost medication authorization process
• **Account Access** - View your personal preauthorization status (requires Policy Number)

What specific information would you like to know about?"""

    def _get_preauth_submission_info(self) -> str:
        """Get information about submitting new preauthorization requests"""
        return """To submit a new preauthorization request, please contact:

📧 **Email:** canvendor1@gmail.com
📞 **Phone:** 1-800-UAE-PREAUTH

Required information:
• Policy Number
• Emirates ID
• Procedure/Medication details (codes, names, dosages)
• Clinical justification from your provider
• Provider details and license number
• Estimated cost

Our team will review your request and respond within 2-5 business days. Track your request status by logging in with your Policy Number.

For urgent requests, please mark as URGENT in your submission."""

    def _get_default_response(self) -> str:
        """Get default response for general queries"""
        return "I'm here to help you with insurance-related questions. You can ask me about our policies, coverage options, preauthorization process, or any other insurance topics. For personal account information, please provide your Policy Number. How can I assist you today?"

    def generate_sql(self, state: ChatState) -> ChatState:
        """Generate SQL query with error handling"""
        logger.debug("=== GENERATE SQL ===")

        try:
            if not self.sql_agent:
                state["sql_query"] = "SELECT 'SQL agent not available' as error"
                return state

            query = state.get('query', '').strip()
            policy_number = state.get('user_id', '')  # user_id stores the policy number

            # Prepend policy number to query for SQL generation
            if policy_number:
                query_with_policy = f"For policy {policy_number}: {query}"
                logger.debug(f"Generating SQL for: '{query_with_policy}'")
                state["sql_query"] = self.sql_agent.generate_sql(query_with_policy)
            else:
                logger.warning("No policy_number found in state, generating SQL without policy filter")
                state["sql_query"] = self.sql_agent.generate_sql(query)

            logger.debug(f"Generated SQL: {state['sql_query']}")

        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            state["sql_query"] = f"SELECT 'Error generating SQL: {str(e)}' as error"

        return state
        
    def execute_sql(self, state: ChatState) -> ChatState:
        """Execute SQL query with error handling"""
        logger.debug("=== EXECUTE SQL ===")
        
        try:
            if not self.sql_agent:
                state["sql_result"] = [{"error": "SQL agent not available"}]
                return state
                
            sql_query = state.get("sql_query", "")
            logger.debug(f"Executing SQL: {sql_query}")
            
            state["sql_result"] = self.sql_agent.execute_sql(sql_query)
            logger.debug("SQL execution completed")
            
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            state["sql_result"] = [{"error": f"Error executing query: {str(e)}"}]
            
        return state
    
    def format_answer(self, state: ChatState) -> ChatState:
        """Format SQL results into final answer"""
        logger.debug("=== FORMAT ANSWER ===")
        
        try:
            if not self.sql_agent:
                state["final_answer"] = "Database service is currently unavailable."
                return state
                
            state["final_answer"] = self.sql_agent.format_answer(
                state.get("query", ""),
                state.get("sql_query", ""),
                state.get("sql_result", [])
            )
            logger.debug("SQL answer formatted")
            
        except Exception as e:
            logger.error(f"Error formatting answer: {e}")
            state["final_answer"] = "I apologize, but I encountered an error while processing your request."
            
        return state
    
    def generate_direct_answer(self, state: ChatState) -> ChatState:
        """Generate direct answer for authenticated users"""
        logger.debug("=== GENERATE DIRECT ANSWER ===")
        
        try:
            current_query = state.get('query', '')
            user_id = state.get('user_id', 'valued customer')
            
            logger.debug(f"Generating direct answer for {user_id}: '{current_query}'")
            
            # Provide personalized response for authenticated user
            if self.vector_store and hasattr(self, 'initialize_qa_chain'):
                try:
                    rag_chain = initialize_qa_chain(self.vector_store, self.vector_store1, self.temp)
                    if rag_chain:
                        prompt = f"You are helping an authenticated customer ({user_id}). Respond to: {current_query}"
                        response = rag_chain.invoke({
                            "input": prompt, 
                            "chat_history": []
                        })
                        
                        if isinstance(response, dict) and 'answer' in response:
                            state['final_answer'] = response['answer']
                        else:
                            state['final_answer'] = str(response)
                    else:
                        state['final_answer'] = f"Hello {user_id}! I'm here to help with your insurance needs. How can I assist you today?"
                except Exception as e:
                    logger.error(f"RAG error: {e}")
                    state['final_answer'] = f"Hello {user_id}! I'm here to help with your insurance questions."
            else:
                state['final_answer'] = f"Hello {user_id}! I can help you with your insurance information and general queries."
            
            logger.debug("Direct answer generated")
            
        except Exception as e:
            logger.error(f"Error in direct answer: {e}")
            state['final_answer'] = "I'm here to help with your insurance questions."
            
        return state

    # Routing functions with simplified logic
    def route_intent(self, state: ChatState) -> str:
        """Route based on intent classification"""
        intent = state.get('intent', 'general_details')
        logger.debug(f"Routing intent: {intent}")
        return intent

    def route_authentication(self, state: ChatState) -> str:
        """Route based on authentication status"""
        try:
            user_auth = state.get('user_authenticated', False)
            auth_state = state.get('auth_state', {})
            auth_needs_response = state.get('auth_needs_response', False)
            otp_verified = auth_state.get('otp_verified', False)
            
            logger.debug(f"Routing auth: user_auth={user_auth}, otp_verified={otp_verified}, needs_response={auth_needs_response}")
            
            if user_auth and otp_verified:
                return 'authenticated'
            else:
                return 'need_auth_response'
                
        except Exception as e:
            logger.error(f"Error in auth routing: {e}")
            return 'need_auth_response'

    def route_database_query(self, state: ChatState) -> str:
        """Route based on database requirement"""
        try:
            route = "sql_needed" if state.get('requires_db', False) else "direct_answer"
            logger.debug(f"Routing database query: {route}")
            return route
        except Exception as e:
            logger.error(f"Error in database routing: {e}")
            return "direct_answer"

    def chat(self, user_input: str, messages: List[AnyMessage] = None) -> str:
        """Main chat interface with robust error handling"""
        try:
            # Validate input
            if not user_input or not user_input.strip():
                return "Please provide a valid question or message."
            
            user_input = user_input.strip()
            
            logger.info(f"\n{'='*60}")
            logger.info(f"CHAT START - User: '{user_input}'")
            logger.info(f"Session Auth: {self.session_state['user_authenticated']}")
            logger.info(f"Auth Step: {self.session_state['auth_state']['auth_step']}")
            logger.info(f"{'='*60}")
            
            # Create state for this interaction
            current_state = {
                'messages': [],
                'user_input': user_input,
                'query': user_input,
                'intent': "",
                'user_authenticated': self.session_state['user_authenticated'],
                'user_id': self.session_state['user_id'],
                'session_data': {},
                'requires_db': False,
                'needs_authentication': False,
                'response': "",
                'context': "",
                'sql_query': "",
                'sql_result': "",
                'final_answer': "",
                'auth_state': self.session_state['auth_state'].copy(),
                'auth_needs_response': False,
                'auth_completed': False
            }
            
            logger.debug(f"State before workflow: user_auth={current_state['user_authenticated']}, auth_step={current_state['auth_state']['auth_step']}")
            
            # Run the workflow
            if not hasattr(self, 'graph') or self.graph is None:
                return "System error: Workflow not properly initialized."
                
            result = self.graph.invoke(current_state)
            
            logger.debug(f"State after workflow: user_auth={result.get('user_authenticated', False)}, auth_step={result.get('auth_state', {}).get('auth_step', 'unknown')}")
            
            # Update session state if authentication status changed
            if result.get('user_authenticated', False) and not self.session_state['user_authenticated']:
                self.session_state['user_authenticated'] = True
                self.session_state['user_id'] = result.get('user_id')
                # Use ASCII instead of Unicode
                logger.info(f"[SUCCESS] User authenticated: {result.get('user_id')}")
            
            # Update auth state
            if result.get('auth_state'):
                self.session_state['auth_state'] = result['auth_state'].copy()
                logger.debug(f"Auth state updated: step={self.session_state['auth_state']['auth_step']}")
            
            # Get final response
            bot_response = ""
            if result.get('final_answer'):
                bot_response = result['final_answer']
            elif result.get('response'):
                bot_response = result['response']
            else:
                bot_response = "I'm here to help. How can I assist you today?"
            
            # Update conversation history
            try:
                self.session_state['conversation_history'].append(HumanMessage(content=user_input))
                self.session_state['conversation_history'].append(AIMessage(content=bot_response))
                
                # Keep history manageable (last 20 messages)
                if len(self.session_state['conversation_history']) > 20:
                    self.session_state['conversation_history'] = self.session_state['conversation_history'][-20:]
            except Exception as e:
                logger.warning(f"Error updating conversation history: {e}")
            
            logger.info(f"CHAT END - Bot: '{bot_response[:100]}{'...' if len(bot_response) > 100 else ''}'")
            logger.info(f"{'='*60}\n")
            
            return bot_response
                
        except Exception as e:
            logger.error(f"Critical error in chat: {e}", exc_info=True)
            return "I apologize, but I encountered an error. Please try again or contact support if the issue persists."

    def reset_session(self):
        """Reset the session state"""
        logger.info("Resetting session state")
        self._reset_session_state()

    def get_session_info(self) -> dict:
        """Get current session information for debugging"""
        return {
            'authenticated': self.session_state['user_authenticated'],
            'user_id': self.session_state['user_id'],
            'auth_step': self.session_state['auth_state']['auth_step'],
            'conversation_length': len(self.session_state['conversation_history'])
        }

# Test function for development
def test_chatapp():
    """Test function to verify ChatApp functionality"""
    try:
        # Initialize with None values for testing
        chatbot = ChatApp(vector_store=None, vector_store1=None, temp=False)
        
        print("=== Testing General Queries ===")
        response1 = chatbot.chat("what policies are available")
        print(f"Q: what policies are available")
        print(f"A: {response1}\n")
        
        response2 = chatbot.chat("tell me about insurance")
        print(f"Q: tell me about insurance")
        print(f"A: {response2}\n")
        
        print("=== Testing Authentication Flow ===")
        response3 = chatbot.chat("I want to see my account details")
        print(f"Q: I want to see my account details")
        print(f"A: {response3}\n")
        
        response4 = chatbot.chat("CUS000001")
        print(f"Q: CUS000001")
        print(f"A: {response4}\n")
        
        response5 = chatbot.chat("12345")
        print(f"Q: 12345")
        print(f"A: {response5}\n")
        
        print("=== Session Info ===")
        print(chatbot.get_session_info())
        
    except Exception as e:
        print(f"Test error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_chatapp()
    else:
        print('Welcome to CAN Insurance')
        print('Type "quit" to end the chat, "reset" to reset session, "info" for session info')
        
        try:
            # Initialize the chatbot - you may need to provide actual vector stores
            chatbot = ChatApp(vector_store=None, vector_store1=None, temp=False)
            
            while True:
                try:
                    query = input('User: ').strip()
                    
                    if query.lower() == 'quit':
                        break
                    elif query.lower() == 'reset':
                        chatbot.reset_session()
                        print("Session reset successfully!")
                        continue
                    elif query.lower() == 'info':
                        print(f"Session Info: {chatbot.get_session_info()}")
                        continue
                    elif not query:
                        print("Please enter a valid question.")
                        continue
                    
                    # Get response
                    response = chatbot.chat(query)
                    print(f"Bot: {response}\n")
                    
                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    print("Please try again.")
                    
        except Exception as e:
            print(f"Failed to initialize chatbot: {e}")
            print("Please check your configuration and dependencies.")