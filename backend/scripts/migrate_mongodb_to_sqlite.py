"""
MongoDB to SQLite Migration Script

This script migrates data from MongoDB to SQLite.
Run this before starting the application with SQLite for the first time.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import aiosqlite
from motor.motor_asyncio import AsyncIOMotorClient
from tqdm import tqdm

# Configuration
MONGODB_URL = "mongodb://localhost:27017"
MONGODB_DB_NAME = "boss_rpa"
SQLITE_DB_PATH = Path(__file__).parent.parent / "data" / "boss_rpa.db"


class MongoDBToSQLiteMigrator:
    """Migration handler for MongoDB to SQLite"""

    def __init__(self, mongodb_url: str, mongodb_db: str, sqlite_path: Path):
        self.mongodb_url = mongodb_url
        self.mongodb_db = mongodb_db
        self.sqlite_path = sqlite_path
        self.mongo_client = None
        self.sqlite_conn = None

    async def connect(self):
        """Connect to both databases"""
        print("Connecting to databases...")
        self.mongo_client = AsyncIOMotorClient(self.mongodb_url)
        self.sqlite_conn = await aiosqlite.connect(self.sqlite_path)
        print("✓ Connected to both databases")

    async def close(self):
        """Close all connections"""
        if self.mongo_client:
            self.mongo_client.close()
        if self.sqlite_conn:
            await self.sqlite_conn.close()
        print("✓ Closed all connections")

    async def migrate_accounts(self) -> int:
        """Migrate accounts collection"""
        print("\n=== Migrating Accounts ===")

        db = self.mongo_client[self.mongodb_db]
        accounts_collection = db.accounts

        # Get total count
        total = await accounts_collection.count_documents({})
        print(f"Found {total} accounts in MongoDB")

        if total == 0:
            print("No accounts to migrate")
            return 0

        # Fetch all accounts
        cursor = accounts_collection.find({})
        accounts = await cursor.to_list(length=total)

        # Prepare data for insertion
        accounts_data = []
        for account in tqdm(accounts, desc="Processing accounts"):
            account_dict = {
                "phone": account.get("phone", ""),
                "username": account.get("username"),
                "is_active": account.get("is_active", True),
                "cookie_status": account.get("cookie_status", "none"),
                "last_login": account.get("last_login").isoformat()
                if account.get("last_login")
                else None,
                "created_at": account.get("created_at", datetime.now()).isoformat(),
                "updated_at": account.get("updated_at", datetime.now()).isoformat(),
            }
            accounts_data.append(
                (
                    account_dict["phone"],
                    account_dict["username"],
                    account_dict["is_active"],
                    account_dict["cookie_status"],
                    account_dict["last_login"],
                    account_dict["created_at"],
                    account_dict["updated_at"],
                )
            )

        # Insert into SQLite
        await self.sqlite_conn.executemany(
            """
            INSERT INTO accounts (
                phone, username, is_active, cookie_status,
                last_login, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            accounts_data,
        )
        await self.sqlite_conn.commit()

        print(f"✓ Migrated {len(accounts_data)} accounts")
        return len(accounts_data)

    async def migrate_jobs(self) -> int:
        """Migrate jobs collection"""
        print("\n=== Migrating Jobs ===")

        db = self.mongo_client[self.mongodb_db]
        jobs_collection = db.jobs

        # Get total count
        total = await jobs_collection.count_documents({})
        print(f"Found {total} jobs in MongoDB")

        if total == 0:
            print("No jobs to migrate")
            return 0

        # Fetch all jobs
        cursor = jobs_collection.find({})
        jobs = await cursor.to_list(length=total)

        # Prepare data for insertion
        jobs_data = []
        for job in tqdm(jobs, desc="Processing jobs"):
            job_dict = {
                "job_name": job.get("job_name", ""),
                "company_name": job.get("company_name", ""),
                "salary": job.get("salary", ""),
                "city": job.get("city", ""),
                "area": job.get("area"),
                "experience": job.get("experience"),
                "education": job.get("education"),
                "company_size": job.get("company_size"),
                "industry": job.get("industry"),
                "job_url": job.get("job_url", ""),
                "boss_title": job.get("boss_title"),
                "status": job.get("status", "pending"),
                "is_applied": job.get("is_applied", False),
                "notes": job.get("notes"),
                "created_at": job.get("created_at", datetime.now()).isoformat(),
                "updated_at": job.get("updated_at", datetime.now()).isoformat(),
            }
            jobs_data.append(
                (
                    job_dict["job_name"],
                    job_dict["company_name"],
                    job_dict["salary"],
                    job_dict["city"],
                    job_dict["area"],
                    job_dict["experience"],
                    job_dict["education"],
                    job_dict["company_size"],
                    job_dict["industry"],
                    job_dict["job_url"],
                    job_dict["boss_title"],
                    job_dict["status"],
                    job_dict["is_applied"],
                    job_dict["notes"],
                    job_dict["created_at"],
                    job_dict["updated_at"],
                )
            )

        # Insert into SQLite
        await self.sqlite_conn.executemany(
            """
            INSERT INTO jobs (job_name, company_name, salary, city, area, experience,
                             education, company_size, industry, job_url, boss_title,
                             status, is_applied, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            jobs_data,
        )
        await self.sqlite_conn.commit()

        print(f"✓ Migrated {len(jobs_data)} jobs")
        return len(jobs_data)

    async def migrate_tasks(self) -> int:
        """Migrate tasks collection"""
        print("\n=== Migrating Tasks ===")

        db = self.mongo_client[self.mongodb_db]
        tasks_collection = db.tasks

        # Get total count
        total = await tasks_collection.count_documents({})
        print(f"Found {total} tasks in MongoDB")

        if total == 0:
            print("No tasks to migrate")
            return 0

        # Fetch all tasks
        cursor = tasks_collection.find({})
        tasks = await cursor.to_list(length=total)

        # Prepare data for insertion
        tasks_data = []
        for task in tqdm(tasks, desc="Processing tasks"):
            # Serialize config and result to JSON
            config = task.get("config", {})
            result = task.get("result")

            task_dict = {
                "name": task.get("name", ""),
                "task_type": task.get("task_type", ""),
                "config": json.dumps(config, ensure_ascii=False),
                "status": task.get("status", "pending"),
                "result": json.dumps(result, ensure_ascii=False) if result else None,
                "error_message": task.get("error_message"),
                "created_at": task.get("created_at", datetime.now()).isoformat(),
                "updated_at": task.get("updated_at", datetime.now()).isoformat(),
            }
            tasks_data.append(
                (
                    task_dict["name"],
                    task_dict["task_type"],
                    task_dict["config"],
                    task_dict["status"],
                    task_dict["result"],
                    task_dict["error_message"],
                    task_dict["created_at"],
                    task_dict["updated_at"],
                )
            )

        # Insert into SQLite
        await self.sqlite_conn.executemany(
            """
            INSERT INTO tasks (
                name, task_type, config, status, result,
                error_message, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            tasks_data,
        )
        await self.sqlite_conn.commit()

        print(f"✓ Migrated {len(tasks_data)} tasks")
        return len(tasks_data)

    async def verify_migration(self):
        """Verify migrated data"""
        print("\n=== Verifying Migration ===")

        # Get MongoDB counts
        mongo_db = self.mongo_client[self.mongodb_db]
        mongo_accounts = await mongo_db.accounts.count_documents({})
        mongo_jobs = await mongo_db.jobs.count_documents({})
        mongo_tasks = await mongo_db.tasks.count_documents({})

        # Get SQLite counts
        cursor = await self.sqlite_conn.execute("SELECT COUNT(*) FROM accounts")
        sqlite_accounts = (await cursor.fetchone())[0]

        cursor = await self.sqlite_conn.execute("SELECT COUNT(*) FROM jobs")
        sqlite_jobs = (await cursor.fetchone())[0]

        cursor = await self.sqlite_conn.execute("SELECT COUNT(*) FROM tasks")
        sqlite_tasks = (await cursor.fetchone())[0]

        print("\nRecord Counts:")
        print(
            "  Accounts: MongoDB={}, SQLite={} {}".format(
                mongo_accounts,
                sqlite_accounts,
                "✓" if mongo_accounts == sqlite_accounts else "✗ MISMATCH",
            ),
        )
        print(
            "  Jobs: MongoDB={}, SQLite={} {}".format(
                mongo_jobs,
                sqlite_jobs,
                "✓" if mongo_jobs == sqlite_jobs else "✗ MISMATCH",
            ),
        )
        print(
            "  Tasks: MongoDB={}, SQLite={} {}".format(
                mongo_tasks,
                sqlite_tasks,
                "✓" if mongo_tasks == sqlite_tasks else "✗ MISMATCH",
            ),
        )

        return (
            mongo_accounts == sqlite_accounts
            and mongo_jobs == sqlite_jobs
            and mongo_tasks == sqlite_tasks
        )

    async def migrate(self):
        """Execute full migration"""
        try:
            print("=" * 60)
            print("MongoDB to SQLite Migration")
            print("=" * 60)
            print(f"\nMongoDB: {self.mongodb_url}/{self.mongodb_db}")
            print(f"SQLite: {self.sqlite_path}")

            # Check if MongoDB is accessible
            try:
                await self.mongo_client.admin.command("ping")
                print("✓ MongoDB is accessible")
            except Exception as e:
                print(f"✗ Cannot connect to MongoDB: {e}")
                print("\nPlease ensure MongoDB is running:")
                print("  - Windows: Start MongoDB service")
                print("  - Linux/Mac: sudo systemctl start mongod")
                return False

            # Start transaction
            await self.sqlite_conn.execute("BEGIN TRANSACTION")

            # Migrate collections
            accounts_count = await self.migrate_accounts()
            jobs_count = await self.migrate_jobs()
            tasks_count = await self.migrate_tasks()

            # Verify migration
            verified = await self.verify_migration()

            if verified:
                # Commit transaction
                await self.sqlite_conn.commit()
                print("\n" + "=" * 60)
                print("✓ Migration completed successfully!")
                print("=" * 60)
                print("\nTotal records migrated:")
                print(f"  Accounts: {accounts_count}")
                print(f"  Jobs: {jobs_count}")
                print(f"  Tasks: {tasks_count}")
                print("\nYou can now start the application with SQLite.")
                return True
            else:
                # Rollback on verification failure
                await self.sqlite_conn.rollback()
                print("\n✗ Migration verification failed, transaction rolled back")
                return False

        except Exception as e:
            # Rollback on error
            await self.sqlite_conn.rollback()
            print(f"\n✗ Migration failed: {e}")
            import traceback

            traceback.print_exc()
            return False


async def main():
    """Main migration function"""
    print("\n" + "=" * 60)
    print("MongoDB to SQLite Migration Script")
    print("=" * 60)
    print("\nThis script will migrate data from MongoDB to SQLite.")
    print("Please ensure:")
    print("  1. MongoDB is running and accessible")
    print("  2. You have a backup of your MongoDB data")
    print("  3. The SQLite database file does not exist yet")
    print()

    # Check if SQLite file exists
    if SQLITE_DB_PATH.exists():
        print(f"⚠ WARNING: SQLite database already exists at: {SQLITE_DB_PATH}")
        response = input("Do you want to delete it and continue? (yes/no): ")
        if response.lower() != "yes":
            print("Migration cancelled")
            return
        SQLITE_DB_PATH.unlink()
        print("✓ Deleted existing SQLite database")

    # Confirm migration
    response = input("\nProceed with migration? (yes/no): ")
    if response.lower() != "yes":
        print("Migration cancelled")
        return

    # Create migrator and run migration
    migrator = MongoDBToSQLiteMigrator(
        mongodb_url=MONGODB_URL, mongodb_db=MONGODB_DB_NAME, sqlite_path=SQLITE_DB_PATH
    )

    try:
        await migrator.connect()
        success = await migrator.migrate()
        await migrator.close()

        if success:
            print("\n✓ All done! Your data has been migrated to SQLite.")
        else:
            print("\n✗ Migration failed. Please check the errors above.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nMigration cancelled by user")
        await migrator.close()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        await migrator.close()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
