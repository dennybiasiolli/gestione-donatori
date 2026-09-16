from .models import Donatore


def elenco_stampa(request):
    if not request.user.is_authenticated:
        return {}
    return {
        "elenco_stampa_count": Donatore.objects.filter(
            stampa_donatore=True,
            sezione__utente=request.user,
        ).count()
    }
