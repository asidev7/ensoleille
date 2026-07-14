from django.shortcuts import render


def erreur_404(request, exception):
    return render(request, "pages/404.html", status=404)


def erreur_500(request):
    return render(request, "pages/500.html", status=500)
