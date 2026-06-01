from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.source import Source, SourceStatus, SourceType
from app.models.setting import SystemSetting

DEFAULT_CATEGORIES = [
    "企业动态",
    "政策监管",
    "价格材料",
    "制造工艺",
    "设备工艺",
    "产能项目",
    "技术路线",
    "投融资",
    "专利论文",
    "行业快讯",
]

DEFAULT_SOURCES = [
    {
        "name": "工业和信息化部 - 政策公告",
        "type": SourceType.policy,
        "entry_url": "https://www.miit.gov.cn/zwgk/zcwj/wjfb/gg/index.html",
        "domain": "www.miit.gov.cn",
        "notes": "官方公开政策公告候选源；默认仅手动抓取，确认 robots 和页面结构后再启用每日抓取。",
    },
    {
        "name": "国家发展改革委 - 通知公告",
        "type": SourceType.policy,
        "entry_url": "https://www.ndrc.gov.cn/xxgk/zcfb/tz/",
        "domain": "www.ndrc.gov.cn",
        "notes": "官方公开政策候选源，关注产业政策、价格和新型储能相关通知；默认仅手动抓取。",
    },
    {
        "name": "国家能源局 - 能源要闻",
        "type": SourceType.policy,
        "entry_url": "https://www.nea.gov.cn/xwzx/nyyw.htm",
        "domain": "www.nea.gov.cn",
        "notes": "官方公开能源资讯候选源，关注储能、电力系统和能源政策；默认仅手动抓取。",
    },
    {
        "name": "自然资源部 - 要闻播报",
        "type": SourceType.announcement,
        "entry_url": "https://www.mnr.gov.cn/dt/ywbb/",
        "domain": "www.mnr.gov.cn",
        "notes": "官方公开资源资讯候选源，关注锂矿、资源政策和矿产信息；默认仅手动抓取。",
    },
    {
        "name": "中国储能网 - 锂离子电池",
        "type": SourceType.media,
        "entry_url": "https://www.escn.com.cn/news/700-4.html",
        "domain": "www.escn.com.cn",
        "notes": "行业媒体候选源，关注锂离子电池与储能应用；默认仅手动抓取，确认转载和展示边界后再启用。",
    },
    {
        "name": "中国电力企业联合会 - 新闻中心",
        "type": SourceType.media,
        "entry_url": "https://www.cec.org.cn/detail/index.html?3-12",
        "domain": "www.cec.org.cn",
        "notes": "公开行业资讯候选源，关注电力系统、新型储能和能源转型；默认仅手动抓取，确认合规后再启用。",
    },
]

REMOVED_DEFAULT_SOURCE_URLS = [
    "https://www.cbea.com/",
]


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

    for source_data in DEFAULT_SOURCES:
        source = db.query(Source).filter(Source.entry_url == source_data["entry_url"]).first()
        if source is None:
            db.add(
                Source(
                    **source_data,
                    status=SourceStatus.manual_only,
                    parser_key="generic",
                    crawl_interval_minutes=1440,
                    domain_delay_seconds=5,
                    max_pages_per_run=10,
                    daily_limit=20,
                )
            )

    for entry_url in REMOVED_DEFAULT_SOURCE_URLS:
        source = db.query(Source).filter(Source.entry_url == entry_url).first()
        if source is not None:
            db.delete(source)

    for source in db.query(Source).filter(Source.last_error == "robots_disallow").all():
        source.status = SourceStatus.blocked_by_policy
        source.notes = "robots.txt 禁止抓取，已自动标记为禁止策略状态。"
    db.commit()
