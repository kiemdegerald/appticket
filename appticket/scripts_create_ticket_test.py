from appticket.models import Agence, Client, Ticket
from django.utils import timezone

# ID de l'agence utilisée dans le dashboard agent
AGENCE_ID = '2c8ee4e2-ad2d-4845-b9e5-aa9b46b3c2e1'

try:
    agence = Agence.objects.get(id_agence=AGENCE_ID)
except Agence.DoesNotExist:
    print(f"Aucune agence trouvée avec l'ID {AGENCE_ID}")
    exit(1)

# Créer un client fictif
client = Client.objects.create(latitude=12.34, longitude=-1.56)

# Créer un ticket en attente
now = timezone.now()
ticket = Ticket.objects.create(
    type_reservation='normal',
    client=client,
    agence=agence,
    etat='en_attente',
    date_emission=now
)

print(f"Ticket créé : {ticket.numero_ticket} (ID: {ticket.id_ticket}) pour l'agence {agence.nom_agence}") 