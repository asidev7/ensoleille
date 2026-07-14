from apps.articles.models import Categorie
from apps.core.models import ParametresSite


def parametres_site(request):
    """Expose les paramètres du site + le menu des rubriques à tous les templates."""
    return {
        "parametres": ParametresSite.load(),
        "menu_categories": Categorie.objects.filter(en_menu=True),
    }
