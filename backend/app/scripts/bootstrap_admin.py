"""Bootstrap the first WINGS Platform Administrator.

Existing user:
  python -m app.scripts.bootstrap_admin --email admin@company.com

Create missing admin:
  python -m app.scripts.bootstrap_admin --email admin@company.com --name "WINGS Admin" --temporary-password 'ChangeMe123!'

Never commit the temporary password. Change it immediately after login.
"""
import argparse
import asyncio

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User


async def main(args) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == args.email.lower()))
        user = result.scalar_one_or_none()
        if user is None:
            if not args.temporary_password or not args.name:
                raise SystemExit("User does not exist. Provide --name and --temporary-password to create the first admin.")
            user = User(
                name=args.name,
                email=args.email.lower(),
                password_hash=hash_password(args.temporary_password),
                role="PLATFORM_ADMIN",
                status="ACTIVE",
                must_change_password=True,
                token_version=0,
            )
            db.add(user)
        else:
            user.role = "PLATFORM_ADMIN"
            user.status = "ACTIVE"
            if args.temporary_password:
                user.password_hash = hash_password(args.temporary_password)
                user.must_change_password = True
                user.token_version += 1
        await db.commit()
        await db.refresh(user)
        print(f"PLATFORM_ADMIN ready: {user.email} (id={user.id}).")
        if user.must_change_password:
            print("Password change is required on first login.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--name")
    parser.add_argument("--temporary-password")
    asyncio.run(main(parser.parse_args()))
