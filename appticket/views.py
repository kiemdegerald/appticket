# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.db import transaction
from datetime import datetime, timedelta
import threading
import time

from .models import (
    Client, Agent, Administrateur, Agence, Ticket, 
    Notification, ConfigurationDistribution
)
from .serializers import (
    ClientSerializer, AgentSerializer, AdministrateurSerializer,
    AgenceSerializer, TicketSerializer, NotificationSerializer,
    TicketReservationSerializer, FileAttenteSerializer,
    StatistiquesSerializer, ConfigurationDistributionSerializer,
    AppelTicketSerializer
)


# ==================== VUES POUR LES CLIENTS ====================

class ClientViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des clients"""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    
    @action(detail=False, methods=['post'])
    def update_position(self, request):
        """Endpoint pour mettre à jour la position d'un client"""
        client_id = request.data.get('client_id')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        if not all([client_id, latitude, longitude]):
            return Response(
                {'error': 'client_id, latitude et longitude sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            client = Client.objects.get(id=client_id)
            client.latitude = latitude
            client.longitude = longitude
            client.save()
            
            serializer = self.get_serializer(client)
            return Response(serializer.data)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )


class TicketReservationAPIView(APIView):
    """Vue pour la réservation de tickets par les clients"""
    
    def post(self, request):
        """Réserver un nouveau ticket"""
        serializer = TicketReservationSerializer(data=request.data)
        if serializer.is_valid():
            ticket = serializer.save()
            
            # Obtenir la position dans la file d'attente via le serializer
            ticket_serializer = TicketSerializer(ticket)
            position_file = ticket_serializer.data.get('position_file', 'N/A')
            
            # Créer une notification de confirmation
            Notification.objects.create(
                ticket=ticket,
                message=f"Votre ticket {ticket.numero_ticket} a été créé. Vous êtes en position {position_file} dans la file d'attente.",
                type_notification='information'
            )
            
            return Response(
                ticket_serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileAttenteAPIView(APIView):
    """Vue pour consulter la file d'attente d'une agence"""
    
    def get(self, request, agence_id):
        """Récupérer la file d'attente d'une agence"""
        try:
            agence = Agence.objects.get(id_agence=agence_id)
        except Agence.DoesNotExist:
            return Response(
                {'error': 'Agence introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Récupérer tous les tickets en attente
        tickets_en_attente = Ticket.objects.filter(
            agence=agence,
            etat='en_attente'
        ).order_by('date_emission')
        
        # Calculer le temps d'attente moyen
        tickets_termines_aujourd_hui = Ticket.objects.filter(
            agence=agence,
            etat='termine',
            date_emission__date=timezone.now().date()
        )
        
        temps_attente_moyen = 0
        if tickets_termines_aujourd_hui.exists():
            total_temps = sum([
                (ticket.date_fin - ticket.date_emission).total_seconds() / 60
                for ticket in tickets_termines_aujourd_hui
                if ticket.date_fin
            ])
            temps_attente_moyen = int(total_temps / tickets_termines_aujourd_hui.count()) if total_temps > 0 else 0
        
        # Dernier ticket appelé
        dernier_ticket_appele = Ticket.objects.filter(
            agence=agence,
            etat__in=['en_cours', 'termine']
        ).order_by('-date_appel').first()
        
        data = {
            'agence': AgenceSerializer(agence).data,
            'tickets_en_attente': TicketSerializer(tickets_en_attente, many=True).data,
            'nombre_tickets_en_attente': tickets_en_attente.count(),
            'temps_attente_moyen': temps_attente_moyen,
            'dernier_ticket_appele': TicketSerializer(dernier_ticket_appele).data if dernier_ticket_appele else None
        }
        
        return Response(data)


class AgencesProchesAPIView(APIView):
    """Vue pour trouver les agences les plus proches d'un client"""
    
    def post(self, request):
        """Trouver les agences les plus proches"""
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        limite = request.data.get('limite', 5)  # Par défaut, retourner 5 agences
        
        if not all([latitude, longitude]):
            return Response(
                {'error': 'latitude et longitude sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Ajouter les coordonnées du client au contexte pour le calcul de distance
        request.client_lat = latitude
        request.client_lng = longitude
        
        agences = Agence.objects.filter(is_active=True)
        agences_avec_distance = []
        
        for agence in agences:
            distance = AgenceSerializer.calculate_distance(
                float(latitude), float(longitude),
                float(agence.latitude), float(agence.longitude)
            )
            agences_avec_distance.append({
                'agence': agence,
                'distance': distance
            })
        
        # Trier par distance et limiter les résultats
        agences_avec_distance.sort(key=lambda x: x['distance'])
        agences_proches = agences_avec_distance[:limite]
        
        serializer = AgenceSerializer(
            [item['agence'] for item in agences_proches],
            many=True,
            context={'request': request}
        )
        
        return Response(serializer.data)


# ==================== VUES POUR LES AGENTS ====================

class AgentViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des agents"""
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    
    @action(detail=True, methods=['get'])
    def tickets_en_cours(self, request, pk=None):
        """Récupérer les tickets en cours d'un agent"""
        agent = self.get_object()
        tickets = Ticket.objects.filter(agent=agent, etat='en_cours')
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)


class AppelTicketAPIView(APIView):
    """Vue pour l'appel de tickets par les agents"""
    
    def put(self, request):
        """Appeler un ticket"""
        serializer = AppelTicketSerializer(data=request.data)
        if serializer.is_valid():
            ticket_id = serializer.validated_data['ticket_id']
            agent_id = serializer.validated_data['agent_id']
            message_notification = serializer.validated_data.get('message_notification', '')
            
            try:
                with transaction.atomic():
                    ticket = Ticket.objects.select_for_update().get(id_ticket=ticket_id)
                    agent = Agent.objects.get(id=agent_id)
                    
                    # Mettre à jour le ticket
                    ticket.agent = agent
                    ticket.etat = 'en_cours'
                    ticket.date_appel = timezone.now()
                    ticket.save()
                    
                    # Créer une notification
                    message = message_notification or f"Votre ticket {ticket.numero_ticket} est maintenant appelé. Présentez-vous au guichet."
                    Notification.objects.create(
                        ticket=ticket,
                        message=message,
                        type_notification='appel'
                    )
                    
                    return Response({
                        'message': 'Ticket appelé avec succès',
                        'ticket': TicketSerializer(ticket).data
                    })
                    
            except (Ticket.DoesNotExist, Agent.DoesNotExist) as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TerminerTicketAPIView(APIView):
    """Vue pour terminer le traitement d'un ticket"""
    
    def put(self, request):
        """Terminer un ticket"""
        ticket_id = request.data.get('ticket_id')
        
        if not ticket_id:
            return Response(
                {'error': 'ticket_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ticket = Ticket.objects.get(id_ticket=ticket_id)
            if ticket.etat != 'en_cours':
                return Response(
                    {'error': 'Ce ticket n\'est pas en cours de traitement'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            ticket.etat = 'termine'
            ticket.date_fin = timezone.now()
            ticket.save()
            
            # Notification de fin
            Notification.objects.create(
                ticket=ticket,
                message=f"Le traitement de votre ticket {ticket.numero_ticket} est terminé. Merci de votre visite.",
                type_notification='information'
            )
            
            return Response({
                'message': 'Ticket terminé avec succès',
                'ticket': TicketSerializer(ticket).data
            })
            
        except Ticket.DoesNotExist:
            return Response(
                {'error': 'Ticket introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )


class DistributionAutomatiqueAPIView(APIView):
    """Vue pour gérer la distribution automatique des tickets"""
    
    def post(self, request):
        """Démarrer la distribution automatique pour une agence"""
        agence_id = request.data.get('agence_id')
        intervalle_minutes = request.data.get('intervalle_minutes', 5)
        
        if not agence_id:
            return Response(
                {'error': 'agence_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            agence = Agence.objects.get(id_agence=agence_id)
            config, created = ConfigurationDistribution.objects.get_or_create(
                agence=agence,
                defaults={'intervalle_minutes': intervalle_minutes}
            )
            
            config.is_active = True
            config.intervalle_minutes = intervalle_minutes
            config.save()
            
            # Démarrer le thread de distribution
            self.start_auto_distribution(agence_id)
            
            return Response({
                'message': 'Distribution automatique démarrée',
                'configuration': ConfigurationDistributionSerializer(config).data
            })
            
        except Agence.DoesNotExist:
            return Response(
                {'error': 'Agence introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def delete(self, request):
        """Arrêter la distribution automatique pour une agence"""
        agence_id = request.data.get('agence_id')
        
        if not agence_id:
            return Response(
                {'error': 'agence_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            agence = Agence.objects.get(id_agence=agence_id)
            config = ConfigurationDistribution.objects.get(agence=agence)
            config.is_active = False
            config.save()
            
            return Response({
                'message': 'Distribution automatique arrêtée',
                'configuration': ConfigurationDistributionSerializer(config).data
            })
            
        except (Agence.DoesNotExist, ConfigurationDistribution.DoesNotExist):
            return Response(
                {'error': 'Configuration introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def start_auto_distribution(self, agence_id):
        """Démarre un thread pour la distribution automatique"""
        def distribute():
            while True:
                try:
                    config = ConfigurationDistribution.objects.get(
                        agence__id_agence=agence_id,
                        is_active=True
                    )
                    
                    # Chercher le prochain ticket en attente
                    next_ticket = Ticket.objects.filter(
                        agence=config.agence,
                        etat='en_attente'
                    ).order_by('date_emission').first()
                    
                    if next_ticket:
                        # Chercher un agent disponible (sans ticket en cours)
                        agent_disponible = Agent.objects.filter(
                            is_active=True
                        ).exclude(
                            tickets__etat='en_cours'
                        ).first()
                        
                        if agent_disponible:
                            with transaction.atomic():
                                next_ticket.agent = agent_disponible
                                next_ticket.etat = 'en_cours'
                                next_ticket.date_appel = timezone.now()
                                next_ticket.save()
                                
                                # Notification automatique
                                Notification.objects.create(
                                    ticket=next_ticket,
                                    message=f"Ticket {next_ticket.numero_ticket} appelé automatiquement. Présentez-vous au guichet.",
                                    type_notification='appel'
                                )
                    
                    config.derniere_execution = timezone.now()
                    config.save()
                    
                    time.sleep(config.intervalle_minutes * 60)
                    
                except ConfigurationDistribution.DoesNotExist:
                    break  # Configuration supprimée ou désactivée
                except Exception as e:
                    print(f"Erreur dans la distribution automatique: {e}")
                    time.sleep(60)  # Attendre 1 minute avant de réessayer
        
        thread = threading.Thread(target=distribute, daemon=True)
        thread.start()


class NotificationAPIView(APIView):
    """Vue pour envoyer des notifications personnalisées"""
    
    def post(self, request):
        """Envoyer une notification à un client"""
        ticket_id = request.data.get('ticket_id')
        message = request.data.get('message')
        type_notification = request.data.get('type_notification', 'information')
        
        if not all([ticket_id, message]):
            return Response(
                {'error': 'ticket_id et message sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ticket = Ticket.objects.get(id_ticket=ticket_id)
            notification = Notification.objects.create(
                ticket=ticket,
                message=message,
                type_notification=type_notification
            )
            
            return Response({
                'message': 'Notification envoyée avec succès',
                'notification': NotificationSerializer(notification).data
            })
            
        except Ticket.DoesNotExist:
            return Response(
                {'error': 'Ticket introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )


# ==================== VUES POUR LES ADMINISTRATEURS ====================

class StatistiquesAPIView(APIView):
    """Vue pour les statistiques générales"""
    
    def get(self, request):
        """Récupérer les statistiques complètes"""
        today = timezone.now().date()
        
        # Statistiques générales
        total_tickets_aujourd_hui = Ticket.objects.filter(date_emission__date=today).count()
        total_tickets_en_attente = Ticket.objects.filter(etat='en_attente').count()
        total_tickets_termines_aujourd_hui = Ticket.objects.filter(
            etat='termine',
            date_emission__date=today
        ).count()
        
        # Temps d'attente moyen
        tickets_termines = Ticket.objects.filter(
            etat='termine',
            date_emission__date=today,
            date_fin__isnull=False
        )
        
        temps_attente_moyen = 0
        if tickets_termines.exists():
            total_temps = sum([
                (ticket.date_fin - ticket.date_emission).total_seconds() / 60
                for ticket in tickets_termines
            ])
            temps_attente_moyen = total_temps / tickets_termines.count()
        
        # Répartition par type de réservation
        repartition_par_type = dict(
            Ticket.objects.filter(date_emission__date=today)
            .values('type_reservation')
            .annotate(count=Count('type_reservation'))
            .values_list('type_reservation', 'count')
        )
        
        # Répartition par agence
        repartition_par_agence = dict(
            Ticket.objects.filter(date_emission__date=today)
            .values('agence__nom_agence')
            .annotate(count=Count('agence'))
            .values_list('agence__nom_agence', 'count')
        )
        
        # Tickets par heure (dernières 24h)
        tickets_par_heure = {}
        for i in range(24):
            heure = timezone.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=i)
            count = Ticket.objects.filter(
                date_emission__hour=heure.hour,
                date_emission__date=heure.date()
            ).count()
            tickets_par_heure[f"{heure.hour:02d}h"] = count
        
        data = {
            'total_tickets_aujourd_hui': total_tickets_aujourd_hui,
            'total_tickets_en_attente': total_tickets_en_attente,
            'total_tickets_termines_aujourd_hui': total_tickets_termines_aujourd_hui,
            'temps_attente_moyen': round(temps_attente_moyen, 2),
            'repartition_par_type': repartition_par_type,
            'repartition_par_agence': repartition_par_agence,
            'tickets_par_heure': dict(reversed(list(tickets_par_heure.items())))
        }
        
        return Response(data)


class AgenceStatistiquesAPIView(APIView):
    """Vue pour les statistiques d'une agence spécifique"""
    
    def get(self, request, agence_id):
        """Récupérer les statistiques d'une agence"""
        try:
            agence = Agence.objects.get(id_agence=agence_id)
        except Agence.DoesNotExist:
            return Response(
                {'error': 'Agence introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        today = timezone.now().date()
        
        tickets_today = Ticket.objects.filter(agence=agence, date_emission__date=today)
        
        data = {
            'agence': AgenceSerializer(agence).data,
            'tickets_aujourd_hui': tickets_today.count(),
            'tickets_en_attente': tickets_today.filter(etat='en_attente').count(),
            'tickets_en_cours': tickets_today.filter(etat='en_cours').count(),
            'tickets_termines': tickets_today.filter(etat='termine').count(),
            'repartition_par_type': dict(
                tickets_today.values('type_reservation')
                .annotate(count=Count('type_reservation'))
                .values_list('type_reservation', 'count')
            )
        }
        
        return Response(data)


# ==================== VIEWSETS GÉNÉRIQUES ====================

class AdministrateurViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des administrateurs"""
    queryset = Administrateur.objects.all()
    serializer_class = AdministrateurSerializer


class AgenceViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des agences"""
    queryset = Agence.objects.all()
    serializer_class = AgenceSerializer
    
    @action(detail=True, methods=['get'])
    def file_attente(self, request, pk=None):
        """Raccourci pour accéder à la file d'attente d'une agence"""
        agence = self.get_object()
        view = FileAttenteAPIView()
        return view.get(request, agence.id_agence)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet en lecture seule pour les notifications"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        """Filtrer les notifications par ticket si spécifié"""
        queryset = super().get_queryset()
        ticket_id = self.request.query_params.get('ticket_id')
        if ticket_id:
            queryset = queryset.filter(ticket__id_ticket=ticket_id)
        return queryset.order_by('-date_envoi')


@api_view(['GET'])
def agent_dashboard(request):
    try:
        # Récupérer l'agent par son ID
        agent = Agent.objects.get(id='369dbb65-0d67-47fd-bad2-1182c6c09c67')
        return render(request, 'appticket/agent_dashboard.html', {'agent': agent})
    except Agent.DoesNotExist:
        return Response({'error': 'Agent non trouvé'}, status=404)


def create_ticket_view(request):
    return render(request, 'appticket/create_ticket.html')