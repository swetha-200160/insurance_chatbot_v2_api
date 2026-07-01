# # import streamlit as st
# # import requests
# # import json
# # from datetime import datetime

# # # Configure page
# # st.set_page_config(
# #     page_title="CAN Insurance Preauthorization Assistant",
# #     page_icon="🏥",
# #     layout="wide"
# # )

# # # API Configuration
# # API_BASE_URL = "http://localhost:8000"  # Change this to your FastAPI server URL

# # # Custom CSS
# # st.markdown("""
# # <style>
# #     .main-header {
# #         font-size: 2.5rem;
# #         color: #1E88E5;
# #         text-align: center;
# #         margin-bottom: 1rem;
# #     }
# #     .sub-header {
# #         font-size: 1.2rem;
# #         color: #666;
# #         text-align: center;
# #         margin-bottom: 2rem;
# #     }
# #     .chat-message {
# #         padding: 1rem;
# #         border-radius: 0.5rem;
# #         margin-bottom: 1rem;
# #         display: flex;
# #         flex-direction: column;
# #     }
# #     .user-message {
# #         background-color: #E3F2FD;
# #         margin-left: 20%;
# #     }
# #     .bot-message {
# #         background-color: #F5F5F5;
# #         margin-right: 20%;
# #     }
# #     .message-label {
# #         font-weight: bold;
# #         margin-bottom: 0.5rem;
# #     }
# #     .user-label {
# #         color: #1E88E5;
# #     }
# #     .bot-label {
# #         color: #43A047;
# #     }
# #     .info-box {
# #         background-color: #FFF3E0;
# #         padding: 1rem;
# #         border-radius: 0.5rem;
# #         border-left: 4px solid #FF9800;
# #         margin-bottom: 1rem;
# #     }
# #     .stButton>button {
# #         width: 100%;
# #         background-color: #1E88E5;
# #         color: white;
# #         font-weight: bold;
# #     }
# # </style>
# # """, unsafe_allow_html=True)

# # # Initialize session state
# # if "messages" not in st.session_state:
# #     st.session_state.messages = []

# # if "authenticated" not in st.session_state:
# #     st.session_state.authenticated = False

# # if "customer_id" not in st.session_state:
# #     st.session_state.customer_id = None

# # # Header
# # st.markdown('<h1 class="main-header">🏥 CAN Insurance (UAE)</h1>', unsafe_allow_html=True)
# # st.markdown('<p class="sub-header">Preauthorization Assistant Chatbot</p>', unsafe_allow_html=True)

# # # Sidebar
# # with st.sidebar:
# #     st.header("ℹ️ Information")

# #     # Authentication status
# #     if st.session_state.authenticated:
# #         st.success(f"✅ Authenticated as: {st.session_state.customer_id}")
# #     else:
# #         st.info("🔒 Not authenticated")

# #     st.markdown("---")

# #     # Sample queries
# #     st.subheader("📝 Sample Queries")
# #     st.markdown("""
# #     **General Questions:**
# #     - What is preauthorization?
# #     - How to submit a new request?
# #     - What is the approval process?

# #     **Personal Queries** (requires login):
# #     - Show my preauth requests
# #     - What's my preauth status?
# #     - Show denied requests
# #     - Show my medication preauths
# #     - My latest request
# #     """)

# #     st.markdown("---")

# #     # Test credentials
# #     st.subheader("🔑 Test Credentials")
# #     st.code("""
# # Customer IDs:
# # - CUS000001
# # - CUS000002
# # - CUS000003
# # - CUS000004
# # - CUS000005

# # OTP: 12345
# #     """)

# #     st.markdown("---")

# #     # Language selection
# #     language = st.selectbox(
# #         "🌐 Language",
# #         ["English", "Arabic"],
# #         key="language_selector"
# #     )

# #     st.markdown("---")

# #     # Reset chat button
# #     if st.button("🔄 Reset Chat", use_container_width=True):
# #         # Call reset endpoint
# #         try:
# #             response = requests.post(f"{API_BASE_URL}/reset")
# #             st.session_state.messages = []
# #             st.session_state.authenticated = False
# #             st.session_state.customer_id = None
# #             st.success("Chat reset successfully!")
# #             st.rerun()
# #         except Exception as e:
# #             st.error(f"Error resetting chat: {str(e)}")

# #     # API Health check
# #     st.markdown("---")
# #     st.subheader("🔌 API Status")
# #     try:
# #         health_response = requests.get(f"{API_BASE_URL}/health", timeout=3)
# #         if health_response.status_code == 200:
# #             st.success("✅ Connected")
# #             health_data = health_response.json()
# #             if health_data.get("vector_stores", {}).get("main"):
# #                 st.caption("📚 Knowledge base loaded")
# #         else:
# #             st.error("❌ API Error")
# #     except:
# #         st.error("❌ Disconnected")
# #         st.caption("Make sure FastAPI server is running on port 8000")

# # # Info box
# # st.markdown("""
# # <div class="info-box">
# #     <strong>ℹ️ How to use:</strong><br>
# #     1. Ask general questions about preauthorization (no login needed)<br>
# #     2. For personal data, authenticate with your Customer ID and OTP<br>
# #     3. View your preauthorization requests, status, and history
# # </div>
# # """, unsafe_allow_html=True)

# # # Chat container
# # chat_container = st.container()

# # # Display chat messages
# # with chat_container:
# #     for message in st.session_state.messages:
# #         if message["role"] == "user":
# #             st.markdown(f"""
# #             <div class="chat-message user-message">
# #                 <div class="message-label user-label">👤 You</div>
# #                 <div>{message["content"]}</div>
# #             </div>
# #             """, unsafe_allow_html=True)
# #         else:
# #             st.markdown(f"""
# #             <div class="chat-message bot-message">
# #                 <div class="message-label bot-label">🤖 Assistant</div>
# #                 <div>{message["content"]}</div>
# #             </div>
# #             """, unsafe_allow_html=True)

# # # Chat input
# # st.markdown("---")

# # # Create columns for input
# # col1, col2 = st.columns([5, 1])

# # with col1:
# #     user_input = st.text_input(
# #         "Type your message here...",
# #         key="user_input",
# #         placeholder="Ask about preauthorization or your requests...",
# #         label_visibility="collapsed"
# #     )

# # with col2:
# #     send_button = st.button("Send 📤", use_container_width=True)

# # # Process user input
# # if send_button and user_input:
# #     # Add user message to chat
# #     st.session_state.messages.append({"role": "user", "content": user_input})

# #     # Determine language code
# #     lang_code = "ar" if language == "Arabic" else "en"

# #     # Make API call
# #     try:
# #         with st.spinner("🤔 Thinking..."):
# #             response = requests.post(
# #                 f"{API_BASE_URL}/insurance/chat",
# #                 json={
# #                     "prompt": user_input,
# #                     "language": lang_code
# #                 },
# #                 timeout=30
# #             )

# #         if response.status_code == 200:
# #             bot_response = response.json().get("answer", "Sorry, I couldn't process that.")

# #             # Check if user authenticated (basic detection)
# #             if "authenticated successfully" in bot_response.lower() or "welcome back" in bot_response.lower():
# #                 st.session_state.authenticated = True
# #                 # Try to extract customer ID from previous messages
# #                 for msg in reversed(st.session_state.messages):
# #                     if msg["role"] == "user" and "CUS" in msg["content"].upper():
# #                         import re
# #                         match = re.search(r'CUS\d{6}', msg["content"].upper())
# #                         if match:
# #                             st.session_state.customer_id = match.group()
# #                             break

# #             # Add bot response to chat
# #             st.session_state.messages.append({"role": "assistant", "content": bot_response})

# #         else:
# #             error_msg = f"Error: API returned status code {response.status_code}"
# #             st.session_state.messages.append({"role": "assistant", "content": error_msg})

# #     except requests.exceptions.Timeout:
# #         error_msg = "Request timed out. Please try again."
# #         st.session_state.messages.append({"role": "assistant", "content": error_msg})

# #     except requests.exceptions.ConnectionError:
# #         error_msg = "Cannot connect to API. Make sure the server is running on http://localhost:8000"
# #         st.session_state.messages.append({"role": "assistant", "content": error_msg})

# #     except Exception as e:
# #         error_msg = f"An error occurred: {str(e)}"
# #         st.session_state.messages.append({"role": "assistant", "content": error_msg})

# #     # Rerun to update chat
# #     st.rerun()

# # # Quick action buttons
# # st.markdown("---")
# # st.subheader("⚡ Quick Actions")

# # col1, col2, col3, col4 = st.columns(4)

# # with col1:
# #     if st.button("🏥 What is preauthorization?", use_container_width=True):
# #         st.session_state.messages.append({"role": "user", "content": "What is preauthorization?"})
# #         st.rerun()

# # with col2:
# #     if st.button("📝 How to submit request?", use_container_width=True):
# #         st.session_state.messages.append({"role": "user", "content": "How to submit a new preauthorization request?"})
# #         st.rerun()

# # with col3:
# #     if st.button("🔍 My requests", use_container_width=True):
# #         st.session_state.messages.append({"role": "user", "content": "Show my preauthorization requests"})
# #         st.rerun()

# # with col4:
# #     if st.button("❓ Help", use_container_width=True):
# #         st.session_state.messages.append({"role": "user", "content": "Help me understand what you can do"})
# #         st.rerun()

# # # Footer
# # st.markdown("---")
# # st.markdown("""
# # <div style="text-align: center; color: #999; padding: 1rem;">
# #     <small>
# #         CAN Insurance UAE - Preauthorization Assistant<br>
# #         For urgent requests, call: 1-800-UAE-PREAUTH | Email: canvendor1@gmail.com
# #     </small>
# # </div>
# # """, unsafe_allow_html=True)


# import streamlit as st
# import requests
# import json
# from datetime import datetime
# import re

# # Configure page
# st.set_page_config(
#     page_title="CAN Insurance Preauthorization Assistant",
#     page_icon="🏥",
#     layout="wide"
# )

# # API Configuration
# API_BASE_URL = "http://localhost:8000"  # Change this to your FastAPI server URL

# # Custom CSS
# st.markdown("""
# <style>
#     .main-header {
#         font-size: 2.5rem;
#         color: #1E88E5;
#         text-align: center;
#         margin-bottom: 1rem;
#     }
#     .sub-header {
#         font-size: 1.2rem;
#         color: #666;
#         text-align: center;
#         margin-bottom: 2rem;
#     }
#     .chat-message {
#         padding: 1rem;
#         border-radius: 0.5rem;
#         margin-bottom: 1rem;
#         display: flex;
#         flex-direction: column;
#     }
#     .user-message {
#         background-color: #E3F2FD;
#         margin-left: 20%;
#     }
#     .bot-message {
#         background-color: #F5F5F5;
#         margin-right: 20%;
#     }
#     .message-label {
#         font-weight: bold;
#         margin-bottom: 0.5rem;
#     }
#     .user-label {
#         color: #1E88E5;
#     }
#     .bot-label {
#         color: #43A047;
#     }
#     .info-box {
#         background-color: #FFF3E0;
#         padding: 1rem;
#         border-radius: 0.5rem;
#         border-left: 4px solid #FF9800;
#         margin-bottom: 1rem;
#     }
#     .stButton>button {
#         width: 100%;
#         background-color: #1E88E5;
#         color: white;
#         font-weight: bold;
#     }
# </style>
# """, unsafe_allow_html=True)

# # Initialize session state
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# if "authenticated" not in st.session_state:
#     st.session_state.authenticated = False

# if "customer_id" not in st.session_state:
#     st.session_state.customer_id = None

# if "session_id" not in st.session_state:
#     st.session_state.session_id = None

# # Header
# st.markdown('<h1 class="main-header">🏥 CAN Insurance (UAE)</h1>', unsafe_allow_html=True)
# st.markdown('<p class="sub-header">Preauthorization Assistant Chatbot</p>', unsafe_allow_html=True)

# # Sidebar
# with st.sidebar:
#     st.header("ℹ️ Information")

#     # Authentication status
#     if st.session_state.authenticated:
#         st.success(f"✅ Authenticated as: {st.session_state.customer_id}")
#     else:
#         st.info("🔒 Not authenticated")

#     st.markdown("---")

#     # Sample queries
#     st.subheader("📝 Sample Queries")
#     st.markdown("""
#     **General Questions:**
#     - What is preauthorization?
#     - How to submit a new request?
#     - What is the approval process?

#     **Personal Queries** (requires login):
#     - Show my preauth requests
#     - What's my preauth status?
#     - Show denied requests
#     - Show my medication preauths
#     - My latest request
#     """)

#     st.markdown("---")

#     # Test credentials
#     st.subheader("🔑 Test Credentials")
#     st.code("""
# Policy Numbers:
# - POL-776620 (Maria Santos)
# - POL-445521 (Fatima Al Shamsi)
# - POL-667788 (Ali Al Hammadi)
# - POL-889900 (Aisha Al Mazrouei)
# - POL-112233 (Khalid Al Qasemi)

# OTP: 12345
#     """)

#     st.markdown("---")

#     # Language selection
#     language = st.selectbox(
#         "🌐 Language",
#         ["English", "Arabic"],
#         key="language_selector"
#     )

#     st.markdown("---")

#     # Reset chat button
#     if st.button("🔄 Reset Chat", use_container_width=True):
#         # Call reset endpoint
#         try:
#             response = requests.post(
#                 f"{API_BASE_URL}/reset",
#                 json={"session_id": st.session_state.session_id}
#             )
#             st.session_state.messages = []
#             st.session_state.authenticated = False
#             st.session_state.customer_id = None
#             st.session_state.session_id = None
#             st.success("Chat reset successfully!")
#             st.rerun()
#         except Exception as e:
#             st.error(f"Error resetting chat: {str(e)}")

#     # API Health check
#     st.markdown("---")
#     st.subheader("🔌 API Status")
#     try:
#         health_response = requests.get(f"{API_BASE_URL}/health", timeout=3)
#         if health_response.status_code == 200:
#             st.success("✅ Connected")
#             health_data = health_response.json()
#             if health_data.get("vector_stores", {}).get("main"):
#                 st.caption("📚 Knowledge base loaded")
#         else:
#             st.error("❌ API Error")
#     except:
#         st.error("❌ Disconnected")
#         st.caption("Make sure FastAPI server is running on port 8000")

# # Info box
# st.markdown("""
# <div class="info-box">
#     <strong>ℹ️ How to use:</strong><br>
#     1. Ask general questions about preauthorization (no login needed)<br>
#     2. For personal data, authenticate with your Policy Number and OTP<br>
#     3. View your preauthorization requests, status, and history
# </div>
# """, unsafe_allow_html=True)

# # Chat container
# chat_container = st.container()

# # Display chat messages
# with chat_container:
#     for message in st.session_state.messages:
#         if message["role"] == "user":
#             st.markdown(f"""
#             <div class="chat-message user-message">
#                 <div class="message-label user-label">👤 You</div>
#                 <div>{message["content"]}</div>
#             </div>
#             """, unsafe_allow_html=True)
#         else:
#             st.markdown(f"""
#             <div class="chat-message bot-message">
#                 <div class="message-label bot-label">🤖 Assistant</div>
#                 <div>{message["content"]}</div>
#             </div>
#             """, unsafe_allow_html=True)

# # Chat input
# st.markdown("---")

# # Create columns for input
# col1, col2 = st.columns([5, 1])

# with col1:
#     user_input = st.text_input(
#         "Type your message here...",
#         key="user_input",
#         placeholder="Ask about preauthorization or your requests...",
#         label_visibility="collapsed"
#     )

# with col2:
#     send_button = st.button("Send 📤", use_container_width=True)

# # Process user input
# if send_button and user_input:
#     # Add user message to chat
#     st.session_state.messages.append({"role": "user", "content": user_input})

#     # Determine language code
#     lang_code = "ar" if language == "Arabic" else "en"

#     # Make API call
#     try:
#         with st.spinner("🤔 Thinking..."):
#             response = requests.post(
#                 f"{API_BASE_URL}/insurance/chat",
#                 json={
#                     "prompt": user_input,
#                     "language": lang_code,
#                     "session_id": st.session_state.session_id
#                 },
#                 timeout=30
#             )

#         if response.status_code == 200:
#             response_data = response.json()
#             bot_response = response_data.get("answer", "Sorry, I couldn't process that.")
            
#             # Store session_id for future requests
#             if "session_id" in response_data:
#                 st.session_state.session_id = response_data["session_id"]
            
#             # Check if user authenticated
#             if "authenticated successfully" in bot_response.lower() or "welcome back" in bot_response.lower():
#                 st.session_state.authenticated = True
#                 # Extract POLICY NUMBER
#                 for msg in reversed(st.session_state.messages):
#                     if msg["role"] == "user" and "POL-" in msg["content"].upper():
#                         match = re.search(r'POL-\d{6}', msg["content"].upper())
#                         if match:
#                             st.session_state.customer_id = match.group()
#                             break

#             # Add bot response to chat
#             st.session_state.messages.append({"role": "assistant", "content": bot_response})

#         else:
#             error_msg = f"Error: API returned status code {response.status_code}"
#             st.session_state.messages.append({"role": "assistant", "content": error_msg})

#     except requests.exceptions.Timeout:
#         error_msg = "Request timed out. Please try again."
#         st.session_state.messages.append({"role": "assistant", "content": error_msg})

#     except requests.exceptions.ConnectionError:
#         error_msg = "Cannot connect to API. Make sure the server is running on http://localhost:8000"
#         st.session_state.messages.append({"role": "assistant", "content": error_msg})

#     except Exception as e:
#         error_msg = f"An error occurred: {str(e)}"
#         st.session_state.messages.append({"role": "assistant", "content": error_msg})

#     # Rerun to update chat
#     st.rerun()

# # Quick action buttons
# st.markdown("---")
# st.subheader("⚡ Quick Actions")

# col1, col2, col3, col4 = st.columns(4)

# with col1:
#     if st.button("🏥 What is preauthorization?", use_container_width=True):
#         st.session_state.messages.append({"role": "user", "content": "What is preauthorization?"})
#         st.rerun()

# with col2:
#     if st.button("📝 How to submit request?", use_container_width=True):
#         st.session_state.messages.append({"role": "user", "content": "How to submit a new preauthorization request?"})
#         st.rerun()

# with col3:
#     if st.button("🔍 My requests", use_container_width=True):
#         st.session_state.messages.append({"role": "user", "content": "Show my preauthorization requests"})
#         st.rerun()

# with col4:
#     if st.button("❓ Help", use_container_width=True):
#         st.session_state.messages.append({"role": "user", "content": "Help me understand what you can do"})
#         st.rerun()

# # Footer
# st.markdown("---")
# st.markdown("""
# <div style="text-align: center; color: #999; padding: 1rem;">
#     <small>
#         CAN Insurance UAE - Preauthorization Assistant<br>
#         For urgent requests, call: 1-800-UAE-PREAUTH | Email: canvendor1@gmail.com
#     </small>
# </div>
# """, unsafe_allow_html=True)


import streamlit as st
import requests
import re

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "customer_id" not in st.session_state:
    st.session_state.customer_id = None

if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Sidebar
with st.sidebar:
    st.header("Controls")
    
    # Language selection
    language = st.selectbox("Language", ["English", "Arabic"])
    
    st.markdown("---")
    
    # API Health check
    st.subheader("API Status")
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=3)
        if health_response.status_code == 200:
            st.success("Connected")
        else:
            st.error("API Error")
    except:
        st.error("Disconnected")
    
    st.markdown("---")
    
    # Reset chat button
    if st.button("Reset Chat"):
        try:
            response = requests.post(
                f"{API_BASE_URL}/reset",
                json={"session_id": st.session_state.session_id}
            )
            st.session_state.messages = []
            st.session_state.authenticated = False
            st.session_state.customer_id = None
            st.session_state.session_id = None
            st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # Test credentials (collapsible)
    with st.expander("Test Credentials"):
        st.code("""
Policy Numbers:
- POL-776620 (Maria Santos)
- POL-445521 (Fatima Al Shamsi)
- POL-667788 (Ali Al Hammadi)
- POL-889900 (Aisha Al Mazrouei)
- POL-112233 (Khalid Al Qasemi)

OTP: 12345
        """)

# Main chat area
st.title("Insurance Assistant")

# Display chat messages in a scrollable container
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask about preauthorization or your requests..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    lang_code = "ar" if language == "Arabic" else "en"
    
    # API call
    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                f"{API_BASE_URL}/insurance/chat",
                json={
                    "prompt": prompt,
                    "language": lang_code,
                    "session_id": st.session_state.session_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                bot_response = data.get("answer", "Sorry, I couldn't process that.")
                
                # Update session
                if "session_id" in data:
                    st.session_state.session_id = data["session_id"]
                
                # Check authentication
                if "authenticated successfully" in bot_response.lower() or "welcome back" in bot_response.lower():
                    st.session_state.authenticated = True
                    for msg in reversed(st.session_state.messages):
                        if msg["role"] == "user" and "POL-" in msg["content"].upper():
                            match = re.search(r'POL-\d{6}', msg["content"].upper())
                            if match:
                                st.session_state.customer_id = match.group()
                                break
                
                # Add bot response
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
            else:
                st.error(f"API Error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            st.error("Request timed out")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to API. Ensure server is running on port 8000")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.rerun()