import os
import sys
from dotenv import load_dotenv
import asyncio
from unittest.mock import AsyncMock, patch
from telegram import Update, User, Chat
from telegram.ext import ContextTypes

# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
from start import start

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, User, Chat, Message
from telegram.ext import ContextTypes

def create_mock_update(user_id):
    """Create a properly mocked async Update object"""
    mock_update = AsyncMock(Update)
    mock_update.effective_user = User(
        id=user_id,
        first_name=f"User{user_id}",
        is_bot=False,
        username=f"user_{user_id}"
    )
    mock_update.effective_chat = Chat(id=user_id, type="private")
    mock_update.message = AsyncMock(Message)
    mock_update.message.reply_text = AsyncMock()
    return mock_update

async def simulate_concurrent_starts(num_users):
    """Simulate multiple users starting the bot simultaneously"""
    tasks = []
    
    for i in range(1, num_users + 1):
        mock_update = create_mock_update(i)
        mock_context = AsyncMock(ContextTypes.DEFAULT_TYPE)
        mock_context.user_data = {}
        
        task = asyncio.create_task(
            start(mock_update, mock_context)
        )
        tasks.append(task)
    
    return await asyncio.gather(*tasks, return_exceptions=True)

async def run_concurrency_test():
    NUM_USERS = 50
    
    # Patch any external dependencies
    with patch('start.set_commands', new_callable=AsyncMock), \
         patch('common.common.get_lang', return_value='en'), \
         patch('common.lang_dicts.TEXTS', {'en': {'welcome_msg': 'Welcome'}}), \
         patch('common.keyboards.build_user_keyboard', return_value=None):
        
        results = await simulate_concurrent_starts(NUM_USERS)
        
        # Analyze results
        failures = [r for r in results if isinstance(r, Exception)]
        print(f"\nTest Results ({NUM_USERS} users):")
        print(f"Success: {NUM_USERS - len(failures)}")
        print(f"Failures: {len(failures)}")
        
        if failures:
            print("\nFailure Details:")
            for i, failure in enumerate(failures[:5], 1):  # Show first 5 failures
                print(f"{i}. {type(failure).__name__}: {str(failure)}")


async def main():
    load_dotenv()
    models.init_db()
    await run_concurrency_test()


asyncio.run(main())
