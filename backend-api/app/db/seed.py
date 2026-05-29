from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.daily_brief import DailyBrief
from app.models.source import Source
from app.models.setting import SystemSetting

DEFAULT_CATEGORIES = ["企业动态", "政策监管", "价格材料", "设备工艺", "产能项目", "技术路线", "投融资", "专利论文", "行业快讯"]


def seed_defaults(db: Session) -> None:
    for name in DEFAULT_CATEGORIES:
        if not db.query(Category).filter(Category.name == name).first():
            db.add(Category(name=name, kind="industry", description=f"{name}分类"))

    if not db.query(SystemSetting).filter(SystemSetting.key == "daily_brief_time").first():
        db.add(SystemSetting(key="daily_brief_time", value="07:30", description="每日摘要生成时间"))
    if not db.query(SystemSetting).filter(SystemSetting.key == "crawl_time").first():
        db.add(SystemSetting(key="crawl_time", value="07:00", description="启用来源自动抓取时间"))
    if not db.query(SystemSetting).filter(SystemSetting.key == "sensitive_words").first():
        db.add(SystemSetting(key="sensitive_words", value="", description="逗号分隔的敏感词"))

    db.query(Source).filter(
        Source.name == "示例禁用来源",
        Source.domain == "example.com",
    ).delete(synchronize_session=False)
    db.query(DailyBrief).filter(
        DailyBrief.title == "今日锂电投研摘要",
        DailyBrief.overview == "暂无新增情报。",
    ).delete(synchronize_session=False)
    db.commit()
