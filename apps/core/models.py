from django.core.cache import cache
from django.db import models


class SingletonModel(models.Model):
    """Base : une seule ligne en base (pk=1)."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete(self.__class__.__name__)

    @classmethod
    def load(cls):
        obj = cache.get(cls.__name__)
        if obj is None:
            obj, _ = cls.objects.get_or_create(pk=1)
            cache.set(cls.__name__, obj, 300)
        return obj


class ParametresSite(SingletonModel):
    nom_site = models.CharField(max_length=120, default="Rédaction Ensoleillé — La Presse")
    slogan = models.CharField(max_length=160, default="Ensoleillé, lumière sur l'obscurité !")
    description = models.TextField(blank=True, default="Lumière sur l'obscurité : l'information vérifiée du Bénin et de l'Afrique de l'Ouest.")
    logo = models.ImageField(upload_to="config/", blank=True)
    favicon = models.ImageField(upload_to="config/", blank=True)
    email_contact = models.EmailField(blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    facebook = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    google_analytics_id = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"

    def __str__(self):
        return self.nom_site


class AbonneNewsletter(models.Model):
    email = models.EmailField(unique=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Abonné newsletter"
        verbose_name_plural = "Abonnés newsletter"

    def __str__(self):
        return self.email


class MessageContact(models.Model):
    nom = models.CharField(max_length=120)
    email = models.EmailField()
    sujet = models.CharField(max_length=160, blank=True)
    message = models.TextField()
    traite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"

    def __str__(self):
        return f"{self.nom} — {self.sujet or 'Sans sujet'}"
