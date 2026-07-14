import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def urgents_pour_ticker(limite=8):
    from apps.articles.models import Article
    return list(Article.objects.urgents()[:limite])


@register.simple_tag
def split_apres_paragraphe(html, n=3):
    """
    Découpe un corps HTML après le n-ième </p> pour permettre l'insertion
    d'une publicité « in-article ». Retourne un dict {avant, apres}.
    """
    html = html or ""
    paragraphes = [m.end() for m in re.finditer(r"</p>", html, flags=re.IGNORECASE)]
    if len(paragraphes) > n:
        coupe = paragraphes[n - 1]
        return {"avant": mark_safe(html[:coupe]), "apres": mark_safe(html[coupe:])}
    return {"avant": mark_safe(html), "apres": mark_safe("")}
