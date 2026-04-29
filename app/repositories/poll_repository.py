from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.models.poll import Poll
from app.repositories.base import BaseRepository


class PollRepository(BaseRepository[Poll]):
    def __init__(self, db: Session):
        super().__init__(Poll, db)

    def get_all_polls(self) -> list[Poll]:
        """Barcha polllar (draft, active, closed)"""
        return self.db.query(Poll).order_by(Poll.created_at.desc()).all()

    def get_active_polls(self) -> list[Poll]:
        """Faqat faol (active) va sana oralig'idagi polllar"""
        now = datetime.utcnow()
        return (
            self.db.query(Poll)
            .filter(
                Poll.status == "active",
                Poll.start_date <= now,
                Poll.end_date >= now,
            )
            .all()
        )

    def get_by_status(self, status: str) -> list[Poll]:
        """Status bo'yicha polllar"""
        return self.db.query(Poll).filter(Poll.status == status).all()

    def get_with_options(self, poll_id: int) -> Poll | None:
        """Bitta poll + variantlari"""
        return (
            self.db.query(Poll)
            .options(joinedload(Poll.options))
            .filter(Poll.id == poll_id)
            .first()
        )

    def get_all_with_options(self) -> list[Poll]:
        """Barcha polllar + variantlari"""
        return (
            self.db.query(Poll)
            .options(joinedload(Poll.options))
            .order_by(Poll.created_at.desc())
            .all()
        )
