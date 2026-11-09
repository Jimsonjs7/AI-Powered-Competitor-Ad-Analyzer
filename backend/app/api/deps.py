from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_auth_token

# Common router dependencies
AuthDependency = Depends(verify_auth_token)
DbDependency = Depends(get_db)
