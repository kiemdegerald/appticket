# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from . import views
from . import views_agent

# Configuration du router pour les ViewSets
router = DefaultRouter()
router.register(r'clients', views.ClientViewSet)
router.register(r'agents', views.AgentViewSet)
router.register(r'administrateurs', views.AdministrateurViewSet)
router.register(r'agences', views.AgenceViewSet)
router.register(r'notifications', views.NotificationViewSet)

# URLs principales de l'application

manual_urlpatterns = [
    # ==================== URLS POUR LES CLIENTS ====================
    
    # Page de création de ticket
    path('client/creer-ticket/', 
         views.create_ticket_view, 
         name='create-ticket'),
    
    # Réservation de tickets
    path('client/reserver-ticket/', 
         views.TicketReservationAPIView.as_view(), 
         name='reserver-ticket'),
    
    # Consultation de la file d'attente
    path('client/file-attente/<uuid:agence_id>/', 
         views.FileAttenteAPIView.as_view(), 
         name='file-attente'),
    
    # Trouver les agences les plus proches
    path('client/agences-proches/', 
         views.AgencesProchesAPIView.as_view(), 
         name='agences-proches'),
    
    # Mettre à jour la position du client (via le ViewSet)
    # POST /api/clients/update_position/
    
    
    # ==================== URLS POUR LES AGENTS ====================
    
    # Interface agent
    path('agent/dashboard/', 
         views.agent_dashboard, 
         name='agent_dashboard'),
    path('agent/tickets/', 
         views_agent.AgentTicketsView.as_view(), 
         name='agent_tickets'),
    path('agent/file-attente/', 
         views_agent.AgentFileAttenteView.as_view(), 
         name='agent_file_attente'),
    path('agent/statistiques/', 
         views_agent.AgentStatistiquesView.as_view(), 
         name='agent_statistiques'),
    
    # API endpoints pour l'interface agent
    path('agent/tickets-en-cours/', 
         views_agent.AgentTicketsEnCoursAPIView.as_view(), 
         name='agent_tickets_en_cours'),
    path('agent/ticket-en-cours/', 
         views_agent.AgentTicketEnCoursAPIView.as_view(), 
         name='agent_ticket_en_cours'),
    path('agent/statistiques-api/', 
         views_agent.AgentStatistiquesAPIView.as_view(), 
         name='agent_statistiques_api'),
    
    # Appeler un ticket
    path('agent/appeler-ticket/', 
         views.AppelTicketAPIView.as_view(), 
         name='appeler-ticket'),
    
    # Terminer un ticket
    path('agent/terminer-ticket/', 
         views.TerminerTicketAPIView.as_view(), 
         name='terminer-ticket'),
    
    # Gestion de la distribution automatique
    path('agent/distribution-automatique/', 
         views.DistributionAutomatiqueAPIView.as_view(), 
         name='distribution-automatique'),
    
    # Envoyer une notification
    path('agent/envoyer-notification/', 
         views.NotificationAPIView.as_view(), 
         name='envoyer-notification'),
    
    # Consulter les tickets en cours d'un agent (via le ViewSet)
    # GET /api/agents/{agent_id}/tickets_en_cours/
    
    
    # ==================== URLS POUR LES ADMINISTRATEURS ====================
    
    # Statistiques générales
    path('admin/statistiques/', 
         views.StatistiquesAPIView.as_view(), 
         name='statistiques-generales'),
    
    # Statistiques par agence
    path('admin/statistiques-agence/<uuid:agence_id>/', 
         views.AgenceStatistiquesAPIView.as_view(), 
         name='statistiques-agence'),
    path('admin/agences/create/', views.create_agence_view, name='create_agence'),
]

urlpatterns = format_suffix_patterns(manual_urlpatterns) + router.urls
