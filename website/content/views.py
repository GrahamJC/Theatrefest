from django.shortcuts import render, get_object_or_404
from django.views import View

from .models import Page


class PageView(View):

    def get(self, request, name):

        # Get page definition
        page = get_object_or_404(Page, name = name)

        # Display page
        context = {
            'page': page,
        }
        return render(request, "content/page.html", context)
