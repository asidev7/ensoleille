from django.db import models

from apps.articles.models import Article


class Commentaire(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="commentaires")
    nom = models.CharField(max_length=80)
    email = models.EmailField(blank=True)
    contenu = models.TextField()
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="reponses"
    )
    approuve = models.BooleanField(default=False)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Commentaire"

    def __str__(self):
        return f"{self.nom} sur « {self.article.titre} »"

    @property
    def reponses_approuvees(self):
        return self.reponses.filter(approuve=True)
