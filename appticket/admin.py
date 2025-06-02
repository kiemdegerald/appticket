from django.contrib import admin
from .models import Agent, Agence, Client, Ticket

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'is_active', 'date_creation')
    search_fields = ('prenom', 'nom')
    list_filter = ('is_active', 'date_creation')

@admin.register(Agence)
class AgenceAdmin(admin.ModelAdmin):
    list_display = ('nom_agence', 'adresse', 'is_active')
    search_fields = ('nom_agence', 'adresse')
    list_filter = ('is_active', 'date_creation')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_creation')
    search_fields = ('id',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('numero_ticket', 'type_reservation', 'etat', 'date_emission')
    list_filter = ('etat', 'type_reservation', 'date_emission')
    search_fields = ('numero_ticket',)
