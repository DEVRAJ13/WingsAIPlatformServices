"""Administrative password reset for a WINGS user.

Example:
  python -m app.scripts.reset_password --email user@company.com --temporary-password 'TempPass123!'
"""
import argparse
import asyncio
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User


async def main(email: str, temporary_password: str) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == email.lower()))
        user = result.scalar_one_or_none()
        if user is None:
            raise SystemExit(f"No user exists with email: {email}")
        user.password_hash = hash_password(temporary_password)
        user.must_change_password = True
        user.token_version += 1
        await db.commit()
        print(f"Temporary password reset for {user.email}. The user must change it after login.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--temporary-password", required=True)
    args = parser.parse_args()
    asyncio.run(main(args.email, args.temporary_password))
