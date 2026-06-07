from django.shortcuts import render
from .models import Boutique


class BoutiqueBlockedMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # admin django reste accessible
        if request.path.startswith('/admin'):
            return self.get_response(request)

        # prendre boutique
        boutique = Boutique.objects.first()

        # si boutique bloquée
        if boutique and boutique.is_blocked:

            return render(request, 'boutique_blocked.html', {
                'boutique': boutique
            })

        response = self.get_response(request)

        return response