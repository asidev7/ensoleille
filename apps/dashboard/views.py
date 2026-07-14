import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.ads.models import AdSenseConfig, Publicite
from apps.articles.models import Article, Auteur, Categorie, Tag
from apps.comments.models import Commentaire
from apps.core.models import AbonneNewsletter, ParametresSite

from .forms import (
    AdSenseForm,
    ArticleForm,
    AuteurForm,
    CategorieForm,
    ParametresForm,
    PubliciteForm,
    TagForm,
)


@login_required
def home(request):
    articles = Article.objects.all()
    publies = articles.filter(statut="publie")
    # 7 derniers jours de vues approximées par articles publiés récemment
    labels, data = [], []
    for i in range(6, -1, -1):
        jour = timezone.localdate() - timezone.timedelta(days=i)
        labels.append(jour.strftime("%d/%m"))
        data.append(
            publies.filter(date_publication__date=jour).aggregate(v=Sum("nombre_vues"))["v"] or 0
        )
    ctx = {
        "nb_publies": publies.count(),
        "nb_brouillons": articles.filter(statut="brouillon").count(),
        "total_vues": publies.aggregate(v=Sum("nombre_vues"))["v"] or 0,
        "commentaires_attente": Commentaire.objects.filter(approuve=False).count(),
        "top_articles": publies.order_by("-nombre_vues")[:5],
        "derniers_commentaires": Commentaire.objects.select_related("article").order_by("-created_at")[:5],
        "chart_labels": labels,
        "chart_data": data,
        "nb_pubs": Publicite.objects.filter(actif=True).count(),
    }
    return render(request, "dashboard/home.html", ctx)


# ---------------------------------------------------------------- Articles
@login_required
def articles_liste(request):
    qs = Article.objects.select_related("categorie", "auteur").all()
    q = request.GET.get("q", "").strip()
    statut = request.GET.get("statut", "")
    cat = request.GET.get("categorie", "")
    if q:
        qs = qs.filter(Q(titre__icontains=q) | Q(chapeau__icontains=q))
    if statut:
        qs = qs.filter(statut=statut)
    if cat:
        qs = qs.filter(categorie_id=cat)
    return render(request, "dashboard/articles_liste.html", {
        "articles": qs,
        "q": q,
        "statut": statut,
        "cat": cat,
        "categories": Categorie.objects.all(),
        "statuts": Article.STATUT,
    })


def auteur_pour(user):
    """Renvoie (ou crée) le profil Auteur lié à l'utilisateur connecté."""
    auteur = getattr(user, "auteur", None)
    if auteur is None:
        nom = user.get_full_name().strip() or user.get_username()
        auteur = Auteur.objects.create(user=user, nom=nom, role="Rédacteur")
    return auteur


@login_required
def article_form(request, pk=None):
    article = get_object_or_404(Article, pk=pk) if pk else None
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            obj = form.save(commit=False)
            # Auteur = l'utilisateur connecté qui rédige (uniquement à la création).
            if obj.auteur_id is None:
                obj.auteur = auteur_pour(request.user)
            obj.save()
            form.save_m2m()
            messages.success(request, f"Article « {obj.titre} » enregistré.")
            return redirect("dashboard:articles")
        messages.error(request, "Corrigez les erreurs du formulaire.")
    else:
        form = ArticleForm(instance=article)
    return render(request, "dashboard/article_form.html", {"form": form, "article": article})


@login_required
def article_supprimer(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        article.delete()
        messages.success(request, "Article supprimé.")
        return redirect("dashboard:articles")
    return render(request, "dashboard/confirmer_suppression.html", {
        "objet": article.titre, "retour": "dashboard:articles",
    })


# ---------------------------------------------------------------- Commentaires
@login_required
def commentaires(request):
    statut = request.GET.get("statut", "attente")
    qs = Commentaire.objects.select_related("article").order_by("-created_at")
    if statut == "attente":
        qs = qs.filter(approuve=False)
    elif statut == "approuves":
        qs = qs.filter(approuve=True)
    return render(request, "dashboard/commentaires.html", {"commentaires": qs, "statut": statut})


@login_required
def commentaire_action(request, pk, action):
    c = get_object_or_404(Commentaire, pk=pk)
    if action == "approuver":
        c.approuve = True
        c.save()
        messages.success(request, "Commentaire approuvé.")
    elif action == "rejeter":
        c.delete()
        messages.success(request, "Commentaire rejeté.")
    return redirect(request.META.get("HTTP_REFERER", "dashboard:commentaires"))


# ---------------------------------------------------------------- Publicités
@login_required
def publicites(request):
    return render(request, "dashboard/publicites.html", {
        "publicites": Publicite.objects.all(),
        "adsense": AdSenseConfig.load(),
    })


@login_required
def publicite_form(request, pk=None):
    pub = get_object_or_404(Publicite, pk=pk) if pk else None
    if request.method == "POST":
        form = PubliciteForm(request.POST, request.FILES, instance=pub)
        if form.is_valid():
            form.save()
            messages.success(request, "Publicité enregistrée.")
            return redirect("dashboard:publicites")
    else:
        form = PubliciteForm(instance=pub)
    return render(request, "dashboard/publicite_form.html", {"form": form, "pub": pub})


@login_required
def publicite_supprimer(request, pk):
    pub = get_object_or_404(Publicite, pk=pk)
    if request.method == "POST":
        pub.delete()
        messages.success(request, "Publicité supprimée.")
        return redirect("dashboard:publicites")
    return render(request, "dashboard/confirmer_suppression.html", {
        "objet": pub.titre, "retour": "dashboard:publicites",
    })


@login_required
def adsense_config(request):
    cfg = AdSenseConfig.load()
    if request.method == "POST":
        form = AdSenseForm(request.POST, instance=cfg)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuration AdSense enregistrée.")
            return redirect("dashboard:publicites")
    else:
        form = AdSenseForm(instance=cfg)
    return render(request, "dashboard/adsense_form.html", {"form": form})


# ---------------------------------------------------------------- Rubriques & tags
@login_required
def rubriques(request):
    return render(request, "dashboard/rubriques.html", {
        "categories": Categorie.objects.annotate(n=Count("articles")),
        "tags": Tag.objects.annotate(n=Count("articles")),
    })


@login_required
def rubrique_form(request, pk=None):
    cat = get_object_or_404(Categorie, pk=pk) if pk else None
    if request.method == "POST":
        form = CategorieForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, "Rubrique enregistrée.")
            return redirect("dashboard:rubriques")
    else:
        form = CategorieForm(instance=cat)
    return render(request, "dashboard/rubrique_form.html", {"form": form, "cat": cat})


@login_required
def tag_creer(request):
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tag créé.")
    return redirect("dashboard:rubriques")


# ---------------------------------------------------------------- Auteurs
@login_required
def auteurs(request):
    return render(request, "dashboard/auteurs.html", {
        "auteurs": Auteur.objects.annotate(n=Count("articles")),
    })


@login_required
def auteur_form(request, pk=None):
    auteur = get_object_or_404(Auteur, pk=pk) if pk else None
    if request.method == "POST":
        form = AuteurForm(request.POST, request.FILES, instance=auteur)
        if form.is_valid():
            form.save()
            messages.success(request, "Auteur enregistré.")
            return redirect("dashboard:auteurs")
    else:
        form = AuteurForm(instance=auteur)
    return render(request, "dashboard/auteur_form.html", {"form": form, "auteur": auteur})


# ---------------------------------------------------------------- Newsletter
@login_required
def newsletter(request):
    return render(request, "dashboard/newsletter.html", {
        "abonnes": AbonneNewsletter.objects.all(),
    })


@login_required
def newsletter_export(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=abonnes_newsletter.csv"
    writer = csv.writer(response)
    writer.writerow(["email", "actif", "inscription"])
    for a in AbonneNewsletter.objects.all():
        writer.writerow([a.email, a.actif, a.created_at.strftime("%Y-%m-%d %H:%M")])
    return response


# ---------------------------------------------------------------- Paramètres
@login_required
def parametres(request):
    obj = ParametresSite.load()
    if request.method == "POST":
        form = ParametresForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Paramètres du site enregistrés.")
            return redirect("dashboard:parametres")
    else:
        form = ParametresForm(instance=obj)
    return render(request, "dashboard/parametres.html", {"form": form})
