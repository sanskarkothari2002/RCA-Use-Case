# SOS Report Log Analyzer Bot

A simple chatbot for parsing and analyzing SOS report logs.
It helps identify issues, summarize key findings, and provide quick insights for troubleshooting.

# Project Structure
 1) collect_logs.py → Collects all errors from SOS logs and generates collected_errors.txt
 2) streamlit_main.py → Streamlit chatbot app where you can upload collected_errors.txt and chat with the bot.


# Getting Started

1. Clone this repo and install dependencies:
   
3. Collect logs:
    
    Command - python collect_logs.py  
   → Produces error_log.txt  

5. Start the chatbot:
   
    Command - streamlit run streamlit_main.py 
