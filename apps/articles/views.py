from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Article, Auteur, Categorie, Tag


def _articles_publies():
    return Article.objects.publies().select_related("categorie", "auteur")


def home(request):
    publies = _articles_publies()
    une = publies.filter(a_la_une=True).first()
    secondaires = list(publies.filter(a_la_une=True).exclude(pk=une.pk if une else 0)[:4])
    if not une:
        # Repli : article le plus récent en vedette
        recents = list(publies[:5])
        une = recents[0] if recents else None
        secondaires = recents[1:5]

    derniers = publies.exclude(pk=une.pk if une else 0)[:12]
    urgents = publies.filter(urgent=True)[:8]
    plus_lus = publies.order_by("-nombre_vues")[:6]

    # Blocs par rubrique (3 premières rubriques du menu avec articles)
    blocs = []
    for cat in Categorie.objects.filter(en_menu=True)[:5]:
        arts = list(cat.articles_publies.select_related("auteur")[:4])
        if arts:
            blocs.append({"categorie": cat, "articles": arts})

    return render(request, "pages/home.html", {
        "une": une,
        "secondaires": secondaires,
        "derniers": derniers,
        "urgents": urgents,
        "plus_lus": plus_lus,
        "blocs": blocs,
    })


def _compter_vue(request, article):
    """+1 vue par session pour éviter le spam de rafraîchissement."""
    vues = request.session.get("articles_vus", [])
    if article.pk not in vues:
        Article.objects.filter(pk=article.pk).update(nombre_vues=article.nombre_vues + 1)
        vues.append(article.pk)
        request.session["articles_vus"] = vues


def detail(request, slug):
    article = get_object_or_404(
        Article.objects.select_related("categorie", "auteur").prefetch_related("tags"),
        slug=slug,
    )
    if not article.est_publie and not request.user.is_staff:
        from django.http import Http404
        raise Http404("Article non publié")

    _compter_vue(request, article)
    article.refresh_from_db(fields=["nombre_vues"])

    commentaires = (
        article.commentaires.filter(approuve=True, parent__isnull=True)
        .prefetch_related("reponses")
    )
    nb_commentaires = article.commentaires.filter(approuve=True).count()

    return render(request, "pages/article_detail.html", {
        "article": article,
        "articles_lies": article.articles_lies(),
        "commentaires": commentaires,
        "nb_commentaires": nb_commentaires,
        "plus_lus": _articles_publies().order_by("-nombre_vues")[:6],
    })


def rubrique(request, slug):
    categorie = get_object_or_404(Categorie, slug=slug)
    qs = categorie.articles_publies.select_related("auteur").order_by("-epingle", "-date_publication")
    page = Paginator(qs, 9).get_page(request.GET.get("page"))
    return render(request, "pages/rubrique.html", {
        "categorie": categorie,
        "page_obj": page,
        "plus_lus": _articles_publies().order_by("-nombre_vues")[:6],
    })


def auteur(request, pk):
    auteur = get_object_or_404(Auteur, pk=pk)
    qs = auteur.articles_publies.select_related("categorie")
    page = Paginator(qs, 9).get_page(request.GET.get("page"))
    return render(request, "pages/auteur.html", {"auteur": auteur, "page_obj": page})


def tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    qs = _articles_publies().filter(tags=tag)
    page = Paginator(qs, 9).get_page(request.GET.get("page"))
    return render(request, "pages/tag.html", {"tag": tag, "page_obj": page})


def recherche(request):
    q = (request.GET.get("q") or "").strip()
    resultats = Article.objects.none()
    if q:
        base = _articles_publies()
        if getattr(settings, "POSTGRES", False):
            from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
            vector = SearchVector("titre", weight="A") + SearchVector("chapeau", weight="B") + SearchVector("contenu", weight="C")
            query = SearchQuery(q, config="french")
            resultats = (
                base.annotate(rank=SearchRank(vector, query))
                .filter(rank__gte=0.01)
                .order_by("-rank")
            )
        else:
            resultats = base.filter(
                Q(titre__icontains=q) | Q(chapeau__icontains=q) | Q(contenu__icontains=q)
            )
    page = Paginator(resultats, 10).get_page(request.GET.get("page"))
    return render(request, "pages/recherche.html", {"q": q, "page_obj": page, "total": resultats.count() if q else 0})
