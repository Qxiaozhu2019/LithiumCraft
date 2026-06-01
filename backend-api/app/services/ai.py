from dataclasses import dataclass

from app.services.process_stages import PROCESS_STAGES


@dataclass(frozen=True)
class AIResult:
    summary: str
    tags: list[str]
    category: str
    importance_score: float


class AIAdapter:
    """第一期使用确定性 stub，后续可替换为真实模型供应商。"""

    def analyze(self, title: str, content: str) -> AIResult:
        text = f"{title} {content}"
        category = "行业快讯"
        matched_stages = [
            stage.name
            for stage in PROCESS_STAGES
            if any(keyword in text for keyword in stage.keywords)
        ]
        if matched_stages:
            category = "制造工艺"
        elif any(word in text for word in ["政策", "监管", "标准", "规范"]):
            category = "政策监管"
        elif any(word in text for word in ["扩产", "项目", "产能", "投产"]):
            category = "产能项目"
        elif any(word in text for word in ["设备", "涂布", "辊压", "化成", "分容"]):
            category = "设备工艺"
        elif any(word in text for word in ["专利", "论文", "研究"]):
            category = "专利论文"
        elif any(word in text for word in ["融资", "并购", "上市", "投资"]):
            category = "投融资"
        tags = [
            word
            for word in ["锂电", "电池", "正极", "负极", "储能", "固态电池", "设备", "材料"]
            if word in text
        ]
        tags.extend(matched_stages)
        if not tags:
            tags = ["锂电"]
        summary = content.strip().replace("\n", " ")[:240] or title
        score = 0.85 if any(word in text for word in ["重大", "突破", "百亿", "首次"]) else 0.5
        return AIResult(summary=summary, tags=tags[:6], category=category, importance_score=score)
