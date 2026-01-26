from __future__ import annotations
from typing import List, Optional, Dict, Any
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from app.config import settings

_db = None

def get_db():
    global _db
    if _db is None:
        if not firebase_admin._apps:
            # Get credentials from config (supports both file and Secret Manager)
            cred_dict = settings.get_firebase_credentials()
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {"projectId": settings.firebase_project_id})
        _db = firestore.client()
    return _db

class TradeRepository:
    def __init__(self):
        self.db = get_db()
        self.col = self.db.collection("trades")

    def add_trade(self, trade: Dict[str, Any]) -> None:
        self.col.document(trade["tradeId"]).set(trade)

    def get_trade(self, trade_id: str) -> Optional[Dict[str, Any]]:
        doc = self.col.document(trade_id).get()
        return doc.to_dict() if doc.exists else None

    def list_trades(self, user_id: str, ticker: Optional[str] = None) -> List[Dict[str, Any]]:
        q = self.col.where(filter=firestore.FieldFilter("userId", "==", user_id))
        if ticker:
            q = q.where(filter=firestore.FieldFilter("ticker", "==", ticker))
        # Firestore ordering: orderDate then seq
        q = q.order_by("orderDate").order_by("seq")
        return [d.to_dict() for d in q.stream()]

    def list_trades_by_side(self, user_id: str, ticker: str, side: str) -> List[Dict[str, Any]]:
        q = (
            self.col.where(filter=firestore.FieldFilter("userId", "==", user_id))
            .where(filter=firestore.FieldFilter("ticker", "==", ticker))
            .where(filter=firestore.FieldFilter("side", "==", side))
            .order_by("orderDate")
            .order_by("seq")
        )
        return [d.to_dict() for d in q.stream()]

class AllocationRepository:
    def __init__(self):
        self.db = get_db()
        self.col = self.db.collection("fifo_allocations")

    def add_allocation(self, alloc: Dict[str, Any]) -> None:
        self.col.document(alloc["allocId"]).set(alloc)

    def list_allocations(self, user_id: str, ticker: Optional[str] = None) -> List[Dict[str, Any]]:
        q = self.col.where(filter=firestore.FieldFilter("userId", "==", user_id))
        if ticker:
            q = q.where(filter=firestore.FieldFilter("ticker", "==", ticker))
        q = q.order_by("createdAt")
        return [d.to_dict() for d in q.stream()]

    def list_allocations_for_buy(self, user_id: str, buy_trade_id: str) -> List[Dict[str, Any]]:
        q = (
            self.col.where(filter=firestore.FieldFilter("userId", "==", user_id))
            .where(filter=firestore.FieldFilter("buyTradeId", "==", buy_trade_id))
        )
        return [d.to_dict() for d in q.stream()]

class UserRepository:
    def __init__(self):
        self.db = get_db()
        self.col = self.db.collection("users")

    def upsert_user(self, user_id: str, user_name: str, chat_id: Optional[int] = None) -> None:
        user_data = {
            "userId": user_id,
            "userName": user_name,
            "registerDate": datetime.utcnow()
        }
        if chat_id is not None:
            user_data["chat_id"] = chat_id
        self.col.document(user_id).set(user_data, merge=True)

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        doc = self.col.document(user_id).get()
        return doc.to_dict() if doc.exists else None

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all registered users"""
        docs = self.col.stream()
        return [d.to_dict() for d in docs]
