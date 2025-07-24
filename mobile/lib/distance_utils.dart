// distance_utils.dart
// Utilitaire pour calculer la distance entre deux points GPS (en km)
import 'dart:math';

double calculateDistance(double lat1, double lon1, double lat2, double lon2) {
  const R = 6371; // Rayon de la Terre en km
  double dLat = (lat2 - lat1) * pi / 180;
  double dLon = (lon2 - lon1) * pi / 180;
  double a =
      sin(dLat / 2) * sin(dLat / 2) +
      cos(lat1 * pi / 180) *
          cos(lat2 * pi / 180) *
          sin(dLon / 2) *
          sin(dLon / 2);
  double c = 2 * atan2(sqrt(a), sqrt(1 - a));
  return R * c;
}
