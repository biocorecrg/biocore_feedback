from django.urls import path
from biocore_feedback.views import submit_feedback

app_name = "biocore_feedback"

urlpatterns = [
    path("", submit_feedback, name="submit"),
]
