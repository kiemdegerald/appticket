# API Endpoints – Application Mobile

Ce document liste les principaux endpoints de l’API pour permettre à un développeur mobile de communiquer avec le backend.

---

## 1. Authentification (si existant)

**POST** `/api/auth/login/`

- **Body JSON** :
```json
{
  "username": "string",
  "password": "string"
}
```
- **Réponse (succès)** :
```json
{
  "token": "jwt-token",
  "user": { ... }
}
```
- **Description** : Authentifie un utilisateur et retourne un token à utiliser dans les headers `Authorization` pour les autres requêtes.

---

## 2. Réserver un ticket

**POST** `/api/agent/reserver-ticket/`

- **Body JSON** :
```json
{
  "type_reservation": "RECLAMATION | DEMANDE_INFO | DEMANDE_BRANCHEMENT | FACTURE | PANNE | AUTRE",
  "client_nom": "string",
  "client_telephone": "string",
  "client_latitude": 48.8566,
  "client_longitude": 2.3522
}
```
- **Réponse (succès)** :
```json
{
  "success": true,
  "ticket": {
    "id_ticket": "uuid",
    "numero_ticket": "A123",
    "etat": "en_attente",
    ...
  }
}
```
- **Description** : Permet à un utilisateur de réserver un ticket.

---

## 3. Voir les tickets de l’utilisateur

**GET** `/api/agent/tickets-utilisateur/<telephone>/`

- **Paramètre URL** : `telephone` (numéro de téléphone du client)
- **Réponse** :
```json
[
  {
    "id_ticket": "uuid",
    "numero_ticket": "A123",
    "etat": "en_attente",
    ...
  },
  ...
]
```
- **Description** : Liste tous les tickets réservés par un utilisateur donné.

---

## 4. Voir le détail d’un ticket

**GET** `/api/agent/ticket/<id_ticket>/`

- **Paramètre URL** : `id_ticket` (UUID du ticket)
- **Réponse** :
```json
{
  "id_ticket": "uuid",
  "numero_ticket": "A123",
  "etat": "en_attente",
  ...
}
```
- **Description** : Récupère le détail d’un ticket spécifique.

---

## 5. Annuler un ticket

**POST** `/api/agent/annuler-ticket/`

- **Body JSON** :
```json
{
  "id_ticket": "uuid"
}
```
- **Réponse** :
```json
{
  "success": true,
  "message": "Ticket annulé"
}
```
- **Description** : Permet à l’utilisateur d’annuler un ticket réservé.

---

## 6. (Optionnel) Voir les types de tickets disponibles

**GET** `/api/agent/types-tickets/`

- **Réponse** :
```json
[
  "RECLAMATION",
  "DEMANDE_INFO",
  "DEMANDE_BRANCHEMENT",
  "FACTURE",
  "PANNE",
  "AUTRE"
]
```
- **Description** : Liste les types de tickets que l’utilisateur peut réserver.

---

## 7. (Optionnel) Voir les agences disponibles

**GET** `/api/agences/`

- **Réponse** :
```json
[
  {
    "id": "uuid",
    "nom": "Agence Paris",
    ...
  },
  ...
]
```
- **Description** : Liste les agences où l’utilisateur peut réserver un ticket.

---

**Remarques :**
- Tous les endpoints commençant par `/api/` doivent être précédés de l’URL de base de ton serveur (ex: `https://monapi.exemple.com/api/...`)
- Si l’authentification est requise, ajouter le header :
  `Authorization: Bearer <token>`
- Adapter les chemins selon la configuration réelle de ton API.

---

**Contact** : Pour toute question sur l’API, contacter l’équipe backend. 