from django_q.tasks import async_task
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from research.models import ResearchRun
from .serializers import RunCreateSerializer


def _cited_ids(report: dict) -> set[int]:
    ids: set[int] = set()
    if not isinstance(report, dict):
        return ids
    for t in report.get("trends", []) or []:
        ids.update(t.get("source_ids", []) or [])
    for item in report.get("learn", []) or []:
        ids.update(item.get("source_ids", []) or [])
    for week in report.get("roadmap", []) or []:
        ids.update(week.get("resource_ids", []) or [])
    return {int(i) for i in ids if isinstance(i, int)}


class RunCreateView(APIView):
    def post(self, request):
        serializer = RunCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        run = ResearchRun.objects.create(topic=serializer.validated_data["topic"], status="queued")
        async_task("research.tasks.run_research", run.id)
        return Response({"id": run.id, "status": run.status}, status=status.HTTP_201_CREATED)


class RunDetailView(APIView):
    def get(self, request, run_id: int):
        try:
            run = ResearchRun.objects.get(id=run_id)
        except ResearchRun.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        cited = _cited_ids(run.report or {})
        sources: dict[str, dict] = {}
        if cited:
            for item in run.items.filter(id__in=cited):
                sources[str(item.id)] = {
                    "title": item.title,
                    "url": item.url,
                    "domain": item.domain,
                    "source": item.source,
                    "published_at": item.published_at.isoformat() if item.published_at else None,
                }
        return Response(
            {
                "id": run.id,
                "topic": run.topic,
                "status": run.status,
                "error": run.error or "",
                "report": run.report,
                "sources": sources,
                "created_at": run.created_at.isoformat() if run.created_at else None,
            }
        )
