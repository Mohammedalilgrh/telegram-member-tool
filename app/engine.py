"""
Telegram engine — multi-account, auto-rotation, bulletproof
"""
import asyncio
import json
import logging
import random
from typing import List, Optional, Tuple

from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError, UserPrivacyRestrictedError,
    UserNotMutualContactError, UserChannelsTooManyError,
    UserKickedError, UserBannedInChannelError,
    InviteHashExpiredError, InviteHashInvalidError,
    UsernameNotOccupiedError, SessionPasswordNeededError,
)
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest, ImportChatInviteRequest
from telethon.tl.types import InputPeerUser, Channel, Chat

from app.state import state

logger = logging.getLogger(__name__)


def make_client(session_str: str, api_id: int, api_hash: str) -> TelegramClient:
    return TelegramClient(
        session=session_str,
        api_id=api_id,
        api_hash=api_hash,
        request_retries=3,
        connection_retries=3,
        retry_delay=2,
        # Spoof a recent-ish app version so Telegram doesn't complain
        device_model="Desktop",
        system_version="Windows 10",
        app_version="4.16.0",
    )


async def create_account(
    client: TelegramClient,
    phone: str,
    api_id: int,
    api_hash: int,
) -> dict:
    """Step 1: send code. Returns phone_code_hash."""
    await client.connect()
    sent = await client.send_code_request(phone)
    return {
        "phone": phone,
        "phone_code_hash": sent.phone_code_hash,
        "timeout": sent.timeout,
    }


async def verify_account(
    client: TelegramClient,
    phone: str,
    code: str,
    password: str = "",
) -> dict:
    """Step 2: verify code. Returns session_string."""
    if not await client.is_user_authorized():
        try:
            await client.sign_in(phone, code=code)
        except SessionPasswordNeededError:
            if not password:
                return {"status": "2fa_needed"}
            await client.sign_in(password=password)
    me = await client.get_me()
    session_str = client.session.save()
    return {
        "status": "ok",
        "phone": phone,
        "username": me.username or "",
        "name": f"{me.first_name or ''} {me.last_name or ''}".strip(),
        "session_string": session_str,
    }


async def resolve_group(client: TelegramClient, identifier: str):
    """Resolve any group identifier to an entity."""
    identifier = identifier.strip()
    if "/+" in identifier or "/joinchat/" in identifier:
        if "/joinchat/" in identifier:
            hash_str = identifier.split("/joinchat/")[-1].split("?")[0]
        else:
            hash_str = identifier.split("/+")[-1].split("?")[0]
        try:
            updates = await client(ImportChatInviteRequest(hash_str))
            if updates.chats:
                return updates.chats[0]
        except (InviteHashExpiredError, InviteHashInvalidError):
            raise ValueError("Invite link expired")
        except Exception:
            pass
    if identifier.startswith("@"):
        identifier = identifier[1:]
    try:
        return await client.get_entity(identifier)
    except (UsernameNotOccupiedError, ValueError):
        pass
    try:
        return await client.get_entity(int(identifier))
    except (ValueError, Exception):
        pass
    raise ValueError(f"Cannot resolve: {identifier}")


async def scrape_members(
    client: TelegramClient, group_identifier: str, limit: Optional[int] = None
) -> List[dict]:
    """Scrape members from a group."""
    entity = await resolve_group(client, group_identifier)
    title = getattr(entity, "title", str(entity.id))
    logger.info(f"Scraping: {title}")

    members = []
    seen = set()

    async for p in client.iter_participants(entity, aggressive=True, limit=limit):
        if p.id in seen:
            continue
        seen.add(p.id)
        members.append({
            "id": p.id,
            "username": p.username or "",
            "first_name": p.first_name or "",
            "last_name": p.last_name or "",
            "is_bot": p.bot if hasattr(p, "bot") else False,
            "is_scam": p.scam if hasattr(p, "scam") else False,
            "is_fake": p.fake if hasattr(p, "fake") else False,
            "is_premium": p.premium if hasattr(p, "premium") else False,
        })
        await asyncio.sleep(random.uniform(0.2, 0.4))
        if limit and len(members) >= limit:
            break

    logger.info(f"Scraped {len(members)} from {title}")
    return members


async def add_members_from_account(
    client: TelegramClient,
    target_group: str,
    user_ids: List[int],
    phone: str,
    daily_limit: int,
    min_delay: float,
    max_delay: float,
    dry_run: bool = False,
) -> dict:
    """
    Add members using ONE account. Respects per-account daily/hourly limits.
    Returns result dict.
    """
    if not user_ids:
        return {"added": 0, "failed": 0, "error": "No users"}

    entity = await resolve_group(client, target_group)
    title = getattr(entity, "title", str(entity.id))
    is_sg = isinstance(entity, Channel)
    is_bg = isinstance(entity, Chat)

    if not is_sg and not is_bg:
        raise ValueError("Target is not a group")

    acc_state = state.get_account(phone)
    remaining = acc_state.remaining(daily_limit)
    if remaining <= 0:
        return {"added": 0, "failed": 0, "error": "Daily limit reached", "account_phone": phone}

    user_ids = user_ids[:remaining]

    if dry_run:
        return {
            "added": 0, "failed": 0, "dry_run": True,
            "would_add": len(user_ids), "target": title,
            "account": phone, "remaining": remaining,
        }

    added = 0
    failed = 0
    fails = []

    for uid in user_ids:
        if not acc_state.can_add(daily_limit):
            logger.info(f"[{phone}] Daily or hourly limit reached. Stopping.")
            break

        try:
            if is_sg:
                await client(InviteToChannelRequest(entity, [InputPeerUser(uid, 0)]))
            else:
                await client(AddChatUserRequest(entity.id, InputPeerUser(uid, 0), fwd_limit=50))
            added += 1
            acc_state.add_one()
            state.total_all_time += 1
            await asyncio.sleep(random.uniform(min_delay, max_delay))

        except FloodWaitError as e:
            wait = e.seconds + 5
            logger.warning(f"[{phone}] FloodWait {wait}s")
            if wait > 1800:
                failed += 1
                fails.append({"id": uid, "r": f"flood_{wait}s"})
                break
            await asyncio.sleep(wait)
            # Retry
            try:
                if is_sg:
                    await client(InviteToChannelRequest(entity, [InputPeerUser(uid, 0)]))
                else:
                    await client(AddChatUserRequest(entity.id, InputPeerUser(uid, 0), fwd_limit=50))
                added += 1
                acc_state.add_one()
                state.total_all_time += 1
                await asyncio.sleep(random.uniform(min_delay, max_delay))
            except Exception as e2:
                failed += 1
                fails.append({"id": uid, "r": str(e2)[:60]})

        except (UserPrivacyRestrictedError, UserNotMutualContactError,
                UserKickedError, UserBannedInChannelError):
            failed += 1
        except UserChannelsTooManyError:
            failed += 1
            fails.append({"id": uid, "r": "too_many_groups"})
        except Exception as e:
            failed += 1
            fails.append({"id": uid, "r": str(e)[:60]})

    return {
        "added": added,
        "failed": failed,
        "target": title,
        "account": phone,
        "remaining_after": acc_state.remaining(daily_limit),
    }


async def run_pipeline_with_all_accounts(
    accounts: List[dict],
    daily_limit: int,
    source_group: str,
    target_group: str,
    max_members: int,
    min_delay: float,
    max_delay: float,
    api_id: int,
    api_hash: str,
) -> dict:
    """
    Full pipeline:
    1. Scrape once (using first account)
    2. Filter quality users
    3. Shuffle
    4. Distribute across ALL accounts, auto-rotate
    """
    # 1. Connect first account for scraping
    first_acc = accounts[0]
    client = make_client(first_acc["session"], api_id, api_hash)
    await client.connect()

    members = await scrape_members(client, source_group, limit=max_members)
    await client.disconnect()
    logger.info(f"Scraped {len(members)} total")

    # 2. Filter
    quality = [
        m for m in members
        if not m.get("is_bot") and not m.get("is_scam") and not m.get("is_fake")
        and m.get("username")
    ]
    random.shuffle(quality)
    ids_to_add = [u["id"] for u in quality]
    logger.info(f"After filter: {len(ids_to_add)} quality users")

    if not ids_to_add:
        return {"total_added": 0, "accounts_used": 0, "error": "No quality users found"}

    # 3. Distribute across accounts
    total_added = 0
    total_failed = 0
    accounts_used = 0
    account_results = []

    remaining_ids = ids_to_add[:]
    # Cycle through accounts until no limit remains
    for acc in accounts:
        if not remaining_ids:
            break
        acc_state = state.get_account(acc["phone"])
        acc_remaining = acc_state.remaining(daily_limit)
        if acc_remaining <= 0:
            logger.info(f"[{acc['phone']}] Already at daily limit, skipping")
            continue

        try:
            acc_client = make_client(acc["session"], api_id, api_hash)
            await acc_client.connect()

            batch = remaining_ids[:acc_remaining]
            result = await add_members_from_account(
                acc_client, target_group, batch,
                acc["phone"], daily_limit,
                min_delay, max_delay,
            )

            await acc_client.disconnect()
            accounts_used += 1
            total_added += result.get("added", 0)
            total_failed += result.get("failed", 0)
            account_results.append(result)
            logger.info(f"[{acc['phone']}] Added {result.get('added', 0)}")

            # Remove added users from remaining
            added_count = result.get("added", 0)
            if added_count > 0:
                remaining_ids = remaining_ids[added_count:]

        except Exception as e:
            logger.error(f"[{acc['phone']}] Failed: {e}")
            continue

    state.last_run_status = "ok" if total_added > 0 else "failed"
    state.last_error = "" if total_added > 0 else "All accounts failed"
    from datetime import datetime
    state.last_run = datetime.utcnow().isoformat()

    return {
        "total_added": total_added,
        "total_failed": total_failed,
        "accounts_used": accounts_used,
        "scraped": len(members),
        "filtered": len(ids_to_add),
        "account_results": account_results,
    }
