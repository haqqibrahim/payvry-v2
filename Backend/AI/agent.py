import os

from phi.agent import Agent, AgentMemory
from phi.model.groq import Groq
from phi.memory.db.postgres import PgMemoryDb
from phi.storage.agent.postgres import PgAgentStorage

from Tools.authenticate_tool import authenticate_tool
from Tools.account_tool import get_balance, get_transaction_history

from Utils.whatsapp_utils import send_whatsapp



DATABASE_URL = os.getenv("DATABASE_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


async def get_payvry_agent(user_id: str, message: str, user_context: str = None):
    try:
        print("Getting Payvry Agent")
        instructions = [
            "You are a helpful assistant that helps users with the Payvry payment platform.",
            "You can perform the following actions: \n 1. Make bank transfers. \n 2. Check your balance. \n 3. Check your transaction history.",
            f"Here is all the information about the user: {user_context}, don't ask for or mention the user's information unless the user asks for it.",
            "When a user asks for their account number, please sent the account number and bank."
        ]
        
        if user_context:
            instructions.insert(1, f"Current user context:\n{user_context}")
        
        payvry_agent = Agent(
            name="Payvry AI",
            model=Groq(id="llama3-groq-70b-8192-tool-use-preview", api_key=GROQ_API_KEY),
            user_id=user_id,
            memory=AgentMemory(
                db=PgMemoryDb(table_name="agent_memory", db_url=DATABASE_URL),
            ),
            storage=PgAgentStorage(table_name="personalized_agent_sessions", db_url=DATABASE_URL),
            add_history_to_messages=True,
            num_history_responses=5,
            description="You are a helpful assistant that helps users with the Payvry payment platform.",
            instructions=instructions,
            # tools=[get_balance, get_transaction_history],
            verbose=False,
            show_tool_calls=False,
            markdown=True
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
    