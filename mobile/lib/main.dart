// main.dart
// Nécessite d'ajouter http: ^0.13.6 dans pubspec.yaml
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:geolocator/geolocator.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Tickets Agent',
      theme: ThemeData(primarySwatch: Colors.blue, useMaterial3: true),
      // Affiche la page de création de ticket (état initial)
      home: const CreateTicketPage(),
    );
  }
}

class CreateTicketPage extends StatefulWidget {
  const CreateTicketPage({super.key});

  @override
  State<CreateTicketPage> createState() => _CreateTicketPageState();
}

class _CreateTicketPageState extends State<CreateTicketPage> {
  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }

  Future<void> _getCurrentLocation() async {
    setState(() {
      isLocating = true;
      locationStatus = "Localisation en cours...";
    });

    try {
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          setState(() {
            locationStatus = "Accès à la localisation refusé";
            isLocating = false;
          });
          return;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        setState(() {
          locationStatus = "La géolocalisation est désactivée";
          isLocating = false;
        });
        return;
      }

      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );

      setState(() {
        currentPosition = position;
        locationStatus = "Position détectée";
        isLocating = false;
      });
    } catch (e) {
      setState(() {
        locationStatus = "Erreur lors de la localisation: $e";
        isLocating = false;
      });
    }
  }

  Future<void> _createTicket() async {
    if (!_formKey.currentState!.validate()) return;
    if (currentPosition == null) {
      _showMessage("Veuillez attendre que votre position soit détectée", false);
      return;
    }

    setState(() {
      isLoading = true;
    });

    try {
      final url = Uri.parse(
        'http://192.168.1.69:8000/api/client/reserver-ticket/',
      );

      // Formater les coordonnées avec 8 décimales comme dans le HTML
      final formattedLatitude = currentPosition!.latitude.toStringAsFixed(8);
      final formattedLongitude = currentPosition!.longitude.toStringAsFixed(8);

      final body = {
        "agence_id": selectedAgence,
        "type_reservation": selectedTypeReservation!,
        "client_latitude": formattedLatitude,
        "client_longitude": formattedLongitude,
      };

      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode(body),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200 || response.statusCode == 201) {
        _showMessage("Ticket créé avec succès !", true);
        // Réinitialiser le formulaire
        setState(() {
          selectedTypeReservation = null;
        });
        _formKey.currentState!.reset();
      } else {
        _showMessage(
          data['error'] ??
              data['message'] ??
              'Erreur lors de la création du ticket',
          false,
        );
      }
    } catch (e) {
      _showMessage("Erreur réseau: $e", false);
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  void _showMessage(String message, bool isSuccess) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isSuccess ? Colors.green : Colors.red,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  final _formKey = GlobalKey<FormState>();

  // Agence pré-sélectionnée (Direction Générale ONEA)
  String selectedAgence = "507ffe5a-5c5c-4c8e-875a-be4ea6096c50";
  String? selectedTypeReservation;
  Position? currentPosition;
  bool isLoading = false;
  bool isLocating = false;
  String locationStatus = "En attente de localisation...";

  final List<Map<String, String>> typeReservations = [
    {"value": "RECLAMATION", "label": "Réclamation"},
    {"value": "DEMANDE_INFO", "label": "Demande d'information"},
    {"value": "DEMANDE_BRANCHEMENT", "label": "Demande de branchement"},
    {"value": "FACTURE", "label": "Problème de facturation"},
    {"value": "PANNE", "label": "Signalement de panne"},
    {"value": "AUTRE", "label": "Autre"},
  ];

  @override
  Widget build(BuildContext context) {
    // Préparation des textes dynamiques pour l'affichage
    String latitudeText = '';
    String longitudeText = '';
    String typeReservationLabel = '';
    if (currentPosition != null) {
      latitudeText =
          'Latitude: ${currentPosition!.latitude.toStringAsFixed(6)}';
      longitudeText =
          'Longitude: ${currentPosition!.longitude.toStringAsFixed(6)}';
    }
    if (selectedTypeReservation != null) {
      typeReservationLabel =
          typeReservations.firstWhere(
            (t) => t['value'] == selectedTypeReservation,
          )['label'] ??
          '';
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Créer un nouveau ticket'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        elevation: 2,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(12.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Card(
                elevation: 6,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.account_balance, color: Colors.blue),
                          const SizedBox(width: 8),
                          const Text(
                            'Agence',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.blue.shade50,
                          border: Border.all(color: Colors.blue.shade100),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Text(
                          'Direction Générale ONEA',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                      const SizedBox(height: 20),

                      Row(
                        children: [
                          const Icon(Icons.category, color: Colors.blue),
                          const SizedBox(width: 8),
                          const Text(
                            'Type de réservation',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      DropdownButtonFormField<String>(
                        value: selectedTypeReservation,
                        decoration: InputDecoration(
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          prefixIcon: const Icon(Icons.list_alt),
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 8,
                          ),
                        ),
                        hint: const Text('Sélectionnez un type'),
                        items:
                            typeReservations.map((type) {
                              return DropdownMenuItem<String>(
                                value: type['value'],
                                child: Text(type['label']!),
                              );
                            }).toList(),
                        onChanged: (value) {
                          setState(() {
                            selectedTypeReservation = value;
                          });
                        },
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Veuillez sélectionner un type de réservation';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 20),

                      Row(
                        children: [
                          const Icon(Icons.location_on, color: Colors.blue),
                          const SizedBox(width: 8),
                          const Text(
                            'Position actuelle',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 6,
                            ),
                            decoration: BoxDecoration(
                              color:
                                  isLocating
                                      ? Colors.blue
                                      : currentPosition != null
                                      ? Colors.green
                                      : Colors.red,
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: Row(
                              children: [
                                Icon(
                                  isLocating
                                      ? Icons.sync
                                      : currentPosition != null
                                      ? Icons.check_circle
                                      : Icons.error,
                                  color: Colors.white,
                                  size: 16,
                                ),
                                const SizedBox(width: 6),
                                Text(
                                  locationStatus,
                                  style: const TextStyle(color: Colors.white),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 8),
                          if (isLocating)
                            const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Nous avons besoin de votre position pour vous diriger vers l\'agence la plus proche.',
                        style: TextStyle(color: Colors.grey, fontSize: 12),
                      ),
                      if (currentPosition != null) ...[
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            const Icon(
                              Icons.my_location,
                              size: 16,
                              color: Colors.blueGrey,
                            ),
                            const SizedBox(width: 4),
                            Text(
                              latitudeText,
                              style: const TextStyle(fontSize: 12),
                            ),
                            const SizedBox(width: 12),
                            Text(
                              longitudeText,
                              style: const TextStyle(fontSize: 12),
                            ),
                          ],
                        ),
                      ],
                      const SizedBox(height: 20),

                      // Résumé du ticket avant validation
                      if (selectedTypeReservation != null &&
                          currentPosition != null) ...[
                        Container(
                          width: double.infinity,
                          margin: const EdgeInsets.only(bottom: 16),
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: Colors.blue.shade50,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: Colors.blue.shade100),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  const Icon(
                                    Icons.info_outline,
                                    color: Colors.blue,
                                  ),
                                  const SizedBox(width: 6),
                                  Text(
                                    'Résumé du ticket',
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      color: Colors.blue.shade700,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text('Type : $typeReservationLabel'),
                              Text(
                                latitudeText.replaceFirst(
                                  'Latitude: ',
                                  'Latitude : ',
                                ),
                              ),
                              Text(
                                longitudeText.replaceFirst(
                                  'Longitude: ',
                                  'Longitude : ',
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],

                      // Bouton de création
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed:
                              (currentPosition != null &&
                                      selectedTypeReservation != null &&
                                      !isLoading)
                                  ? _createTicket
                                  : null,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.blue.shade700,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 18),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            elevation: 2,
                            textStyle: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          child:
                              isLoading
                                  ? const SizedBox(
                                    height: 24,
                                    width: 24,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2.5,
                                      valueColor: AlwaysStoppedAnimation<Color>(
                                        Colors.white,
                                      ),
                                    ),
                                  )
                                  : const Text('Créer le ticket'),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
    // ...existing code...
  }
}
