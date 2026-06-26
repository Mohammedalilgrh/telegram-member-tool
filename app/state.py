"""
State — per-account daily counters, auto-reset at midnight UTC
"""
import json
import logging
from datetime import date, datetime
from typing import Dict

logger = logging.getLogger(__name__)


class AccountState:
    def __init__(self, phone: str):
        self.phone = phone
        self.added_today = 0
        self.hourly_count = 0
        self.last_reset = date.today().isoformat()
        self.last_hour_reset = datetime.utcnow().hour

    def check_reset(self):
        today = date.today().isoformat()
        now_hour = datetime.utcnow().hour
        if self.last_reset != today:
            self.added_today = 0
            self.hourly_count = 0
            self.last_reset = today
            self.last_hour_reset = now_hour
            logger.info(f"[{self.phone}] Daily reset")
        if self.last_hour_reset != now_hour:
            self.hourly_count = 0
            self.last_hour_reset = now_hour

    def can_add(self, daily_limit: int) -> bool:
        self.check_reset()
        return self.added_today < daily_limit and self.hourly_count < 15

    def remaining(self, daily_limit: int) -> int:
        self.check_reset()
        return max(0, daily_limit - self.added_today)

    def add_one(self):
        self.added_today += 1
        self.hourly_count += 1


class GlobalState:
    def __init__(self):
        self.accounts: Dict[str, AccountState] = {}
        self.total_all_time = 0
        self.last_run: str = "never"
        self.last_run_status: str = "idle"
        self.last_error: str = ""

    def get_account(self, phone: str) -> AccountState:
        if phone not in self.accounts:
            self.accounts[phone] = AccountState(phone)
        return self.accounts[phone]

    def to_dict(self, daily_limit: int) -> dict:
        accounts_info = []
        total_added_today = 0
        for phone, acc in self.accounts.items():
            acc.check_reset()
            remaining = acc.remaining(daily_limit)
            total_added_today += acc.added_today
            accounts_info.append({
                "phone": phone[:5] + "***" if len(phone) > 5 else phone,
                "added_today": acc.added_today,
                "remaining": remaining,
                "can_add": remaining > 0,
                "daily_limit": daily_limit,
            })
        return {
            "total_added_today": total_added_today,
            "total_all_time": self.total_all_time,
            "last_run": self.last_run,
            "last_run_status": self.last_run_status,
            "last_error": self.last_error,
            "accounts": accounts_info,
            "active_accounts": len(self.accounts),
            "date": date.today().isoformat(),
            "daily_limit_per_account": daily_limit,
        }


state = GlobalState()
