from django.shortcuts import render
from django.views.generic import TemplateView
from .settings import FIREBASE_CONFIG


class Index(TemplateView):
    template_name = "firebase/auth/index.html"
    extra_context = {
        'FIREBASE_CONFIG': FIREBASE_CONFIG['FIREBASE_WEBAPP_CONFIG'],
    }


def passthought(request, page):
    context = {
        'FIREBASE_CONFIG': FIREBASE_CONFIG['FIREBASE_WEBAPP_CONFIG'],
    }
    return render(request, f'firebase/auth/{page}', context=context)
