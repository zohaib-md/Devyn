from django.urls import path

from .views import RunCreateView, RunDetailView

urlpatterns = [
    path("runs", RunCreateView.as_view(), name="run-create"),
    path("runs/<int:run_id>", RunDetailView.as_view(), name="run-detail"),
]
