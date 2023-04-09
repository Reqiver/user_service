from typing import Optional

from motor.motor_asyncio import AsyncIOMotorCollection

from app.crud.base import CRUDBase
from app.schemas import RetrieveUser, CreateUser, UpdateUser, RetrieveUserWithPass


class UserCRUD(CRUDBase[RetrieveUser, CreateUser, UpdateUser]):
    async def get_with_hash_pass(
            self, _id: str, coll: AsyncIOMotorCollection,
    ) -> Optional[RetrieveUserWithPass]:
        obj = await coll.find_one({"id": _id})
        if obj:
            return RetrieveUserWithPass(**obj)


user = UserCRUD(RetrieveUser)
