from rest_framework.serializers import ModelSerializer

from .models import Donatore, Sesso, StatoDonatore


class SessoLightSerializer(ModelSerializer):
    class Meta:
        model = Sesso
        fields = ["id", "codice"]


class StatoDonatoreSerializer(ModelSerializer):
    class Meta:
        model = StatoDonatore
        fields = ["id", "codice", "descrizione"]


class DonatoreListSerializer(ModelSerializer):
    sesso = SessoLightSerializer(read_only=True)
    stato_donatore = StatoDonatoreSerializer(read_only=True)

    class Meta:
        model = Donatore
        fields = [
            "id",
            "num_tessera_avis",
            "num_tessera_ct",
            "nome",
            "cognome",
            "sesso",
            "gruppo_sanguigno",
            "rh",
            "indirizzo",
            "frazione",
            "cap",
            "comune",
            "provincia",
            "telefono",
            "telefono_lavoro",
            "cellulare",
            "fax",
            "email",
            "stato_donatore",
        ]


class DonatoreDetailSerializer(DonatoreListSerializer):
    class Meta:
        model = Donatore
        fields = "__all__"
