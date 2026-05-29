from dataclasses import dataclass

from rapidfuzz import fuzz
from sqlalchemy.orm import Session

from app.models.intelligence import IntelligenceItem
from app.models.setting import SystemSetting
from app.services.text import csv_to_set, normalize_title


@dataclass(frozen=True)
class PublishDecision:
    allowed: bool
    reason: str = ""


class PublishGuard:
    def __init__(self, db: Session, min_content_length: int = 30, duplicate_threshold: float = 92.0) -> None:
        self.db = db
        self.min_content_length = min_content_length
        self.duplicate_threshold = duplicate_threshold

    def evaluate(self, *, title: str, content: str, source_url: str) -> PublishDecision:
        if not source_url:
            return PublishDecision(False, "missing_source_url")
        if not title.strip():
            return PublishDecision(False, "missing_title")
        if len(content.strip()) < self.min_content_length:
            return PublishDecision(False, "content_too_short")

        sensitive = self.db.query(SystemSetting).filter(SystemSetting.key == "sensitive_words").first()
        for word in csv_to_set(sensitive.value if sensitive else ""):
            if word in f"{title} {content}":
                return PublishDecision(False, "sensitive_word")

        normalized = normalize_title(title)
        if self.db.query(IntelligenceItem).filter(IntelligenceItem.normalized_title == normalized).first():
            return PublishDecision(False, "duplicate_title")
        for (recent_title,) in self.db.query(IntelligenceItem.normalized_title).order_by(IntelligenceItem.id.desc()).limit(200).all():
            if fuzz.ratio(normalized, recent_title) >= self.duplicate_threshold:
                return PublishDecision(False, "similar_title")
        return PublishDecision(True)
