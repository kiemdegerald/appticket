# models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid


class Client(models.Model):
    """Modèle pour les clients"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, help_text="Latitude de la position du client")
    longitude = models.DecimalField(max_digits=11, decimal_places=8, help_text="Longitude de la position du client")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'clients'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
    
    def __str__(self):
        return f"Client {self.id}"


class Agent(models.Model):
    """Modèle pour les agents"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'agents'
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Administrateur(models.Model):
    """Modèle pour les administrateurs"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'administrateurs'
        verbose_name = 'Administrateur'
        verbose_name_plural = 'Administrateurs'
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Agence(models.Model):
    """Modèle pour les agences"""
    id_agence = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom_agence = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, help_text="Latitude de l'agence")
    longitude = models.DecimalField(max_digits=11, decimal_places=8, help_text="Longitude de l'agence")
    adresse = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'agences'
        verbose_name = 'Agence'
        verbose_name_plural = 'Agences'
    
    def __str__(self):
        return self.nom_agence


class Ticket(models.Model):
    """Modèle pour les tickets"""
    
    TYPE_RESERVATION_CHOICES = [
        ('RECLAMATION', 'Réclamation'),
        ('DEMANDE_INFO', 'Demande d\'information'),
        ('DEMANDE_BRANCHEMENT', 'Demande de branchement'),
        ('FACTURE', 'Problème de facturation'),
        ('PANNE', 'Signalement de panne'),
        ('AUTRE', 'Autre'),
    ]
    
    ETAT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
        ('expire', 'Expiré'),
    ]
    
    id_ticket = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_ticket = models.CharField(max_length=20, unique=True, help_text="Numéro de ticket affiché au client")
    type_reservation = models.CharField(max_length=20, choices=TYPE_RESERVATION_CHOICES, default='normal')
    date_emission = models.DateTimeField(auto_now_add=True)
    date_appel = models.DateTimeField(null=True, blank=True, help_text="Date d'appel du ticket par l'agent")
    date_fin = models.DateTimeField(null=True, blank=True, help_text="Date de fin de traitement du ticket")
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='en_attente')
    
    # Relations
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='tickets')
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name='tickets')
    
    class Meta:
        db_table = 'tickets'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['date_emission']
        indexes = [
            models.Index(fields=['etat', 'agence']),
            models.Index(fields=['date_emission']),
            models.Index(fields=['numero_ticket']),
        ]
    
    def __str__(self):
        return f"Ticket {self.numero_ticket} - {self.get_etat_display()}"
    
    def save(self, *args, **kwargs):
        """Génère automatiquement le numéro de ticket s'il n'existe pas"""
        if not self.numero_ticket:
            # Générer un numéro de ticket basé sur l'agence et la date
            today = timezone.now().strftime('%Y%m%d')
            # Trouver le dernier numéro de ticket pour aujourd'hui
            last_ticket = Ticket.objects.filter(
                numero_ticket__startswith=f"{self.agence.nom_agence[:3].upper()}-{today}-"
            ).order_by('-numero_ticket').first()
            
            if last_ticket:
                # Extraire le numéro et l'incrémenter
                last_number = int(last_ticket.numero_ticket.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
                
            self.numero_ticket = f"{self.agence.nom_agence[:3].upper()}-{today}-{new_number:04d}"
        
        super().save(*args, **kwargs)


class Notification(models.Model):
    """Modèle pour les notifications"""
    
    TYPE_NOTIFICATION_CHOICES = [
        ('appel', 'Appel de ticket'),
        ('information', 'Information'),
        ('rappel', 'Rappel'),
        ('annulation', 'Annulation'),
    ]
    
    STATUT_CHOICES = [
        ('envoye', 'Envoyé'),
        ('lu', 'Lu'),
        ('non_envoye', 'Non envoyé'),
    ]
    
    id_notification = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.TextField()
    type_notification = models.CharField(max_length=20, choices=TYPE_NOTIFICATION_CHOICES, default='information')
    date_envoi = models.DateTimeField(auto_now_add=True)
    date_lecture = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='envoye')
    
    # Relations
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='notifications')
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-date_envoi']
    
    def __str__(self):
        return f"Notification pour {self.ticket.numero_ticket}"


class ConfigurationDistribution(models.Model):
    """Modèle pour la configuration de la distribution automatique des tickets"""
    agence = models.OneToOneField(Agence, on_delete=models.CASCADE, related_name='configuration_distribution')
    is_active = models.BooleanField(default=False, help_text="Distribution automatique activée")
    intervalle_minutes = models.IntegerField(default=5, help_text="Intervalle en minutes entre les appels automatiques")
    derniere_execution = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'configuration_distribution'
        verbose_name = 'Configuration Distribution'
        verbose_name_plural = 'Configurations Distribution'
    
    def __str__(self):
        return f"Distribution {self.agence.nom_agence} - {'Activée' if self.is_active else 'Désactivée'}"