from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Query, Session

from app.models.intelligence import IntelligenceItem, IntelligenceStatus


@dataclass(frozen=True)
class ProcessStage:
    slug: str
    name: str
    description: str
    keywords: tuple[str, ...]
    diagram_steps: tuple[str, ...]


PROCESS_STAGES: tuple[ProcessStage, ...] = (
    ProcessStage("slurry", "制浆", "活性物质、导电剂、粘结剂与溶剂混合分散，形成稳定浆料。", ("制浆", "匀浆", "浆料", "分散", "粘度"), ("投料", "混合", "分散", "脱泡")),
    ProcessStage("coating", "涂布", "将浆料均匀涂覆在集流体上，并通过干燥控制面密度与一致性。", ("涂布", "涂覆", "极片", "干燥", "面密度", "厚度"), ("供料", "涂覆", "烘干", "收卷")),
    ProcessStage("calendering", "辊压", "通过辊压控制极片压实密度、孔隙率、厚度和反弹。", ("辊压", "压实", "压实密度", "孔隙率", "反弹"), ("预热", "辊压", "测厚", "复卷")),
    ProcessStage("slitting", "分切", "将辊压后的极片按规格分切，控制毛刺、粉尘与边缘质量。", ("分切", "模切", "毛刺", "粉尘", "极耳"), ("放卷", "切割", "除尘", "收卷")),
    ProcessStage("winding-stacking", "卷绕/叠片", "将正负极片与隔膜按结构装配成电芯芯包。", ("卷绕", "叠片", "隔膜", "芯包", "对齐度"), ("送料", "对齐", "成型", "贴胶")),
    ProcessStage("assembly", "装配", "完成入壳、焊接、封装等电芯结构装配步骤。", ("装配", "入壳", "焊接", "封装", "顶盖"), ("入壳", "焊接", "封装", "检漏")),
    ProcessStage("electrolyte-filling", "注液", "向电芯注入电解液并完成浸润，影响界面和循环表现。", ("注液", "电解液", "浸润", "静置", "真空"), ("抽真空", "注液", "静置", "封口")),
    ProcessStage("formation", "化成", "通过首次充放电形成稳定 SEI/CEI 界面。", ("化成", "SEI", "首次充电", "充放电", "温控"), ("上柜", "充放电", "温控", "静置")),
    ProcessStage("grading", "分容", "按容量、内阻、电压等指标对电芯进行分档。", ("分容", "容量", "内阻", "分档", "OCV"), ("测试", "容量计算", "分档", "入库")),
    ProcessStage("inspection", "检测", "通过外观、尺寸、电性能和安全检测筛选异常电芯。", ("检测", "测试", "外观", "尺寸", "缺陷", "X-ray", "安全"), ("外观", "尺寸", "电性能", "安全")),
)


def get_process_stage(slug: str) -> ProcessStage | None:
    return next((stage for stage in PROCESS_STAGES if stage.slug == slug), None)


def process_stage_query(db: Session, stage: ProcessStage) -> Query[IntelligenceItem]:
    filters = []
    for keyword in stage.keywords:
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


def latest_crawled_at(items_query: Query[IntelligenceItem]) -> datetime | None:
    item = items_query.order_by(IntelligenceItem.crawled_at.desc()).first()
    return item.crawled_at if item else None


def match_process_stages(title: str, content: str = "", tags: str = "") -> list[ProcessStage]:
    text = f"{title} {content} {tags}"
    return [stage for stage in PROCESS_STAGES if any(keyword in text for keyword in stage.keywords)]


def is_process_related(title: str, content: str = "", tags: str = "") -> bool:
    text = f"{title} {content} {tags}"
    general_terms = ("锂电", "锂离子电池", "电池", "电芯", "极片", "正极", "负极", "隔膜", "电解液")
    return bool(match_process_stages(title, content, tags)) and any(term in text for term in general_terms)
