"""
账户服务
"""
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from ..core.logging import get_logger
from ..schemas.account import AccountCreate, AccountUpdate, AccountResponse

logger = get_logger("account_service")


class AccountService:
    """账户服务类"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.accounts

    async def create(self, account: AccountCreate) -> AccountResponse:
        """创建账户"""
        account_dict = account.model_dump()
        # 移除密码字段，不存储明文密码
        account_dict.pop("password", None)
        account_dict["created_at"] = datetime.now()
        account_dict["updated_at"] = datetime.now()
        account_dict["cookie_status"] = "none"

        result = await self.collection.insert_one(account_dict)
        account_dict["id"] = str(result.inserted_id)

        logger.info(f"Created account: {account_dict['id']}")
        return AccountResponse(**account_dict)

    async def get_by_id(self, account_id: str) -> Optional[AccountResponse]:
        """根据ID获取账户"""
        try:
            obj_id = ObjectId(account_id)
            account = await self.collection.find_one({"_id": obj_id})
            if account:
                account["id"] = str(account.pop("_id"))
                return AccountResponse(**account)
        except Exception as e:
            logger.error(f"Error getting account: {e}")
        return None

    async def get_by_phone(self, phone: str) -> Optional[AccountResponse]:
        """根据手机号获取账户"""
        try:
            account = await self.collection.find_one({"phone": phone})
            if account:
                account["id"] = str(account.pop("_id"))
                return AccountResponse(**account)
        except Exception as e:
            logger.error(f"Error getting account by phone: {e}")
        return None

    async def get_list(
        self, skip: int = 0, limit: int = 10, is_active: Optional[bool] = None
    ) -> tuple[List[AccountResponse], int]:
        """获取账户列表"""
        query = {}
        if is_active is not None:
            query["is_active"] = is_active

        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        accounts = await cursor.to_list(length=limit)
        total = await self.collection.count_documents(query)

        result = []
        for account in accounts:
            account["id"] = str(account.pop("_id"))
            result.append(AccountResponse(**account))

        return result, total

    async def update(self, account_id: str, account: AccountUpdate) -> Optional[AccountResponse]:
        """更新账户"""
        try:
            obj_id = ObjectId(account_id)
            update_data = {k: v for k, v in account.model_dump().items() if v is not None}
            update_data["updated_at"] = datetime.now()

            await self.collection.update_one({"_id": obj_id}, {"$set": update_data})
            return await self.get_by_id(account_id)
        except Exception as e:
            logger.error(f"Error updating account: {e}")
            return None

    async def update_cookie_status(
        self, account_id: str, cookie_status: str
    ) -> Optional[AccountResponse]:
        """更新Cookie状态"""
        try:
            obj_id = ObjectId(account_id)
            update_data = {
                "cookie_status": cookie_status,
                "updated_at": datetime.now(),
            }
            if cookie_status == "valid":
                update_data["last_login"] = datetime.now()

            await self.collection.update_one({"_id": obj_id}, {"$set": update_data})
            logger.info(f"Updated cookie status: {account_id} -> {cookie_status}")
            return await self.get_by_id(account_id)
        except Exception as e:
            logger.error(f"Error updating cookie status: {e}")
            return None

    async def delete(self, account_id: str) -> bool:
        """删除账户"""
        try:
            obj_id = ObjectId(account_id)
            result = await self.collection.delete_one({"_id": obj_id})
            logger.info(f"Deleted account: {account_id}, deleted_count: {result.deleted_count}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting account: {e}")
            return False
