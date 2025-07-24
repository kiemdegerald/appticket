// agent_ticket_list.dart
// Exemple de liste de tickets côté agent avec bouton pour voir la distance agence-client

import 'package:flutter/material.dart';
import 'distance_utils.dart';

class Ticket {
  final String id;
  final String clientName;
  final double clientLatitude;
  final double clientLongitude;

  Ticket({
    required this.id,
    required this.clientName,
    required this.clientLatitude,
    required this.clientLongitude,
  });
}

class AgentTicketListPage extends StatelessWidget {
  AgentTicketListPage({super.key});

  // Exemple de tickets (à remplacer par les données de l'API)
  final List<Ticket> tickets = [
    Ticket(
      id: '1',
      clientName: 'Client A',
      clientLatitude: 12.4000,
      clientLongitude: -1.5000,
    ),
    Ticket(
      id: '2',
      clientName: 'Client B',
      clientLatitude: 12.3500,
      clientLongitude: -1.5300,
    ),
  ];

  // Coordonnées fixes de l'agence principale
  final double agenceLat = 12.3703;
  final double agenceLon = -1.5247;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Tickets des clients')),
      body: ListView.builder(
        itemCount: tickets.length,
        itemBuilder: (context, index) {
          final ticket = tickets[index];
          return Card(
            margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: ListTile(
              title: Text(ticket.clientName),
              subtitle: Text(
                'Lat: ${ticket.clientLatitude}, Lon: ${ticket.clientLongitude}',
              ),
              trailing: ElevatedButton(
                onPressed: () {
                  double distance = calculateDistance(
                    agenceLat,
                    agenceLon,
                    ticket.clientLatitude,
                    ticket.clientLongitude,
                  );
                  showDialog(
                    context: context,
                    builder:
                        (_) => AlertDialog(
                          title: const Text('Distance réelle'),
                          content: Text(
                            'Distance agence-client : ${distance.toStringAsFixed(2)} km',
                          ),
                        ),
                  );
                },
                child: const Text('Voir la distance'),
              ),
            ),
          );
        },
      ),
    );
  }
}
