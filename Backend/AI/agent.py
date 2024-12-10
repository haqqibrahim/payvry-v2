import os
from dotenv import load_dotenv
import json
from pathlib import Path
from urllib.parse import urlencode
import asyncio
from urllib.parse import urlencode

from phi.agent import Agent, AgentMemory
from phi.model.groq import Groq
from phi.model.google import Gemini
from phi.memory.db.postgres import PgMemoryDb
from phi.storage.agent.postgres import PgAgentStorage

from Tools.authenticate_tool import authenticate_tool
from Tools.account_tool import get_balance, get_transaction_history
from Tools.bank_transfer_tool import bank_transfer_tool
from Tools.bank_verification_tool import verify_bank_account

from Utils.whatsapp_utils import send_whatsapp
from database import get_db
from sqlalchemy.orm import Session
from Auth.models import ChatHistory
from sqlalchemy import desc

load_dotenv()

# Load bank data
BANK_JSON_PATH = Path(__file__).parent / "bank.json"
with open(BANK_JSON_PATH, "r") as f:
    BANK_DATA = json.load(f)
    BANKS = BANK_DATA["data"]

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL_AGENT = os.getenv("DATABASE_URL_AGENT")

async def get_payvry_agent(user_id: str, message: str, user_context: str = None):
    try:
        print("Getting Payvry Agent")
        
        
        # Create bank list string
        bank_list = "\n".join([f"- {bank['name']} (Code: {bank['code']})" for bank in BANK_DATA["data"]])
        
        description = "You are a knowledgeable and helpful assistant specializing in assisting users with the Payvry payment platform. Your primary goal is to ensure users can efficiently and accurately perform tasks like making bank transfers, checking account balances, and viewing transaction histories. You must follow precise workflows, leverage available tools to validate data, and provide clear and concise communication at every step."
        
        instructions = [
            "You are a knowledgeable and helpful assistant specializing in assisting users with the Payvry payment platform.",
            "Your primary capabilities include the following actions:",
            "1. Making bank transfers.",
            "2. Checking account balances.",
            "3. Viewing transaction history.",
            f"Here is the user's details: {user_context}.",
            f"Here is the supported banks:\n{bank_list}.",
            "Guidelines for communication:",
            "- Always refer to banks by their full names, not their codes. For example, when the user says 'UBA,' interpret it as 'United Bank for Africa.'",
            "- Specific mappings: 'GTB' or 'GT' means 'Guaranty Trust Bank,' 'FCMB' means 'First City Monument Bank,' 'Kuda' means 'Kuda Bank,' and so on as per the provided mappings.",
            "- For transfers, interpret shorthand input such as '212493343 GT 1500' as follows:\n  - Account number: '212493343',\n  - Bank: 'Guaranty Trust Bank',\n  - Amount: '1500'.\n",
            "When the user says transfer 200 to 1213455432 UBA, this means the user is providing you with the amount to be transfered (200), account number (1213455432) and the bank name (UBA), so the next step is to verify the account using the `verify_bank_account` tool and send response to the user.",
            "If the user doesn't provide the account number or the bank name, you need to ask for the account number and the bank name and then verify the account using the `verify_bank_account` tool and send response to the user.",
            "Note this is very important: Don't assume values, always use the values provided by the user or the most recent values in the Chat History.",
            "During the transfer process, only use the recipient's account number, bank name, and amount. Do not include the user's account details.",
            "When the user asks for their account number, respond with the user's account number, the bank and the user's name e.g. Account Number: 212493343 \n Bank: United Bank for Africa \n Name: John Doe",
        ]

        
        payvry_agent = Agent(
            name="Payvry AI",
            model=Gemini(id="gemini-1.5-pro", api_key=GEMINI_API_KEY),
            user_id=user_id,
            session_id=user_id,
            memory=AgentMemory(
                db=PgMemoryDb(table_name="agent_memory", db_url=DATABASE_URL_AGENT),
            ),
            storage=PgAgentStorage(table_name="personalized_agent_sessions", db_url=DATABASE_URL_AGENT),
            add_history_to_messages=True,
            num_history_responses=20,
            description=description,
            instructions=instructions,
            tools=[verify_bank_account],
            verbose=True,
            show_tool_calls=False,
            markdown=True,
            debug_mode=False
        )
        
        response = payvry_agent.run(message)
        response = response.content
        print(response)
        

        await send_whatsapp(phone_number=user_id, message=response)
        return response
    except Exception as e:
        error_message = f"Sorry, I encountered an error: {str(e)}"
        await send_whatsapp(phone_number=user_id, message=error_message)
        print(f"Error in get_payvry_agent: {str(e)}")
    

