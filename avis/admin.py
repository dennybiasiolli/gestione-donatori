from django.contrib import admin
from django.db.models import Q
from django.http import HttpRequest
from reversion.admin import VersionAdmin

from .models import Donatore, Donazione, Sesso, Sezione, StatoDonatore


@admin.register(Sesso)
class SessoAdmin(admin.ModelAdmin):
    pass


@admin.register(Sezione)
class SezioneAdmin(admin.ModelAdmin):
    list_display = ("descrizione", "utente", "email")

    def get_queryset(self, request: HttpRequest):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(utente=request.user)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            # removing `utente` field if user is not superuser
            form.base_fields.pop("utente", None)
        return form


@admin.register(StatoDonatore)
class StatoDonatoreAdmin(admin.ModelAdmin):
    list_display = (
        "codice",
        "descrizione",
        "sezione",
        "is_attivo",
        "can_export_elenco_soci_xls",
    )
    ordering = ("codice",)

    def get_queryset(self, request: HttpRequest):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(Q(sezione__isnull=True) | Q(sezione__utente=request.user))
        return qs

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        if not request.user.is_superuser and obj:
            return obj.sezione and obj.sezione.utente == request.user
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        if not request.user.is_superuser and obj:
            return obj.sezione and obj.sezione.utente == request.user
        return super().has_delete_permission(request, obj)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == "sezione":
            kwargs["queryset"] = Sezione.objects.filter(utente=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser and "sezione" in form.base_fields:
            form.base_fields["sezione"].required = True
            form.base_fields["sezione"].initial = form.base_fields["sezione"].queryset[
                0
            ]
        return form


class DonazioneInlineAdmin(admin.TabularInline):
    model = Donazione
    extra = 0
    ordering = ("-data_donazione",)


@admin.register(Donatore)
class DonatoreAdmin(VersionAdmin):
    list_display = (
        "num_tessera_avis",
        "num_tessera_ct",
        "data_iscrizione",
        "data_rilascio_tessera",
        "data_cessata_iscrizione",
        "cognome",
        "nome",
        "sesso",
        "data_nascita",
        "comune",
        "email",
        "cellulare",
        "stato_donatore",
    )
    list_filter = (
        ("sezione", admin.RelatedOnlyFieldListFilter),
        "sesso",
        "stato_donatore",
        "data_iscrizione",
        "data_rilascio_tessera",
    )
    ordering = ("cognome", "nome")
    search_fields = (
        "num_tessera_avis",
        "cognome",
        "nome",
        "comune",
        "email",
        "telefono",
        "cellulare",
    )
    inlines = [DonazioneInlineAdmin]
    save_on_top = True

    def get_queryset(self, request: HttpRequest):
        qs = super().get_queryset(request).select_related("sesso", "sezione")
        if not request.user.is_superuser:
            qs = qs.filter(sezione__utente=request.user)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == "sezione":
            kwargs["queryset"] = Sezione.objects.filter(utente=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields["sezione"].initial = form.base_fields["sezione"].queryset[
                0
            ]
        return form
