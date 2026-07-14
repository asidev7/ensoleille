from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.ads.models import AdSenseConfig

from .models import AbonneNewsletter, MessageContact, ParametresSite


def a_propos(request):
    return render(request, "pages/a_propos.html")


def mentions_legales(request):
    return render(request, "pages/mentions_legales.html")


def contact(request):
    if request.method == "POST":
        if request.POST.get("site"):  # honeypot
            return redirect("core:contact")
        nom = (request.POST.get("nom") or "").strip()
        email = (request.POST.get("email") or "").strip()
        message = (request.POST.get("message") or "").strip()
        if nom and email and message:
            MessageContact.objects.create(
                nom=nom[:120],
                email=email,
                sujet=(request.POST.get("sujet") or "")[:160],
                message=message,
            )
            messages.success(request, "Merci, votre message a bien été envoyé.")
            return redirect("core:contact")
        messages.error(request, "Tous les champs requis ne sont pas remplis.")
    return render(request, "pages/contact.html")


@require_POST
def newsletter(request):
    email = (request.POST.get("email") or "").strip()
    if email:
        AbonneNewsletter.objects.get_or_create(email=email)
        messages.success(request, "Inscription à la newsletter confirmée. Merci !")
    else:
        messages.error(request, "Adresse email invalide.")
    return redirect(request.META.get("HTTP_REFERER", "/"))


def newsletter_desinscription(request, email):
    AbonneNewsletter.objects.filter(email=email).update(actif=False)
    messages.info(request, "Vous êtes désinscrit de la newsletter.")
    return redirect("articles:home")


# --- Fichiers SEO servis dynamiquement ---

def robots_txt(request):
    lignes = [
        "User-agent: *",
        "Disallow: /dashboard/",
        "Disallow: /admin/",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lignes), content_type="text/plain")


def ads_txt(request):
    cfg = AdSenseConfig.load()
    if cfg.actif and cfg.client_id:
        pub = cfg.client_id.replace("ca-", "")
        contenu = f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n"
    else:
        contenu = "# Aucune régie programmatique configurée.\n"
    return HttpResponse(contenu, content_type="text/plain")
