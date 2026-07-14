from django import template

from apps.ads.models import AdSenseConfig, Publicite

register = template.Library()


@register.simple_tag
def get_adsense():
    return AdSenseConfig.load()


@register.inclusion_tag("partials/ad_slot.html")
def ad_slot(emplacement, css_class=""):
    """
    Affiche une publicité pour un emplacement donné.
    1) Publicité maison active → image/lien ou code_html (+ impression).
    2) Sinon AdSense actif → bloc <ins> du slot correspondant.
    3) Sinon → rien.
    """
    pub = None
    for p in Publicite.objects.filter(emplacement=emplacement, actif=True).order_by("?"):
        if p.est_active():
            pub = p
            break

    adsense = AdSenseConfig.load()

    if pub:
        # Comptage d'impression (non bloquant).
        Publicite.objects.filter(pk=pub.pk).update(impressions=pub.impressions + 1)

    return {
        "pub": pub,
        "emplacement": emplacement,
        "css_class": css_class,
        "adsense": adsense,
        "adsense_slot": adsense.slot_for(emplacement) if adsense else "",
        "show_adsense": bool(adsense and adsense.actif and not pub and adsense.slot_for(emplacement)),
    }
