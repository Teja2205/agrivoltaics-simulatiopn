# Create a file named check_auth.py
import jwt
from datetime import datetime, timedelta
from app.core.config import settings
from app.core.security import create_access_token, decode_token

def test_token_flow():
    print("Testing JWT token flow:")
    print(f"SECRET_KEY (first 10 chars): {settings.SECRET_KEY[:10]}...")
    print(f"ALGORITHM: {settings.ALGORITHM}")
    
    # Create a test user ID
    test_user_id = 1
    
    # Create a token
    token = create_access_token(subject=test_user_id)
    print(f"\nCreated token (first 20 chars): {token[:20]}...")
    
    # Manually decode the token
    try:
        raw_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print("\nRaw JWT payload:")
        for key, value in raw_payload.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"\nError manually decoding token: {str(e)}")
    
    # Use our decode_token function
    token_data = decode_token(token)
    if token_data:
        print(f"\nToken successfully decoded:")
        print(f"  Subject: {token_data.sub}")
        print(f"  Expiry: {datetime.fromtimestamp(token_data.exp)}")
    else:
        print("\nFailed to decode token using application's decode_token function")

if __name__ == "__main__":
    test_token_flow()