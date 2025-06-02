"""
URL configuration for ticket project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# ==================== CONFIGURATION DU PROJET PRINCIPAL ====================
# 
# Dans le fichier urls.py principal de votre projet Django, ajoutez :
#
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
 
urlpatterns = [
     path('admin/', admin.site.urls),
     path('api/', include('appticket.urls')),
     path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
     path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
 ]



# ==================== DOCUMENTATION DES ENDPOINTS ====================

"""
DOCUMENTATION COMPLÈTE DES ENDPOINTS API ONEA

BASE URL: http://localhost:8000/api/

==================== ENDPOINTS POUR LES CLIENTS ====================

1. RÉSERVER UN TICKET
   POST /api/client/reserver-ticket/
   Body: {
       "client_latitude": 12.3586,
       "client_longitude": -1.5234,
       "type_reservation": "normal"  // ou "prioritaire", "handicape", "personne_agee"
   }
   Response: {
       "id_ticket": "uuid",
       "numero_ticket": "ONA-20241201-0001",
       "type_reservation": "normal",
       "date_emission": "2024-12-01T10:30:00Z",
       "etat": "en_attente",
       "agence_la_plus_proche": {...}
   }

2. CONSULTER LA FILE D'ATTENTE
   GET /api/client/file-attente/{agence_id}/
   Response: {
       "agence": {...},
       "tickets_en_attente": [...],
       "nombre_tickets_en_attente": 5,
       "temps_attente_moyen": 15,
       "dernier_ticket_appele": {...}
   }

3. TROUVER LES AGENCES PROCHES
   POST /api/client/agences-proches/
   Body: {
       "latitude": 12.3586,
       "longitude": -1.5234,
       "limite": 3  // optionnel, défaut 5
   }
   Response: [
       {
           "id_agence": "uuid",
           "nom_agence": "Agence Centrale",
           "distance": 2.5,
           "tickets_en_attente": 3,
           ...
       }
   ]

4. METTRE À JOUR LA POSITION CLIENT
   POST /api/clients/update_position/
   Body: {
       "client_id": "uuid",
       "latitude": 12.3586,
       "longitude": -1.5234
   }

==================== ENDPOINTS POUR LES AGENTS ====================

5. APPELER UN TICKET
   PUT /api/agent/appeler-ticket/
   Body: {
       "ticket_id": "uuid",
       "agent_id": "uuid",
       "message_notification": "Présentez-vous au guichet 3"  // optionnel
   }
   Response: {
       "message": "Ticket appelé avec succès",
       "ticket": {...}
   }

6. TERMINER UN TICKET
   PUT /api/agent/terminer-ticket/
   Body: {
       "ticket_id": "uuid"
   }

7. DÉMARRER LA DISTRIBUTION AUTOMATIQUE
   POST /api/agent/distribution-automatique/
   Body: {
       "agence_id": "uuid",
       "intervalle_minutes": 5  // optionnel, défaut 5
   }

8. ARRÊTER LA DISTRIBUTION AUTOMATIQUE
   DELETE /api/agent/distribution-automatique/
   Body: {
       "agence_id": "uuid"
   }

9. ENVOYER UNE NOTIFICATION
   POST /api/agent/envoyer-notification/
   Body: {
       "ticket_id": "uuid",
       "message": "Veuillez vous présenter avec vos documents",
       "type_notification": "information"  // ou "rappel", "annulation"
   }

10. CONSULTER LES TICKETS EN COURS D'UN AGENT
    GET /api/agents/{agent_id}/tickets_en_cours/

==================== ENDPOINTS POUR LES ADMINISTRATEURS ====================

11. STATISTIQUES GÉNÉRALES
    GET /api/admin/statistiques/
    Response: {
        "total_tickets_aujourd_hui": 45,
        "total_tickets_en_attente": 12,
        "total_tickets_termines_aujourd_hui": 33,
        "temps_attente_moyen": 18.5,
        "repartition_par_type": {...},
        "repartition_par_agence": {...},
        "tickets_par_heure": {...}
    }

12. STATISTIQUES PAR AGENCE
    GET /api/admin/statistiques-agence/{agence_id}/
    Response: {
        "agence": {...},
        "tickets_aujourd_hui": 15,
        "tickets_en_attente": 5,
        "tickets_en_cours": 2,
        "tickets_termines": 8,
        "repartition_par_type": {...}
    }

==================== ENDPOINTS VIEWSETS (CRUD COMPLET) ====================

13. GESTION DES CLIENTS
    GET /api/clients/                    # Liste tous les clients
    POST /api/clients/                   # Créer un client
    GET /api/clients/{client_id}/        # Détails d'un client
    PUT /api/clients/{client_id}/        # Modifier un client
    DELETE /api/clients/{client_id}/     # Supprimer un client

14. GESTION DES AGENTS
    GET /api/agents/                     # Liste tous les agents
    POST /api/agents/                    # Créer un agent
    GET /api/agents/{agent_id}/          # Détails d'un agent
    PUT /api/agents/{agent_id}/          # Modifier un agent
    DELETE /api/agents/{agent_id}/       # Supprimer un agent

15. GESTION DES ADMINISTRATEURS
    GET /api/administrateurs/            # Liste tous les administrateurs
    POST /api/administrateurs/           # Créer un administrateur
    GET /api/administrateurs/{admin_id}/ # Détails d'un administrateur
    PUT /api/administrateurs/{admin_id}/ # Modifier un administrateur
    DELETE /api/administrateurs/{admin_id}/ # Supprimer un administrateur

16. GESTION DES AGENCES
    GET /api/agences/                    # Liste toutes les agences
    POST /api/agences/                   # Créer une agence
    GET /api/agences/{agence_id}/        # Détails d'une agence
    PUT /api/agences/{agence_id}/        # Modifier une agence
    DELETE /api/agences/{agence_id}/     # Supprimer une agence
    GET /api/agences/{agence_id}/file_attente/ # File d'attente de l'agence

17. GESTION DES NOTIFICATIONS
    GET /api/notifications/              # Liste toutes les notifications
    GET /api/notifications/?ticket_id={uuid} # Notifications d'un ticket
    GET /api/notifications/{notif_id}/   # Détails d'une notification

==================== CODES DE STATUT HTTP ====================

200 OK                  - Requête réussie
201 Created            - Ressource créée avec succès
400 Bad Request        - Données invalides
404 Not Found          - Ressource introuvable
500 Internal Server Error - Erreur serveur

==================== FORMATS DE DONNÉES ====================

Tous les endpoints acceptent et retournent du JSON.
Les UUIDs sont utilisés comme identifiants.
Les dates sont au format ISO 8601 (YYYY-MM-DDTHH:MM:SSZ).
Les coordonnées GPS sont en degrés décimaux.

==================== EXEMPLES D'UTILISATION ====================

# Workflow complet client :
1. POST /api/client/agences-proches/ (trouver agences)
2. POST /api/client/reserver-ticket/ (réserver)
3. GET /api/client/file-attente/{agence_id}/ (suivre file)

# Workflow complet agent :
1. GET /api/agences/{agence_id}/file_attente/ (voir file)
2. PUT /api/agent/appeler-ticket/ (appeler client)
3. PUT /api/agent/terminer-ticket/ (terminer service)

# Workflow administrateur :
1. GET /api/admin/statistiques/ (vue d'ensemble)
2. GET /api/admin/statistiques-agence/{id}/ (détails agence)
"""