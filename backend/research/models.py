from django.db import models


class ResearchRun(models.Model):
    STATUS_CHOICES = [
        ("queued", "queued"),
        ("planning", "planning"),
        ("researching", "researching"),
        ("writing", "writing"),
        ("done", "done"),
        ("failed", "failed"),
    ]

    topic = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")
    queries = models.JSONField(default=list)
    report = models.JSONField(null=True, blank=True)
    error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Run {self.id}: {self.topic} ({self.status})"


class Item(models.Model):
    SOURCE_CHOICES = [
        ("web", "web"),
        ("hn", "hn"),
        ("github", "github"),
    ]

    run = models.ForeignKey(ResearchRun, on_delete=models.CASCADE, related_name="items")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    url = models.URLField(max_length=1000)
    title = models.CharField(max_length=500)
    snippet = models.TextField()
    domain = models.CharField(max_length=200)
    published_at = models.DateTimeField(null=True, blank=True)
    meta = models.JSONField(default=dict)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["run", "url"], name="unique_run_url"),
        ]

    def __str__(self) -> str:
        return f"[{self.source}] {self.title[:80]}"
