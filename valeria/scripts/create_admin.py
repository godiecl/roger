"""
Script to create an admin user for ROGER - Valeria API
"""

import asyncio
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config.settings import settings
from app.features.authenticate.domain.user import User
from app.features.authenticate.domain.role import Role
from app.features.authenticate.infrastructure.persistence.user_model import UserModel
from app.features.authenticate.infrastructure.adapters.user_repository import UserRepository
from app.features.authenticate.infrastructure.adapters.password_hasher import password_hasher
from app.infrastructure.database.base import Base


async def create_admin_user():
    """Create an admin user."""
    print("=" * 60)
    print("ROGER - Create Admin User")
    print("=" * 60)
    
    # Get admin details
    email = input("Admin email: ")
    password = input("Admin password: ")
    full_name = input("Admin full name (optional): ") or None
    
    # Confirm
    print(f"\nCreating admin user:")
    print(f"  Email: {email}")
    print(f"  Full name: {full_name or 'N/A'}")
    print(f"  Role: {Role.ADMINISTRADOR.value}")
    
    confirm = input("\nProceed? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return
    
    # Create engine and session
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Create repository
            user_repository = UserRepository(session)
            
            # Check if user exists
            existing_user = await user_repository.get_by_email(email)
            if existing_user:
                print(f"\n❌ User with email {email} already exists!")
                return
            
            # Create admin user
            admin_user = User(
                email=email,
                hashed_password=password_hasher.hash(password),
                role=Role.ADMINISTRADOR,
                full_name=full_name,
                is_active=True,
                is_verified=True
            )
            
            # Save user
            created_user = await user_repository.create(admin_user)
            await session.commit()
            
            print(f"\n✅ Admin user created successfully!")
            print(f"   ID: {created_user.id}")
            print(f"   Email: {created_user.email}")
            print(f"   Role: {created_user.role.value}")
            
        except Exception as e:
            print(f"\n❌ Error creating admin user: {str(e)}")
            await session.rollback()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin_user())
