# Rédaction Ensoleillé — La Presse

> **« Ensoleillé, lumière sur l'obscurité ! »**
> Plateforme média / blog d'actualité en **Django 5/6 + Tailwind CSS (CDN) + Alpine.js**, aux couleurs or/ambre sur fond noir (« le soleil dans la nuit »).

## ✨ Fonctionnalités

- **Articles** : couverture + crédit, titre, date/heure, chapô, contenu riche (gras, italique, citations), catégories, tags, auteurs, temps de lecture auto, compteur de vues, SEO (OG + JSON-LD `NewsArticle`).
- **Une / Urgent / Épinglé**, bandeau de unes défilant, « Les plus lus ».
- **Commentaires** sans compte, fil de réponses, modération, anti-spam (honeypot + throttling IP).
- **Régie publicitaire interne** (`Publicite`) par emplacement (header, sidebar, in-article après le 3ᵉ paragraphe, between, footer, popup) + **Google AdSense** (Auto Ads ou slots manuels) + `ads.txt`.
- **Tableau de bord personnalisé** `/dashboard/` (pas l'admin Django brut) : vue d'ensemble + graphe Chart.js, CRUD articles, modération commentaires, pubs + AdSense, rubriques/tags, auteurs, newsletter (export CSV), paramètres du site.
- **Recherche** plein-texte (PostgreSQL `SearchVector`, repli `icontains` en SQLite).
- **SEO** : `sitemap.xml`, `robots.txt`, flux **RSS** (global + par rubrique), Open Graph.
- **Mode nuit** (Alpine + localStorage), bandeau **RGPD/cookies**, pages **404/500** personnalisées.

## 🚀 Installation

```bash
# 1. Dépendances
pip install -r requirements.txt

# 2. Configuration
cp .env.example .env        # ajustez SECRET_KEY ; DATABASE_URL vide = SQLite

# 3. Base de données + données de démo
python manage.py migrate
python manage.py seed       # rubriques + 5 articles + 1 pub + compte admin

# 4. Lancement
python manage.py runserver
```

- Site public : <http://127.0.0.1:8000/>
- Tableau de bord : <http://127.0.0.1:8000/dashboard/> — **admin / ensoleille2026**
- Admin Django (secours) : <http://127.0.0.1:8000/admin/>

## 🐘 PostgreSQL (production)

Renseignez dans `.env` :

```
DATABASE_URL=postgres://user:password@localhost:5432/ensoleille
DEBUG=False
ALLOWED_HOSTS=votre-domaine.bj
```

Puis `python manage.py migrate`. La recherche plein-texte française s'active automatiquement sous PostgreSQL.

## 🎨 Charte

| or | ambre | jaune | noir | crème |
|----|-------|-------|------|-------|
| `#F5A623` | `#FF8C00` | `#FFC107` | `#0A0A0A` | `#FFF8E7` |

Header/footer/hero **noir-or**, lecture des articles sur **fond blanc**, dégradé solaire réservé au hero. Polices : *Great Vibes* (logo), *Playfair Display* (titres), *Inter* (corps).

## 🏗️ Architecture

```
config/            settings, urls, wsgi
apps/articles/     Article, Categorie, Tag, Auteur + vues publiques
apps/comments/     Commentaire + modération
apps/ads/          Publicite, AdSenseConfig + ad_slot
apps/core/         ParametresSite, newsletter, contact, SEO (sitemap/rss/robots/ads.txt)
apps/dashboard/    interface d'administration personnalisée
templates/         base, partials/, pages/, dashboard/
```

## 📦 Déploiement (Gunicorn + Nginx)

```bash
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

Servez `/static/` et `/media/` via Nginx, placez les secrets dans `.env`, `DEBUG=False`.

---
*Rédaction Ensoleillé — lumière sur l'obscurité.*
# ensoleille
# ensoleille
