# serializers.py
from rest_framework import serializers
from .models import Client, Agent, Administrateur, Agence, Ticket, Notification, ConfigurationDistribution
from django.utils import timezone
from decimal import Decimal
import math


class ClientSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle Client"""
    
    class Meta:
        model = Client
        fields = ['id', 'latitude', 'longitude', 'date_creation']
        read_only_fields = ['id', 'date_creation']
    
    def validate_latitude(self, value):
        """Valide que la latitude est dans les limites correctes"""
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("La latitude doit être comprise entre -90 et 90 degrés.")
        return value
    
    def validate_longitude(self, value):
        """Valide que la longitude est dans les limites correctes"""
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("La longitude doit être comprise entre -180 et 180 degrés.")
        return value


class AgentSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle Agent"""
    tickets_en_cours = serializers.SerializerMethodField()
    
    class Meta:
        model = Agent
        fields = ['id', 'nom', 'prenom', 'is_active', 'date_creation', 'tickets_en_cours']
        read_only_fields = ['id', 'date_creation', 'tickets_en_cours']
    
    def get_tickets_en_cours(self, obj):
        """Retourne le nombre de tickets en cours pour cet agent"""
        return obj.tickets.filter(etat='en_cours').count()


class AdministrateurSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle Administrateur"""
    
    class Meta:
        model = Administrateur
        fields = ['id', 'nom', 'prenom', 'is_active', 'date_creation']
        read_only_fields = ['id', 'date_creation']


class AgenceSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle Agence"""
    tickets_en_attente = serializers.SerializerMethodField()
    tickets_total_jour = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = Agence
        fields = [
            'id_agence', 'nom_agence', 'latitude', 'longitude', 
            'adresse', 'is_active', 'date_creation',
            'tickets_en_attente', 'tickets_total_jour', 'distance'
        ]
        read_only_fields = ['id_agence', 'date_creation', 'tickets_en_attente', 'tickets_total_jour', 'distance']
    
    def get_tickets_en_attente(self, obj):
        """Retourne le nombre de tickets en attente dans cette agence"""
        return obj.tickets.filter(etat='en_attente').count()
    
    def get_tickets_total_jour(self, obj):
        """Retourne le nombre total de tickets créés aujourd'hui"""
        today = timezone.now().date()
        return obj.tickets.filter(date_emission__date=today).count()
    
    def get_distance(self, obj):
        """Calcule la distance si les coordonnées du client sont fournies dans le contexte"""
        request = self.context.get('request')
        if request and hasattr(request, 'client_lat') and hasattr(request, 'client_lng'):
            return self.calculate_distance(
                float(request.client_lat), float(request.client_lng),
                float(obj.latitude), float(obj.longitude)
            )
        return None
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calcule la distance entre deux points géographiques (formule de Haversine)"""
        # Rayon de la Terre en kilomètres
        R = 6371.0
        
        # Conversion en radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Différences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Formule de Haversine
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return round(distance, 2)


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle Notification"""
    ticket_numero = serializers.CharField(source='ticket.numero_ticket', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id_notification', 'message', 'type_notification', 
            'date_envoi', 'date_lecture', 'statut', 'ticket', 'ticket_numero'
        ]
        read_only_fields = ['id_notification', 'date_envoi', 'ticket_numero']


class TicketSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle Ticket"""
    client_info = ClientSerializer(source='client', read_only=True)
    agent_info = AgentSerializer(source='agent', read_only=True)
    agence_info = AgenceSerializer(source='agence', read_only=True)
    notifications = NotificationSerializer(many=True, read_only=True)
    temps_attente = serializers.SerializerMethodField()
    position_file = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = [
            'id_ticket', 'numero_ticket', 'type_reservation', 
            'date_emission', 'date_appel', 'date_fin', 'etat',
            'client', 'agent', 'agence',
            'client_info', 'agent_info', 'agence_info', 'notifications',
            'temps_attente', 'position_file'
        ]
        read_only_fields = [
            'id_ticket', 'numero_ticket', 'date_emission', 'date_appel', 'date_fin',
            'client_info', 'agent_info', 'agence_info', 'notifications',
            'temps_attente', 'position_file'
        ]
    
    def get_temps_attente(self, obj):
        """Calcule le temps d'attente du ticket"""
        if obj.etat == 'en_attente':
            delta = timezone.now() - obj.date_emission
            return int(delta.total_seconds() / 60)  # en minutes
        elif obj.date_appel:
            delta = obj.date_appel - obj.date_emission
            return int(delta.total_seconds() / 60)  # en minutes
        return None
    
    def get_position_file(self, obj):
        """Retourne la position du ticket dans la file d'attente"""
        if obj.etat == 'en_attente':
            return Ticket.objects.filter(
                agence=obj.agence,
                etat='en_attente',
                date_emission__lt=obj.date_emission
            ).count() + 1
        return None


class TicketReservationSerializer(TicketSerializer):
    """Serializer spécialisé pour la réservation de tickets"""
    client_latitude = serializers.DecimalField(max_digits=10, decimal_places=8, write_only=True)
    client_longitude = serializers.DecimalField(max_digits=11, decimal_places=8, write_only=True)
    agence_la_plus_proche = AgenceSerializer(read_only=True)
    
    class Meta(TicketSerializer.Meta):
        fields = [
            'id_ticket', 'numero_ticket', 'type_reservation', 'date_emission', 'etat',
            'client_latitude', 'client_longitude', 'agence', 'agence_la_plus_proche',
            'client_info', 'agent_info', 'agence_info', 'notifications',
            'temps_attente', 'position_file'
        ]
        read_only_fields = [
            'id_ticket', 'numero_ticket', 'date_emission', 'date_appel', 'date_fin',
            'client_info', 'agent_info', 'agence_info', 'notifications',
            'temps_attente', 'position_file', 'agence_la_plus_proche'
        ]
        extra_kwargs = {
            'agence': {'required': False}  # Rendre le champ agence optionnel
        }
    
    def create(self, validated_data):
        """Création d'un ticket avec recherche automatique de l'agence la plus proche"""
        client_lat = validated_data.pop('client_latitude')
        client_lng = validated_data.pop('client_longitude')
        
        # Créer ou récupérer le client
        client, created = Client.objects.get_or_create(
            latitude=client_lat,
            longitude=client_lng
        )
        
        # Trouver l'agence la plus proche
        agence_la_plus_proche = self.find_nearest_agency(float(client_lat), float(client_lng))
        
        if not agence_la_plus_proche:
            raise serializers.ValidationError("Aucune agence active n'a été trouvée à proximité.")
        
        # Créer le ticket
        ticket = Ticket.objects.create(
            client=client,
            agence=agence_la_plus_proche,
            type_reservation=validated_data.get('type_reservation', 'normal')
        )
        
        return ticket
    
    def find_nearest_agency(self, client_lat, client_lng):
        """Trouve l'agence la plus proche du client"""
        agences = Agence.objects.filter(is_active=True)
        nearest_agency = None
        min_distance = float('inf')
        
        for agence in agences:
            distance = AgenceSerializer.calculate_distance(
                client_lat, client_lng,
                float(agence.latitude), float(agence.longitude)
            )
            if distance < min_distance:
                min_distance = distance
                nearest_agency = agence
        
        return nearest_agency


class FileAttenteSerializer(serializers.Serializer):
    """Serializer pour afficher la file d'attente d'une agence"""
    agence = AgenceSerializer(read_only=True)
    tickets_en_attente = TicketSerializer(many=True, read_only=True)
    nombre_tickets_en_attente = serializers.IntegerField(read_only=True)
    temps_attente_moyen = serializers.IntegerField(read_only=True, help_text="Temps d'attente moyen en minutes")
    dernier_ticket_appele = TicketSerializer(read_only=True)


class StatistiquesSerializer(serializers.Serializer):
    """Serializer pour les statistiques générales"""
    total_tickets_aujourd_hui = serializers.IntegerField()
    total_tickets_en_attente = serializers.IntegerField()
    total_tickets_termines_aujourd_hui = serializers.IntegerField()
    temps_attente_moyen = serializers.FloatField(help_text="Temps d'attente moyen en minutes")
    repartition_par_type = serializers.DictField()
    repartition_par_agence = serializers.DictField()
    tickets_par_heure = serializers.DictField()


class ConfigurationDistributionSerializer(serializers.ModelSerializer):
    """Serializer pour la configuration de distribution automatique"""
    agence_nom = serializers.CharField(source='agence.nom_agence', read_only=True)
    
    class Meta:
        model = ConfigurationDistribution
        fields = [
            'agence', 'agence_nom', 'is_active', 'intervalle_minutes', 
            'derniere_execution', 'date_creation', 'date_modification'
        ]
        read_only_fields = ['derniere_execution', 'date_creation', 'date_modification', 'agence_nom']


class AppelTicketSerializer(serializers.Serializer):
    """Serializer pour l'appel d'un ticket par un agent"""
    ticket_id = serializers.UUIDField()
    agent_id = serializers.UUIDField()
    message_notification = serializers.CharField(required=False, allow_blank=True)
    
    def validate_ticket_id(self, value):
        """Valide que le ticket existe et peut être appelé"""
        try:
            ticket = Ticket.objects.get(id_ticket=value)
            if ticket.etat != 'en_attente':
                raise serializers.ValidationError("Ce ticket n'est pas en attente.")
            return value
        except Ticket.DoesNotExist:
            raise serializers.ValidationError("Ticket introuvable.")
    
    def validate_agent_id(self, value):
        """Valide que l'agent existe et est actif"""
        try:
            agent = Agent.objects.get(id=value)
            if not agent.is_active:
                raise serializers.ValidationError("Cet agent n'est pas actif.")
            return value
        except Agent.DoesNotExist:
            raise serializers.ValidationError("Agent introuvable.")