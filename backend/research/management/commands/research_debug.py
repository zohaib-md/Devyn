import json

from django.core.management.base import BaseCommand

from research.models import ResearchRun
from research.pipeline.plan import plan_queries
from research.pipeline.search import research
from research.pipeline.synthesize import synthesize
from research.pipeline.validate import validate


class Command(BaseCommand):
    help = "Debug the research pipeline for a topic: saves Items and prints a validated report."

    def add_arguments(self, parser):
        parser.add_argument("topic", type=str, help="Topic to research")

    def handle(self, *args, **options):
        topic = options["topic"]
        run = ResearchRun.objects.create(topic=topic, status="researching")
        self.stdout.write(f"Run {run.id} topic={topic!r}")
        queries = plan_queries(topic)
        run.queries = queries
        run.save(update_fields=["queries"])
        self.stdout.write(f"Queries: {queries}")
        items = research(run, queries)
        self.stdout.write(f"Saved {len(items)} items")
        report = synthesize(topic, items)
        validated = validate(report, items)
        run.report = validated
        run.status = "done"
        run.save(update_fields=["report", "status"])
        self.stdout.write(json.dumps(validated, indent=2, default=str))
