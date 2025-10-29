#!/usr/bin/env python3
"""
User JSON Manager - Sync users between database and users.json file
"""
import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Import from app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.models import supabase

def load_users_json():
    """Load users from users.json file"""
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return {"users": [], "last_sync": None}

def save_users_json(data):
    """Save users to users.json file"""
    with open('users.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved {len(data.get('users', []))} users to users.json")

def sync_from_database():
    """Sync users from Supabase database to users.json"""
    from datetime import datetime
    
    print("🔄 Syncing users from database to users.json...")
    
    # Get all users from database
    try:
        response = supabase.table("users").select("*").execute()
        db_users = response.data
        
        print(f"📊 Found {len(db_users)} users in database")
        
        # Load existing users.json
        users_data = load_users_json()
        existing_users = {str(u.get('telegram_id')): u for u in users_data.get('users', [])}
        
        # Update with database users
        updated_count = 0
        new_count = 0
        
        for db_user in db_users:
            telegram_id = str(db_user.get('telegram_id'))
            
            # Convert datetime objects to ISO format strings
            created_at = db_user.get('created_at')
            if created_at and not isinstance(created_at, str):
                created_at = created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at)
            
            updated_at = db_user.get('updated_at')
            if updated_at and not isinstance(updated_at, str):
                updated_at = updated_at.isoformat() if hasattr(updated_at, 'isoformat') else str(updated_at)
            
            user_record = {
                "telegram_id": telegram_id,
                "user_id": db_user.get('id'),
                "username": db_user.get('username'),
                "first_name": db_user.get('first_name'),
                "last_name": db_user.get('last_name'),
                "total_xp": db_user.get('total_xp', 0),
                "created_at": created_at,
                "updated_at": updated_at
            }
            
            if telegram_id in existing_users:
                existing_users[telegram_id] = user_record
                updated_count += 1
            else:
                existing_users[telegram_id] = user_record
                new_count += 1
        
        # Save back to users.json
        users_data = {
            "users": list(existing_users.values()),
            "last_sync": datetime.utcnow().isoformat(),
            "total_count": len(existing_users)
        }
        
        save_users_json(users_data)
        print(f"✅ Sync complete!")
        print(f"   - New users: {new_count}")
        print(f"   - Updated users: {updated_count}")
        print(f"   - Total users: {len(existing_users)}")
        
    except Exception as e:
        print(f"❌ Error syncing from database: {str(e)}")
        import traceback
        traceback.print_exc()

def add_user_to_json(telegram_id, username=None, first_name=None, last_name=None):
    """Add a single user to users.json"""
    from datetime import datetime
    
    print(f"➕ Adding user to users.json...")
    print(f"   Telegram ID: {telegram_id}")
    print(f"   Username: {username}")
    
    users_data = load_users_json()
    existing_users = users_data.get('users', [])
    
    # Check if user already exists
    for user in existing_users:
        if str(user.get('telegram_id')) == str(telegram_id):
            print(f"⚠️  User already exists in users.json")
            return
    
    # Add new user
    new_user = {
        "telegram_id": str(telegram_id),
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "added_at": datetime.utcnow().isoformat()
    }
    
    existing_users.append(new_user)
    users_data['users'] = existing_users
    users_data['total_count'] = len(existing_users)
    
    save_users_json(users_data)
    print(f"✅ User added successfully!")

def list_users():
    """List all users from users.json"""
    users_data = load_users_json()
    users = users_data.get('users', [])
    
    print(f"\n📋 Users in users.json ({len(users)} total):")
    print(f"{'Telegram ID':<15} {'Username':<20} {'Name':<25} {'XP':<10}")
    print("-" * 70)
    
    for user in users:
        telegram_id = user.get('telegram_id', 'N/A')
        username = user.get('username', 'N/A')
        first_name = user.get('first_name', '')
        last_name = user.get('last_name', '')
        full_name = f"{first_name} {last_name}".strip() or 'N/A'
        xp = user.get('total_xp', 0)
        
        print(f"{telegram_id:<15} {username:<20} {full_name:<25} {xp:<10}")
    
    last_sync = users_data.get('last_sync')
    if last_sync:
        print(f"\nLast synced: {last_sync}")

def verify_user(telegram_id):
    """Verify if user exists in both users.json and database"""
    print(f"\n🔍 Verifying user: {telegram_id}")
    
    # Check users.json
    users_data = load_users_json()
    json_user = None
    for user in users_data.get('users', []):
        if str(user.get('telegram_id')) == str(telegram_id):
            json_user = user
            break
    
    if json_user:
        print(f"✅ Found in users.json:")
        print(f"   - Username: {json_user.get('username', 'N/A')}")
        print(f"   - Name: {json_user.get('first_name', '')} {json_user.get('last_name', '')}")
    else:
        print(f"❌ NOT found in users.json")
    
    # Check database
    try:
        response = supabase.table("users").select("*").eq("telegram_id", str(telegram_id)).execute()
        if response.data and len(response.data) > 0:
            db_user = response.data[0]
            print(f"✅ Found in database:")
            print(f"   - User ID: {db_user.get('id')}")
            print(f"   - Username: {db_user.get('username', 'N/A')}")
            print(f"   - Total XP: {db_user.get('total_xp', 0)}")
        else:
            print(f"❌ NOT found in database")
    except Exception as e:
        print(f"❌ Error checking database: {str(e)}")
    
    print()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage users.json file")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync users from database to users.json')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a user to users.json')
    add_parser.add_argument('telegram_id', help='Telegram ID')
    add_parser.add_argument('--username', help='Telegram username')
    add_parser.add_argument('--first-name', help='First name')
    add_parser.add_argument('--last-name', help='Last name')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all users in users.json')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify user exists in both sources')
    verify_parser.add_argument('telegram_id', help='Telegram ID to verify')
    
    args = parser.parse_args()
    
    if args.command == 'sync':
        sync_from_database()
    elif args.command == 'add':
        add_user_to_json(args.telegram_id, args.username, args.first_name, args.last_name)
    elif args.command == 'list':
        list_users()
    elif args.command == 'verify':
        verify_user(args.telegram_id)
    else:
        parser.print_help()
