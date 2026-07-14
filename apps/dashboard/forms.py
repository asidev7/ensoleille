from django import forms

from apps.ads.models import AdSenseConfig, Publicite
from apps.articles.models import Article, Auteur, Categorie, Tag
from apps.core.models import ParametresSite

INPUT = "w-full rounded-lg border border-ensoleille-bordure px-3 py-2 focus:border-ensoleille-or focus:ring-1 focus:ring-ensoleille-or outline-none"
CHECK = "h-4 w-4 rounded border-ensoleille-bordure text-ensoleille-or focus:ring-ensoleille-or"


def _style(fields):
    for f in fields.values():
        if isinstance(f.widget, (forms.CheckboxInput,)):
            f.widget.attrs.setdefault("class", CHECK)
        elif isinstance(f.widget, forms.SelectMultiple):
            f.widget.attrs.setdefault("class", INPUT + " h-32")
        else:
            f.widget.attrs.setdefault("class", INPUT)


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        # « auteur » est attribué automatiquement à l'utilisateur connecté (voir la vue).
        fields = [
            "titre", "categorie", "tags", "image_couverture", "credit_image",
            "chapeau", "contenu", "date_publication", "statut",
            "a_la_une", "urgent", "epingle", "meta_description", "meta_image",
        ]
        widgets = {
            "chapeau": forms.Textarea(attrs={"rows": 3}),
            "contenu": forms.Textarea(attrs={"rows": 16, "id": "editeur-contenu"}),
            "date_publication": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "meta_description": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date_publication"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"]
        _style(self.fields)


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ["nom", "description", "couleur", "icone_svg", "ordre", "en_menu"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "icone_svg": forms.Textarea(attrs={"rows": 3}),
            "couleur": forms.TextInput(attrs={"type": "color"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self.fields)


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["nom"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self.fields)


class AuteurForm(forms.ModelForm):
    class Meta:
        model = Auteur
        fields = ["user", "nom", "role", "bio", "photo", "facebook", "twitter"]
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self.fields)


class PubliciteForm(forms.ModelForm):
    class Meta:
        model = Publicite
        fields = [
            "titre", "emplacement", "image", "code_html", "lien", "annonceur",
            "actif", "date_debut", "date_fin",
        ]
        widgets = {
            "code_html": forms.Textarea(attrs={"rows": 4}),
            "date_debut": forms.DateInput(attrs={"type": "date"}),
            "date_fin": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self.fields)


class AdSenseForm(forms.ModelForm):
    class Meta:
        model = AdSenseConfig
        fields = ["client_id", "actif", "auto_ads", "slot_header", "slot_in_article", "slot_sidebar"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self.fields)


class ParametresForm(forms.ModelForm):
    class Meta:
        model = ParametresSite
        fields = [
            "nom_site", "slogan", "description", "logo", "favicon", "email_contact",
            "telephone", "facebook", "tiktok", "youtube", "twitter", "whatsapp",
            "google_analytics_id",
        ]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self.fields)
