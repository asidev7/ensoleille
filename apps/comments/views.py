from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.articles.models import Article

from .models import Commentaire


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR")


@require_POST
def poster(request, slug):
    article = get_object_or_404(Article, slug=slug)

    # Honeypot anti-spam : champ « site » invisible doit rester vide.
    if request.POST.get("site"):
        return redirect(article.get_absolute_url())

    nom = (request.POST.get("nom") or "").strip()
    contenu = (request.POST.get("contenu") or "").strip()
    email = (request.POST.get("email") or "").strip()
    parent_id = request.POST.get("parent")

    if not nom or not contenu:
        messages.error(request, "Merci d'indiquer votre nom et votre commentaire.")
        return redirect(article.get_absolute_url() + "#commentaires")

    # Throttling : 1 commentaire / 30 s par IP.
    ip = _client_ip(request)
    recent = Commentaire.objects.filter(
        ip=ip, created_at__gte=timezone.now() - timezone.timedelta(seconds=30)
    ).exists()
    if recent:
        messages.error(request, "Vous commentez trop vite. Patientez un instant.")
        return redirect(article.get_absolute_url() + "#commentaires")

    parent = None
    if parent_id:
        parent = Commentaire.objects.filter(pk=parent_id, article=article).first()

    Commentaire.objects.create(
        article=article,
        nom=nom[:80],
        email=email,
        contenu=contenu,
        parent=parent,
        ip=ip,
        approuve=False,
    )
    messages.success(request, "Merci ! Votre commentaire sera publié après modération.")
    return redirect(article.get_absolute_url() + "#commentaires")
