from django.utils import timezone

from research.models import ResearchRun
from research.pipeline.plan import plan_queries
from research.pipeline.search import research
from research.pipeline.synthesize import synthesize
from research.pipeline.validate import validate


def set_status(run: ResearchRun, status: str) -> None:
    run.status = status
    run.updated_at = timezone.now()
    run.save(update_fields=["status", "queries", "report", "error", "updated_at"])


def run_research(run_id: int) -> None:
    run = ResearchRun.objects.get(id=run_id)
    try:
        set_status(run, "planning")
        run.queries = plan_queries(run.topic)

        set_status(run, "researching")
        items = research(run, run.queries)

        set_status(run, "writing")
        report = synthesize(run.topic, items)

        run.report = validate(report, items)
        set_status(run, "done")
    except Exception as e:
        run.error = str(e)
        set_status(run, "failed")
