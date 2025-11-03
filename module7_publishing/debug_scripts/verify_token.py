# verify_token.py
"""
Debug script to verify token retrieval and decryption
"""

import sys
from pathlib import Path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from database.oauth_db import get_oauth_collection, decrypt_token
from config.settings import settings
from datetime import datetime

def verify_token_retrieval(user_id: str):
    """Verify token is being retrieved and decrypted correctly"""
    
    print(f"\n{'='*80}")
    print(f"Token Verification for User: {user_id}")
    print(f"{'='*80}\n")
    
    try:
        # Step 1: Get raw token from database
        print("Step 1: Retrieving RAW token from database...")
        collection = get_oauth_collection()
        
        raw_token_doc = collection.find_one({
            'user_id': user_id,
            'platform': 'twitter'
        })
        
        if not raw_token_doc:
            print(f"✗ No token found for user {user_id}")
            return False
        
        print(f"✓ Token document found")
        print(f"  User: {raw_token_doc.get('user_id')}")
        print(f"  Platform: {raw_token_doc.get('platform')}")
        print(f"  Username: @{raw_token_doc.get('platform_username')}")
        print(f"  Is Valid: {raw_token_doc.get('is_valid')}")
        print(f"  Expires: {raw_token_doc.get('expires_at')}")
        
        # Check if expired
        expires_at = raw_token_doc.get('expires_at')
        if expires_at and isinstance(expires_at, datetime):
            if expires_at < datetime.utcnow():
                print(f"  ⚠ WARNING: Token is EXPIRED!")
                print(f"  Expired: {(datetime.utcnow() - expires_at).total_seconds() / 60:.1f} minutes ago")
            else:
                print(f"  ✓ Token still valid for: {(expires_at - datetime.utcnow()).total_seconds() / 60:.1f} minutes")
        
        # Step 2: Check token format
        print(f"\nStep 2: Checking token format...")
        raw_access_token = raw_token_doc.get('access_token', '')
        
        print(f"  Raw access token (first 50 chars): {raw_access_token[:50]}...")
        print(f"  Raw access token length: {len(raw_access_token)} chars")
        
        # Step 3: Try to decrypt
        print(f"\nStep 3: Attempting to decrypt token...")
        try:
            decrypted_token = decrypt_token(raw_access_token, settings.ENCRYPTION_KEY)
            print(f"✓ Token decrypted successfully")
            print(f"  Decrypted token (first 50 chars): {decrypted_token[:50]}...")
            print(f"  Decrypted token length: {len(decrypted_token)} chars")
            
            # Twitter OAuth 2.0 bearer tokens are typically 100+ characters
            if len(decrypted_token) < 50:
                print(f"  ⚠ WARNING: Token seems too short for OAuth 2.0")
            
            return decrypted_token
            
        except Exception as decrypt_error:
            print(f"✗ Decryption failed: {decrypt_error}")
            print(f"\n  Possible issues:")
            print(f"  1. Token was not encrypted when stored")
            print(f"  2. Wrong encryption key being used")
            print(f"  3. Token corruption")
            
            # Try using raw token (in case it wasn't encrypted)
            print(f"\n  Attempting to use raw token without decryption...")
            return raw_access_token
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_token_with_tweepy(access_token: str):
    """Test if token works with Tweepy"""
    
    print(f"\n{'='*80}")
    print(f"Testing Token with Tweepy")
    print(f"{'='*80}\n")
    
    try:
        import tweepy
        
        print(f"Creating Tweepy client with token...")
        print(f"  Token (first 30 chars): {access_token[:30]}...")
        
        # Try direct API call first (no client)
        print(f"\nTest 1: Direct Twitter API call...")
        import requests
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            'https://api.twitter.com/2/users/me',
            headers=headers,
            timeout=10
        )
        
        print(f"  Response status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✓ Direct API call successful!")
            print(f"  User: @{user_data['data']['username']}")
            print(f"  ID: {user_data['data']['id']}")
            
            # Now try with Tweepy
            print(f"\nTest 2: Creating Tweepy client...")
            client = tweepy.Client(bearer_token=access_token)
            
            try:
                me = client.get_me()
                if me.data:
                    print(f"✓ Tweepy client working!")
                    print(f"  Authenticated as: @{me.data.username}")
                    return True
                else:
                    print(f"✗ Tweepy client.get_me() returned no data")
                    return False
            except Exception as tweepy_error:
                print(f"✗ Tweepy error: {tweepy_error}")
                return False
                
        else:
            print(f"✗ Direct API call failed")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    user_id = 'test_user_demo'
    
    # Step 1: Verify token retrieval
    access_token = verify_token_retrieval(user_id)
    
    if not access_token:
        print(f"\n❌ Cannot proceed - no valid token")
        sys.exit(1)
    
    # Step 2: Test with Tweepy
    success = test_token_with_tweepy(access_token)
    
    if success:
        print(f"\n{'='*80}")
        print(f"✓ SUCCESS: Token is valid and working!")
        print(f"{'='*80}")
        print(f"\nYou can now use this token for publishing.")
    else:
        print(f"\n{'='*80}")
        print(f"✗ FAILED: Token is not working")
        print(f"{'='*80}")
        print(f"\nPossible solutions:")
        print(f"1. Reconnect Twitter OAuth to get a fresh token")
        print(f"2. Check if token has correct scopes (tweet.write)")
        print(f"3. Verify encryption/decryption is working correctly")