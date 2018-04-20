from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View
from django.http import JsonResponse

from program.models import Show, Performance

def get_performances(request):

    show = get_object_or_404(Show, pk = request.GET.get('show_id', 0))
    performances = []
    for performance in show.performances.all():
        performances.append({
            "id": performance.id,
            "date": performance.date,
            "time": performance.time,
            "tickets_available": performance.tickets_available,
        })
    data = {
        "performances": performances,
    }
    return JsonResponse(data)

