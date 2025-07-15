from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Agent, Ticket, Agence
from .serializers import TicketSerializer
from django.utils import timezone

class AgentDashboardView(TemplateView):
    template_name = 'agent/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pour l'instant, on récupère le premier agent disponible
        context['agent'] = Agent.objects.filter(is_active=True).first()
        return context

class AgentTicketsView(TemplateView):
    template_name = 'agent/tickets.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agent'] = Agent.objects.filter(is_active=True).first()
        return context

class AgentFileAttenteView(TemplateView):
    template_name = 'agent/file_attente.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agent'] = Agent.objects.filter(is_active=True).first()
        return context

class AgentStatistiquesView(TemplateView):
    template_name = 'agent/statistiques.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agent'] = Agent.objects.filter(is_active=True).first()
        return context

# API Views pour l'interface agent
class AgentTicketsEnCoursAPIView(APIView):
    def get(self, request):
        agent = Agent.objects.filter(is_active=True).first()
        if not agent:
            return Response([], status=200)
        # Montrer uniquement les tickets en attente
        tickets = Ticket.objects.filter(
            etat='en_attente'
        ).order_by('date_emission')
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)

class AgentTicketEnCoursAPIView(APIView):
    def get(self, request):
        agent = Agent.objects.filter(is_active=True).first()
        if not agent:
            return Response({}, status=200)
        # Trouver le ticket en cours pour l'agent actif
        try:
            ticket = Ticket.objects.get(etat='en_cours', agent=agent)
            serializer = TicketSerializer(ticket)
            return Response(serializer.data)
        except Ticket.DoesNotExist:
            return Response({}, status=200)

class AgentStatistiquesAPIView(APIView):
    def get(self, request):
        agent = Agent.objects.filter(is_active=True).first()
        today = timezone.now().date()

        # Tickets en attente et en cours
        tickets_en_cours = Ticket.objects.filter(
            etat__in=['en_attente', 'en_cours']
        ).count()
        
        # Tickets terminés aujourd'hui
        tickets_termines_aujourd_hui = Ticket.objects.filter(
            etat='termine',
            date_fin__date=today
        ).count()

        # Calcul du temps moyen de traitement
        tickets_termines = Ticket.objects.filter(
            etat='termine',
            date_fin__date=today
        )
        
        temps_attente_moyen = 0
        if tickets_termines.exists():
            total_temps = sum([
                (ticket.date_fin - ticket.date_emission).total_seconds() / 60
                for ticket in tickets_termines
            ])
            temps_attente_moyen = round(total_temps / tickets_termines.count(), 2)

        return Response({
            'tickets_en_cours': tickets_en_cours,
            'tickets_termines_aujourd_hui': tickets_termines_aujourd_hui,
            'temps_attente_moyen': temps_attente_moyen
        })

# NOUVELLE VUE POUR LES TICKETS DE L'AGENCE
class AgentTicketsAgenceAPIView(APIView):
    """Vue pour récupérer tous les tickets d'une agence pour les agents"""
    
    def get(self, request, agence_id):
        """Récupérer tous les tickets d'une agence"""
        try:
            agence = Agence.objects.get(id_agence=agence_id)
        except Agence.DoesNotExist:
            return Response(
                {'error': 'Agence introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Récupérer tous les tickets de l'agence (tous états)
        tous_les_tickets = Ticket.objects.filter(
            agence=agence
        ).order_by('-date_emission')
        
        # Récupérer les tickets en attente
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
            'agence': {
                'id_agence': agence.id_agence,
                'nom_agence': agence.nom_agence
            },
            'tickets_en_attente': TicketSerializer(tickets_en_attente, many=True).data,
            'tous_les_tickets': TicketSerializer(tous_les_tickets, many=True).data,
            'nombre_tickets_en_attente': tickets_en_attente.count(),
            'temps_attente_moyen': temps_attente_moyen,
            'dernier_ticket_appele': TicketSerializer(dernier_ticket_appele).data if dernier_ticket_appele else None
        }
        
        return Response(data)

class AppelerTicketAPIView(APIView):
    def put(self, request):
        try:
            ticket_id = request.data.get('ticket_id')
            agent_id = request.data.get('agent_id')
            
            ticket = Ticket.objects.get(id_ticket=ticket_id)
            agent = Agent.objects.get(id=agent_id)
            
            # Mettre à jour le ticket
            ticket.etat = 'en_cours'
            ticket.agent = agent
            ticket.date_debut = timezone.now()
            ticket.save()
            
            return Response({
                'message': 'Ticket appelé avec succès',
                'ticket': TicketSerializer(ticket).data
            })
        except Ticket.DoesNotExist:
            return Response(
                {'error': 'Ticket non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Agent.DoesNotExist:
            return Response(
                {'error': 'Agent non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class TerminerTicketAPIView(APIView):
    def put(self, request):
        try:
            ticket_id = request.data.get('ticket_id')
            ticket = Ticket.objects.get(id_ticket=ticket_id)
            
            # Mettre à jour le ticket
            ticket.etat = 'termine'
            ticket.date_fin = timezone.now()
            ticket.save()
            
            return Response({
                'message': 'Ticket terminé avec succès',
                'ticket': TicketSerializer(ticket).data
            })
        except Ticket.DoesNotExist:
            return Response(
                {'error': 'Ticket non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            ) 