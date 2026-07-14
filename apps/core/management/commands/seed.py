import io
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.ads.models import AdSenseConfig, Publicite
from apps.articles.models import Article, Auteur, Categorie, Tag
from apps.core.models import ParametresSite

RUBRIQUES = [
    ("Politique", "#F5A623", "Vie politique nationale et institutions."),
    ("Société", "#FF8C00", "Faits de société, éducation, santé."),
    ("Économie", "#FFC107", "Économie, finances et entreprises de l'UEMOA."),
    ("Culture", "#E0A100", "Arts, musique et patrimoine."),
    ("Sport", "#FFB300", "Football, championnats et exploits."),
    ("International", "#D98E00", "Afrique de l'Ouest et monde."),
    ("Investigation", "#C97E00", "Enquêtes et révélations."),
    ("Faits divers", "#B5740F", "Sécurité, justice et incidents."),
    ("Tribune", "#FFD27A", "Opinions et points de vue."),
]

ARTICLES = [
    {
        "titre": "Cotonou : le gouvernement dévoile un plan d'éclairage solaire pour 12 communes",
        "rub": "Société",
        "chapeau": "Le ministère de l'Énergie a présenté ce vendredi un programme d'installation de lampadaires solaires destiné à sécuriser les artères de douze communes du sud du pays.",
        "une": True, "urgent": True,
    },
    {
        "titre": "Économie : la croissance du Bénin attendue à 6,2 % cette année selon la BCEAO",
        "rub": "Économie",
        "chapeau": "Portée par les services et l'agro-industrie, l'économie béninoise resterait l'une des plus dynamiques de la zone UEMOA, d'après les dernières projections.",
        "une": True,
    },
    {
        "titre": "Football : les Guépards arrachent le nul face au Sénégal en éliminatoires",
        "rub": "Sport",
        "chapeau": "Dans un stade de l'Amitié plein à craquer, la sélection nationale a tenu tête aux champions d'Afrique au terme d'un match intense.",
        "une": False, "urgent": True,
    },
    {
        "titre": "Investigation : ce que révèlent les marchés publics de la dernière décennie",
        "rub": "Investigation",
        "chapeau": "Notre rédaction a épluché des centaines de contrats pour comprendre les circuits d'attribution des grands chantiers publics.",
        "une": False,
    },
    {
        "titre": "Culture : le festival des arts d'Abomey célèbre la mémoire des rois",
        "rub": "Culture",
        "chapeau": "Pendant trois jours, danseurs, conteurs et artisans ont fait revivre l'histoire du royaume du Danxomè devant un public nombreux.",
        "une": False,
    },
]

CORPS = """<p>La cérémonie de présentation s'est tenue en présence de plusieurs membres du gouvernement et de représentants des collectivités locales. Le projet, financé à hauteur de plusieurs milliards de francs CFA, vise à répondre à une demande pressante des populations.</p>
<p>« Nous voulons apporter la lumière là où régnait l'obscurité », a déclaré le porte-parole du programme, reprenant un slogan désormais familier. Les premières installations devraient débuter dès le mois prochain.</p>
<p>Les autorités locales saluent une initiative attendue de longue date. Selon elles, l'éclairage public contribue directement à la réduction de l'insécurité nocturne et au dynamisme des activités commerciales.</p>
<blockquote>« C'est un changement concret pour nos quartiers », confie un habitant rencontré sur place.</blockquote>
<p>Sur le plan technique, les équipements retenus fonctionnent de manière autonome grâce à des panneaux photovoltaïques et des batteries de stockage, sans raccordement au réseau électrique national.</p>
<p>Le calendrier prévoit un déploiement progressif sur dix-huit mois, avec une priorité accordée aux axes les plus fréquentés. Un comité de suivi associant la société civile sera mis en place.</p>
<p><em>Avec notre correspondant. © Rédaction Ensoleillé.</em></p>"""


def cover(titre, couleur):
    """Génère une couverture placeholder (dégradé sombre + halo solaire)."""
    from PIL import Image, ImageDraw

    w, h = 1200, 675
    img = Image.new("RGB", (w, h), (10, 10, 10))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(10 + t * 120)
        g = int(10 + t * 70)
        b = int(5 + t * 10)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    # Halo solaire
    draw.ellipse([w - 360, -120, w + 120, 360], fill=(245, 166, 35))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=82)
    return ContentFile(buf.getvalue(), name="cover.jpg")


class Command(BaseCommand):
    help = "Données de démonstration : rubriques, auteur, articles, publicité."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Supprime les articles existants d'abord.")

    def handle(self, *args, **opts):
        ParametresSite.load()
        AdSenseConfig.load()

        # Admin
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@ensoleille.bj", "ensoleille2026")
            self.stdout.write(self.style.SUCCESS("Superuser créé : admin / ensoleille2026"))

        # Rubriques
        cats = {}
        for i, (nom, couleur, desc) in enumerate(RUBRIQUES):
            cat, _ = Categorie.objects.get_or_create(
                nom=nom, defaults={"couleur": couleur, "description": desc, "ordre": i}
            )
            cats[nom] = cat
        self.stdout.write(self.style.SUCCESS(f"{len(cats)} rubriques."))

        # Auteur
        auteur, _ = Auteur.objects.get_or_create(
            nom="Sandé Augustin IDOHOU",
            defaults={"role": "Rédacteur en chef", "bio": "Journaliste, fondateur de la Rédaction Ensoleillé."},
        )

        # Tags
        tags = [Tag.objects.get_or_create(nom=n)[0] for n in ["Bénin", "Cotonou", "UEMOA", "Énergie", "Actualité"]]

        if opts["reset"]:
            Article.objects.all().delete()

        # Articles
        now = timezone.now()
        created = 0
        for i, data in enumerate(ARTICLES):
            if Article.objects.filter(titre=data["titre"]).exists():
                continue
            art = Article(
                titre=data["titre"],
                chapeau=data["chapeau"],
                contenu=CORPS,
                categorie=cats[data["rub"]],
                auteur=auteur,
                statut="publie",
                a_la_une=data.get("une", False),
                urgent=data.get("urgent", False),
                credit_image="© Rédaction Ensoleillé",
                date_publication=now - timedelta(hours=i * 6),
                nombre_vues=(5 - i) * 137,
            )
            art.image_couverture.save("cover.jpg", cover(art.titre, cats[data["rub"]].couleur), save=False)
            art.save()
            art.tags.set(tags[:3])
            created += 1
        self.stdout.write(self.style.SUCCESS(f"{created} articles créés."))

        # Publicité de démonstration
        if not Publicite.objects.exists():
            pub = Publicite(
                titre="Espace publicitaire — Votre marque ici",
                emplacement="sidebar",
                lien="https://example.com",
                annonceur="Ensoleillé Régie",
                actif=True,
            )
            from PIL import Image, ImageDraw

            img = Image.new("RGB", (300, 250), (245, 166, 35))
            d = ImageDraw.Draw(img)
            d.text((20, 110), "Votre publicite ici", fill=(10, 10, 10))
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            pub.image.save("pub.jpg", ContentFile(buf.getvalue(), name="pub.jpg"), save=False)
            pub.save()
            self.stdout.write(self.style.SUCCESS("1 publicité de démonstration."))

        self.stdout.write(self.style.SUCCESS("Seed terminé. → http://127.0.0.1:8000/  ·  /dashboard/"))
