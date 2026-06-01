from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.intelligence import IntelligenceItem
from app.schemas import TopicDetail, TopicRead
from app.services.topics import TOPICS, Topic, get_topic, topic_latest_crawled_at, topic_query

router = APIRouter()


def build_topic_read(db: Session, topic: Topic) -> TopicRead:
    query = topic_query(db, topic)
    return TopicRead(
        slug=topic.slug,
        name=topic.name,
        summary=topic.summary,
        description=topic.description,
        keywords=list(topic.keywords),
        related_process_slugs=list(topic.related_process_slugs),
        key_properties=list(topic.key_properties),
        process_impacts=list(topic.process_impacts),
        item_count=query.count(),
        latest_crawled_at=topic_latest_crawled_at(query),
    )


@router.get("", response_model=list[TopicRead])
def list_topics(db: Session = Depends(get_db)) -> list[TopicRead]:
    return [build_topic_read(db, topic) for topic in TOPICS]


@router.get("/{slug}", response_model=TopicDetail)
def get_topic_detail(
    slug: str,
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> TopicDetail:
    topic = get_topic(slug)
    if topic is None:
        raise HTTPException(status_code=404, detail="topic_not_found")

    query = topic_query(db, topic)
    items = query.order_by(IntelligenceItem.crawled_at.desc()).limit(page_size).all()
    return TopicDetail(
        **build_topic_read(db, topic).model_dump(),
        items=items,
        source_count=len({item.source_id for item in items if item.source_id is not None}),
    )
