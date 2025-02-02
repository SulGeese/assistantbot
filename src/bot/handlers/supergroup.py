from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION

from db.redis import redis
from db.requests import insert_user_into_group, del_user_from_group

sgr_router = Router()
sgr_router.message.filter(F.chat.type == "supergroup")
sgr_router.chat_member.filter(F.chat.type == "supergroup")
sgr_router.callback_query.filter(F.chat.type == "supergroup")


@sgr_router.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def supergroup_message_handler(message: Message, session: AsyncSession):
    await insert_user_into_group(
        session=session,
        user_id=message.new_chat_member.user.id,
        username=message.new_chat_member.user.username,
        first_name=message.new_chat_member.user.first_name,
        last_name=message.new_chat_member.user.last_name,
    )
    if await redis.exists("users"):
        await redis.delete("users")


@sgr_router.chat_member(ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def supergroup_message_handler(message: Message, session: AsyncSession):
    await del_user_from_group(
        session=session,
        user_id=message.old_chat_member.user.id,
    )
    if await redis.exists("users"):
        await redis.delete("users")
