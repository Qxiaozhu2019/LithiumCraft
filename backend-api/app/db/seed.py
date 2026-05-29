from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.daily_brief import DailyBrief, BriefStatus
from app.models.source import Source, SourceStatus, SourceType
from app.models.setting import SystemSetting

DEFAULT_CATEGORIES = ["企业动态", "政策监管", "价格材料", "设备工艺", "产能项目", "技术路线", "投融资", "专利论文", "行业快讯"]


def seed_defaults(db: Session) -> None:
    for name in DEFAULT_CATEGORIES:
        if not db.query(Category).filter(Category.name == name).first():
            db.add(Category(name=name, kind="industry", description=f"{name}分类"))

    if not db.query(SystemSetting).filter(SystemSetting.key == "daily_brief_time").first():
        db.add(SystemSetting(key="daily_brief_time", value="18:00", description="每日摘要生成时间"))
    if not db.query(SystemSetting).filter(SystemSetting.key == "sensitive_words").first():
        db.add(SystemSetting(key="sensitive_words", value="", description="逗号分隔的敏感词"))

    if not db.query(Source).filter(Source.name == "示例禁用来源").first():
        db.add(Source(
            name="示例禁用来源",
            type=SourceType.rss,
            entry_url="https://example.com/feed.xml",
            domain="example.com",
            status=SourceStatus.disabled,
            notes="默认禁用，避免首次启动访问外部网站。",
        ))

    if not db.query(DailyBrief).filter(DailyBrief.brief_date == date.today()).first():
        db.add(DailyBrief(
            brief_date=date.today(),
            title="今日锂电投研摘要",
            overview="暂无新增情报。",
            highlights="[]",
            category_summary="{}",
            status=BriefStatus.success,
            generated_at=datetime.now(timezone.utc),
        ))
    db.commit()
