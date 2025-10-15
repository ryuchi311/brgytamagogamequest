"""
Test script to verify the application is working correctly
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


def test_environment_variables():
    """Test if all required environment variables are set"""
    print("🔍 Testing environment variables...")
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            print(f"   ❌ {var} is not set")
        else:
            print(f"   ✅ {var} is set")
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All environment variables are set\n")
        return True


def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        from app.models import supabase
        
        # Try to fetch from users table
        response = supabase.table("users").select("*").limit(1).execute()
        print("   ✅ Database connection successful")
        print(f"   ℹ️  Found {len(response.data)} user(s) in database\n")
        return True
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}\n")
        return False


async def test_telegram_bot():
    """Test Telegram bot token"""
    print("🔍 Testing Telegram bot...")
    
    try:
        from telegram import Bot
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        bot = Bot(token=bot_token)
        
        # Get bot info
        bot_info = await bot.get_me()
        print(f"   ✅ Bot connected: @{bot_info.username}")
        print(f"   ℹ️  Bot name: {bot_info.first_name}\n")
        return True
    except Exception as e:
        print(f"   ❌ Bot connection failed: {e}\n")
        return False


def test_api_imports():
    """Test if API can be imported"""
    print("🔍 Testing API imports...")
    
    try:
        from app.api import app
        print("   ✅ API imports successful\n")
        return True
    except Exception as e:
        print(f"   ❌ API import failed: {e}\n")
        return False


def test_models():
    """Test database models"""
    print("🔍 Testing database models...")
    
    try:
        from app.models import DatabaseService
        
        # Test getting active tasks
        tasks = DatabaseService.get_active_tasks()
        print(f"   ✅ Found {len(tasks)} active task(s)")
        
        # Test getting leaderboard
        leaderboard = DatabaseService.get_leaderboard(limit=5)
        print(f"   ✅ Leaderboard has {len(leaderboard)} user(s)")
        
        # Test getting rewards
        rewards = DatabaseService.get_active_rewards()
        print(f"   ✅ Found {len(rewards)} active reward(s)\n")
        
        return True
    except Exception as e:
        print(f"   ❌ Model tests failed: {e}\n")
        return False


async def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("🧪 Running Application Tests")
    print("=" * 50)
    print()
    
    results = {
        'Environment Variables': test_environment_variables(),
        'Database Connection': test_database_connection(),
        'API Imports': test_api_imports(),
        'Database Models': test_models(),
        'Telegram Bot': await test_telegram_bot()
    }
    
    print("=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your application is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
