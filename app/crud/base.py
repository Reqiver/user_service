from typing import List, Optional, Type, TypeVar, Generic

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel
from pymongo.errors import DuplicateKeyError


BaseSchemaType = TypeVar("BaseSchemaType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[BaseSchemaType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[BaseSchemaType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `coll`: A MongoDB collection object
        * `model`: A Pydantic Base model (schema) class used to retrieve data
        """
        self.model = model

    async def get(self, _id: str, coll: AsyncIOMotorCollection) -> Optional[BaseSchemaType]:
        obj = await coll.find_one({"id": _id})
        if obj:
            return self.model(**obj)

    async def get_multi(
            self, coll: AsyncIOMotorCollection, skip: int = 0, limit: int = 12,
    ) -> List[BaseSchemaType]:
        cursor = coll.find().skip(skip).limit(limit)
        objs = [self.model(**obj) async for obj in cursor]
        return objs

    async def create(
            self, obj_in: CreateSchemaType, coll: AsyncIOMotorCollection,
    ) -> BaseSchemaType:
        obj_dict = obj_in.dict()
        try:
            await coll.insert_one(obj_dict)
            return self.model(**obj_dict)
        except DuplicateKeyError:
            raise HTTPException(
                status_code=400, detail="Duplicate object already exists"
            )

    async def update(
            self, _id: str, obj_in: UpdateSchemaType | dict, coll: AsyncIOMotorCollection,
    ) -> Optional[BaseSchemaType]:
        obj = await self.get(_id, coll)
        if not obj:
            return None
        if isinstance(obj_in, BaseModel):
            update_data = obj_in.dict(exclude_unset=True)
        else:
            update_data = obj_in
        obj_dict = obj.dict()
        obj_dict.update(update_data)
        obj = self.model(**obj_dict)
        await coll.update_one({"id": _id}, {"$set": obj_dict})
        return obj

    async def remove(self, _id: str, coll: AsyncIOMotorCollection) -> Optional[BaseModel]:
        obj = await self.get(_id, coll)
        if obj:
            await coll.delete_one({"id": _id})
        return obj
