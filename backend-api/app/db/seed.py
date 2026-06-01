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
        "name": "工信部 - 锂电池行业规范公告候选",
        "type": SourceType.policy,
        "entry_url": "https://www.miit.gov.cn/zwgk/zcwj/wjfb/gg/index.html",
        "domain": "www.miit.gov.cn",
        "notes": "target_process=全流程; source_type=official; robots_status=pending_manual_review; auto_crawl=false; 仅作为工艺规范候选入口，确认 robots、详情页和图片规则后再启用。",
    },
    {
        "name": "国家标准全文公开系统 - 工艺标准候选",
        "type": SourceType.policy,
        "entry_url": "https://openstd.samr.gov.cn/bzgk/gb/index",
        "domain": "openstd.samr.gov.cn",
        "notes": "target_process=全流程; source_type=standard; robots_status=pending_manual_review; auto_crawl=false; 不抓站内搜索结果，人工确认可访问标准说明页后再启用。",
    },
    {
        "name": "中科院物理所 - 电池工艺公开资料候选",
        "type": SourceType.paper,
        "entry_url": "https://www.iop.cas.cn/",
        "domain": "www.iop.cas.cn",
        "notes": "target_process=材料/制浆/化成; source_type=research; robots_status=pending_manual_review; auto_crawl=false; 仅保留命中制造工艺关键词的公开资料。",
    },
    {
        "name": "中国科学院过程工程研究所 - 电池过程公开资料候选",
        "type": SourceType.paper,
        "entry_url": "https://www.ipe.cas.cn/",
        "domain": "www.ipe.cas.cn",
        "notes": "target_process=制浆/涂布/干燥; source_type=research; robots_status=pending_manual_review; auto_crawl=false; 人工确认栏目和 robots 后才可启用。",
    },
    {
        "name": "中国电池工业协会 - 工艺公开资料候选",
        "type": SourceType.webpage,
        "entry_url": "https://www.chinabattery.org/",
        "domain": "www.chinabattery.org",
        "notes": "target_process=全流程; source_type=association; robots_status=pending_manual_review; auto_crawl=false; 仅抓公开且 robots 允许的制造工艺资料。",
    },
]

PROCESS_PAGE_SOURCES = [
    ("\u5236\u6d46", "Neware - \u5236\u6d46", "https://www.neware.net/support/slurry-preparation-manufacturing-process-terminology/217/497.html"),
    ("\u6d82\u5e03", "Neware - \u6d82\u5e03", "https://www.neware.net/support/coating-manufacturing-process-terminology/217/499.html"),
    ("\u8f8a\u538b", "Neware - \u8f8a\u538b", "https://www.neware.net/support/roll-pressing-manufacturing-process-terminology/217/503.html"),
    ("\u5206\u5207", "Neware - \u6781\u7247\u5206\u5207\u8bbe\u5907", "https://www.neware.net/support/electrode-slitting-machine-manufacturing-equipment-terminology/218/541.html"),
    ("\u5377\u7ed5/\u53e0\u7247", "Neware - \u5377\u7ed5", "https://www.neware.net/support/winding-manufacturing-process-terminology/217/508.html"),
    ("\u5377\u7ed5/\u53e0\u7247", "Neware - \u53e0\u7247", "https://www.neware.net/support/stacking-manufacturing-process-terminology/217/509.html"),
    ("\u88c5\u914d", "Neware - \u5165\u58f3", "https://www.neware.net/support/inserting-can-manufacturing-process-terminology/217/521.html"),
    ("\u6ce8\u6db2", "Neware - \u6ce8\u6db2", "https://www.neware.net/support/electrolyte-injection-manufacturing-process-terminology/217/529.html"),
    ("\u5316\u6210", "Neware - \u5316\u6210", "https://www.neware.net/support/formation-manufacturing-process-terminology/217/530.html"),
    ("\u5206\u5bb9", "Neware - \u5206\u5bb9\u8bbe\u5907", "https://www.neware.net/support/capacity-grading-machine-manufacturing-equipment-terminology/218/587.html"),
    ("\u68c0\u6d4b", "Neware - X-ray \u68c0\u6d4b", "https://www.neware.net/support/x-ray-detection-manufacturing-process-terminology/217/518.html"),
]
DEFAULT_SOURCES.extend(
    {
        "name": name,
        "type": SourceType.webpage,
        "entry_url": entry_url,
        "domain": "www.neware.net",
        "parser_key": "single_page",
        "notes": f"target_process={process}; source_type=process_terminology; robots_status=pending_manual_review; auto_crawl=false",
    }
    for process, name, entry_url in PROCESS_PAGE_SOURCES
)

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
            data = source_data.copy()
            parser_key = data.pop("parser_key", "generic")
            db.add(
                Source(
                    **data,
                    status=SourceStatus.manual_only,
                    parser_key=parser_key,
                    crawl_interval_minutes=1440,
                    domain_delay_seconds=5,
                    max_pages_per_run=1 if parser_key == "single_page" else 10,
                    daily_limit=1 if parser_key == "single_page" else 20,
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
