from rest_framework.serializers import ModelSerializer

from .models import Donatore, Sesso


class SessoLightSerializer(ModelSerializer):
    class Meta:
        model = Sesso
        fields = ["id", "codice"]


class DonatoreListSerializer(ModelSerializer):
    sesso = SessoLightSerializer(read_only=True)

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
        ]


class DonatoreDetailSerializer(DonatoreListSerializer):
    class Meta:
        model = Donatore
        fields = "__all__"
