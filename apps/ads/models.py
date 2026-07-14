from django.db import models
from django.utils import timezone

from apps.core.models import SingletonModel


class Publicite(models.Model):
    EMPLACEMENT = [
        ("header", "Bannière header"),
        ("sidebar", "Colonne latérale"),
        ("in_article", "Dans l'article"),
        ("footer", "Pied de page"),
        ("popup", "Pop-up / interstitiel"),
        ("between", "Entre les articles (flux)"),
    ]
    titre = models.CharField(max_length=120)
    image = models.ImageField(upload_to="pub/", blank=True)
    code_html = models.TextField(blank=True, help_text="Si bannière HTML/JS au lieu d'une image")
    lien = models.URLField(blank=True)
    emplacement = models.CharField(max_length=20, choices=EMPLACEMENT)
    annonceur = models.CharField(max_length=120, blank=True)
    actif = models.BooleanField(default=True)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    impressions = models.PositiveIntegerField(default=0)
    clics = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["emplacement", "-created_at"]
        verbose_name = "Publicité"

    def __str__(self):
        return f"{self.titre} ({self.get_emplacement_display()})"

    def est_active(self):
        if not self.actif:
            return False
        today = timezone.localdate()
        if self.date_debut and today < self.date_debut:
            return False
        if self.date_fin and today > self.date_fin:
            return False
        return True

    @property
    def ctr(self):
        return round(self.clics / self.impressions * 100, 2) if self.impressions else 0


class AdSenseConfig(SingletonModel):
    client_id = models.CharField(max_length=40, blank=True, help_text="ca-pub-XXXXXXXXXXXX")
    actif = models.BooleanField(default=False)
    slot_header = models.CharField(max_length=20, blank=True)
    slot_in_article = models.CharField(max_length=20, blank=True)
    slot_sidebar = models.CharField(max_length=20, blank=True)
    auto_ads = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Configuration AdSense"
        verbose_name_plural = "Configuration AdSense"

    def __str__(self):
        return f"AdSense ({'actif' if self.actif else 'inactif'})"

    def slot_for(self, emplacement):
        return {
            "header": self.slot_header,
            "in_article": self.slot_in_article,
            "sidebar": self.slot_sidebar,
        }.get(emplacement, "")
