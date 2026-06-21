from fastapi import Security, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.session import get_db
from app.models.user import User
from app.core.security import azure_scheme

async def validate_user(
    token_user: dict = Security(azure_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Validates the Azure AD token and syncs the user to the local database.
    Production Standard: You can add RBAC (Role-Based Access Control) 
    or database lookups here later if needed.
    """
    oid = token_user.claims.get("oid") if hasattr(token_user, "claims") else token_user.get("oid")
    email = (token_user.claims.get("preferred_username") or token_user.claims.get("email")) if hasattr(token_user, "claims") else (token_user.get("preferred_username") or token_user.get("email"))
    name = token_user.claims.get("name") if hasattr(token_user, "claims") else token_user.get("name")

    if not oid:
        # Fallback if somehow oid is missing
        return None

    # Check if user exists in local DB
    result = await db.execute(select(User).where(User.azure_oid == oid))
    user = result.scalars().first()

    if not user:
        # Auto-provision user on first login
        user = User(
            azure_oid=oid,
            email=email,
            name=name
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user
