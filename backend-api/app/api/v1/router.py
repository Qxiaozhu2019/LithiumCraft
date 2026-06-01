from fastapi import APIRouter

from app.api.v1 import auth, categories, crawl_tasks, daily_briefs, intelligence, processes, settings, sources, topics

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])
api_router.include_router(processes.router, prefix="/processes", tags=["processes"])
api_router.include_router(topics.router, prefix="/topics", tags=["topics"])
api_router.include_router(daily_briefs.router, prefix="/daily-briefs", tags=["daily-briefs"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(crawl_tasks.router, prefix="/crawl-tasks", tags=["crawl-tasks"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
