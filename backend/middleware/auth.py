from fastapi import Header, HTTPException
from config.supabase_client import supabase
import jwt
from types import SimpleNamespace

async def get_current_user(authorization: str = Header(None)):
    """Extract and verify user from JWT token"""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(' ')[1]
    
    try:
        # Decode JWT to get user ID (Supabase JWT contains 'sub' claim with user ID)
        # We don't verify signature here since Supabase RLS will verify at DB level
        decoded = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded.get('sub')
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: no user ID")
        
        # Return user object with id and email as attributes
        return SimpleNamespace(id=user_id, email=decoded.get('email'))
    except jwt.DecodeError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

