from django.shortcuts import get_object_or_404, redirect

from .models import Publicite


def clic(request, pk):
    """Redirection trackée : incrémente les clics puis renvoie vers l'annonceur."""
    pub = get_object_or_404(Publicite, pk=pk)
    Publicite.objects.filter(pk=pk).update(clics=pub.clics + 1)
    return redirect(pub.lien or "/")
