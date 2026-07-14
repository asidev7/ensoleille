import re

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import Truncator, slugify


def unique_slugify(instance, value, slug_field="slug", max_length=240):
    base = slugify(value)[:max_length] or "article"
    slug = base
    Model = instance.__class__
    n = 2
    qs = Model.objects.all()
    if instance.pk:
        qs = qs.exclude(pk=instance.pk)
    while qs.filter(**{slug_field: slug}).exists():
        suffix = f"-{n}"
        slug = base[: max_length - len(suffix)] + suffix
        n += 1
    return slug


class Categorie(models.Model):
    nom = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    description = models.TextField(blank=True)
    couleur = models.CharField(max_length=7, default="#F5A623")
    icone_svg = models.TextField(blank=True)
    ordre = models.PositiveIntegerField(default=0)
    en_menu = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["ordre", "nom"]
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.nom, max_length=90)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("articles:rubrique", args=[self.slug])

    @property
    def articles_publies(self):
        return self.articles.filter(statut="publie", date_publication__lte=timezone.now())


class Tag(models.Model):
    nom = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.nom, max_length=70)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("articles:tag", args=[self.slug])


class Auteur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="auteur")
    nom = models.CharField(max_length=120)
    role = models.CharField(max_length=80, default="Rédacteur")
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="auteurs/", blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "Auteur"

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse("articles:auteur", args=[self.pk])

    @property
    def articles_publies(self):
        return self.articles.filter(statut="publie", date_publication__lte=timezone.now())


class ArticleQuerySet(models.QuerySet):
    def publies(self):
        return self.filter(statut="publie", date_publication__lte=timezone.now())

    def a_la_une(self):
        return self.publies().filter(a_la_une=True)

    def urgents(self):
        return self.publies().filter(urgent=True)


class Article(models.Model):
    STATUT = [
        ("brouillon", "Brouillon"),
        ("publie", "Publié"),
        ("archive", "Archivé"),
    ]

    # Couverture & en-tête
    image_couverture = models.ImageField(upload_to="couvertures/%Y/%m/")
    credit_image = models.CharField(max_length=160, blank=True)
    titre = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    chapeau = models.TextField(help_text="Le chapô : 1 à 3 phrases d'accroche")

    # Corps riche (HTML : <p>, <strong>, <em>, <blockquote>, listes…)
    contenu = models.TextField(help_text="Contenu riche : gras, italique, paragraphes, citations…")

    # Classement
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name="articles")
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")
    auteur = models.ForeignKey(Auteur, on_delete=models.SET_NULL, null=True, blank=True, related_name="articles")

    # Métadonnées éditoriales
    date_publication = models.DateTimeField(default=timezone.now)
    statut = models.CharField(max_length=12, choices=STATUT, default="brouillon")
    a_la_une = models.BooleanField(default=False)
    urgent = models.BooleanField(default=False)
    epingle = models.BooleanField(default=False)

    # Engagement
    nombre_vues = models.PositiveIntegerField(default=0)
    temps_lecture = models.PositiveSmallIntegerField(default=0, help_text="minutes, auto-calculé")

    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    meta_image = models.ImageField(upload_to="og/", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ArticleQuerySet.as_manager()

    class Meta:
        ordering = ["-date_publication"]
        indexes = [models.Index(fields=["-date_publication", "statut"])]
        verbose_name = "Article"

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.titre, max_length=240)
        # Temps de lecture ≈ 200 mots/min
        texte = strip_tags(self.contenu or "")
        nb_mots = len(re.findall(r"\w+", texte))
        self.temps_lecture = max(1, round(nb_mots / 200)) if nb_mots else 1
        # Meta description auto depuis le chapô
        if not self.meta_description:
            self.meta_description = Truncator(strip_tags(self.chapeau)).chars(157)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("articles:detail", args=[self.slug])

    @property
    def og_image(self):
        return self.meta_image or self.image_couverture

    @property
    def est_publie(self):
        return self.statut == "publie" and self.date_publication <= timezone.now()

    @property
    def commentaires_approuves(self):
        return self.commentaires.filter(approuve=True, parent__isnull=True)

    def articles_lies(self, limite=4):
        return (
            Article.objects.publies()
            .filter(categorie=self.categorie)
            .exclude(pk=self.pk)[:limite]
        )
