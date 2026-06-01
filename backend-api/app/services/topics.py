from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Query, Session

from app.models.intelligence import IntelligenceItem, IntelligenceStatus


@dataclass(frozen=True)
class Topic:
    slug: str
    name: str
    summary: str
    description: str
    keywords: tuple[str, ...]
    related_process_slugs: tuple[str, ...]
    key_properties: tuple[str, ...]
    process_impacts: tuple[str, ...]


TOPICS: tuple[Topic, ...] = (
    Topic(
        slug="cathode-materials",
        name="正极材料",
        summary="理解 LFP、NCM/NCA、LMO、LCO 的容量、电压、安全和成本差异。",
        description="正极材料决定电芯能量密度、电压平台、热稳定性和成本边界，也会影响制浆分散、涂布面密度、辊压压实和化成制度。",
        keywords=(
            "正极",
            "磷酸铁锂",
            "LFP",
            "三元",
            "NCM",
            "NCA",
            "锰酸锂",
            "LMO",
            "钴酸锂",
            "LCO",
            "正极材料",
            "cathode",
        ),
        related_process_slugs=("slurry", "coating", "calendering", "formation", "inspection"),
        key_properties=("容量", "电压平台", "热稳定性", "成本", "安全性"),
        process_impacts=("颗粒形貌影响浆料粘度和分散窗口", "材料压实能力影响辊压密度和孔隙结构", "表面副反应影响化成制度和循环表现"),
    ),
    Topic(
        slug="anode-materials",
        name="负极材料",
        summary="关注石墨、硅碳、硬碳、锂金属的比容量、膨胀、首效和循环稳定性。",
        description="负极材料影响首次效率、倍率、膨胀和 SEI 成膜，对制浆均匀性、极片反弹、注液浸润和化成策略都有直接影响。",
        keywords=(
            "负极",
            "石墨",
            "硅碳",
            "硅氧",
            "硬碳",
            "锂金属",
            "人造石墨",
            "天然石墨",
            "负极材料",
            "anode",
            "graphite",
            "silicon carbon",
        ),
        related_process_slugs=("slurry", "coating", "calendering", "electrolyte-filling", "formation"),
        key_properties=("比容量", "体积膨胀", "首次效率", "倍率性能", "循环寿命"),
        process_impacts=("硅基材料膨胀要求更关注粘结体系和极片结构", "负极孔隙率影响注液浸润与锂离子传输", "SEI 稳定性影响化成参数和首圈损失"),
    ),
    Topic(
        slug="electrolyte",
        name="电解液",
        summary="围绕溶剂、锂盐、添加剂及其对浸润、SEI/CEI、温度窗口和安全性的影响。",
        description="电解液连接材料界面与工艺窗口，是注液、静置、化成和安全评估的关键变量。",
        keywords=(
            "电解液",
            "锂盐",
            "溶剂",
            "添加剂",
            "浸润",
            "SEI",
            "CEI",
            "六氟磷酸锂",
            "LiPF6",
            "electrolyte",
        ),
        related_process_slugs=("electrolyte-filling", "formation", "grading", "inspection"),
        key_properties=("浸润性", "离子电导率", "SEI/CEI 成膜", "温度窗口", "安全性"),
        process_impacts=("浸润速度影响注液量、静置时间和真空工艺", "添加剂体系影响化成电流、温度和截止条件", "高低温窗口影响分容和安全测试边界"),
    ),
    Topic(
        slug="separator",
        name="隔膜",
        summary="理解 PE/PP、陶瓷涂覆、湿法/干法隔膜的孔隙率、闭孔温度和机械强度。",
        description="隔膜承担离子通道和安全隔离功能，影响卷绕/叠片对齐、注液浸润、热安全和短路风险。",
        keywords=(
            "隔膜",
            "PE",
            "PP",
            "陶瓷涂覆",
            "湿法隔膜",
            "干法隔膜",
            "孔隙率",
            "闭孔",
            "热收缩",
            "separator",
        ),
        related_process_slugs=("winding-stacking", "assembly", "electrolyte-filling", "inspection"),
        key_properties=("孔隙率", "闭孔温度", "热收缩", "穿刺强度", "浸润性"),
        process_impacts=("厚度和强度影响卷绕张力、叠片对齐和破膜风险", "孔结构影响电解液浸润和倍率表现", "热收缩与闭孔行为影响安全测试结果"),
    ),
    Topic(
        slug="dry-electrode",
        name="干法电极",
        summary="以干混、粘结剂纤维化、干法成膜、集流体复合和辊压替代湿法制浆/涂布/烘干。",
        description="干法电极是跨制浆、涂布和辊压的工艺路线，目标是减少溶剂和烘干能耗，同时支撑厚电极与高载量设计。",
        keywords=(
            "干法电极",
            "干电极",
            "干法制备",
            "干混",
            "纤维化",
            "干法成膜",
            "厚电极",
            "高载量",
            "dry electrode",
            "dry coating",
        ),
        related_process_slugs=("slurry", "coating", "calendering"),
        key_properties=("少溶剂", "低能耗", "厚电极", "高载量", "工艺连续性"),
        process_impacts=("绕开传统湿法制浆和长距离烘干", "纤维化粘结剂决定膜强度和集流体附着力", "厚电极设计需要平衡传输阻抗、良率和辊压窗口"),
    ),
)


def get_topic(slug: str) -> Topic | None:
    return next((topic for topic in TOPICS if topic.slug == slug), None)


def topics_for_process(process_slug: str) -> list[Topic]:
    return [topic for topic in TOPICS if process_slug in topic.related_process_slugs]


def topic_query(db: Session, topic: Topic) -> Query[IntelligenceItem]:
    filters = []
    for keyword in topic.keywords:
        pattern = f"%{keyword}%"
        filters.extend(
            [
                IntelligenceItem.title.ilike(pattern),
                IntelligenceItem.summary.ilike(pattern),
                IntelligenceItem.content_excerpt.ilike(pattern),
                IntelligenceItem.tags.ilike(pattern),
                IntelligenceItem.category.ilike(pattern),
            ]
        )
    return db.query(IntelligenceItem).filter(
        IntelligenceItem.status == IntelligenceStatus.active,
        or_(*filters),
    )


def topic_latest_crawled_at(items_query: Query[IntelligenceItem]) -> datetime | None:
    item = items_query.order_by(IntelligenceItem.crawled_at.desc()).first()
    return item.crawled_at if item else None
