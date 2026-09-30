TaskFlow - Déploiement Kubernetes
1. Présentation
TaskFlow est une application web permettant de créer et consulter des tâches.
Une tâche contient :
- un nom ;
- une adresse e-mail ;
- un titre ;
- une description.
L'application est composée de trois parties :
- un Frontend Web ;
- une API REST ;
- une base de données PostgreSQL.
L'objectif du projet est de déployer cette application dans Kubernetes avec Minikube et Docker.
2. Architecture de l'application
Architecture fonctionnelle :
Utilisateur
   ↓
Frontend
   ↓ HTTP
API REST
   ↓ SQL
PostgreSQL
   ↓
PVC
Architecture Kubernetes :
Namespace taskflow
│
├── Deployment frontend
│   ├── Pod frontend 1
│   └── Pod frontend 2
│
├── Service frontend
│
├── Deployment api
│   ├── Pod api 1
│   └── Pod api 2
│
├── Service api
│
├── Deployment postgres
│   └── Pod PostgreSQL
│
├── Service postgres
│
├── ConfigMap postgres-config
├── Secret postgres-secret
└── PVC postgres-pvc
3. Technologies utilisées
- Kubernetes
- Minikube
- Docker
- kubectl
- PostgreSQL
- FastAPI
- Uvicorn
- Nginx
- HTML
- JavaScript
4. Organisation du projet
taskflow-k8s/
│
├── postgres/
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── pvc.yaml
│   ├── deployment.yaml
│   └── service.yaml
│
├── api/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── deployment.yaml
│   └── service.yaml
│
└── frontend/
    ├── index.html
    ├── app.js
    ├── nginx.conf
    ├── Dockerfile
    ├── deployment.yaml
    └── service.yaml
5. Namespace
Un namespace nommé taskflow a été créé afin d'isoler les ressources Kubernetes de l'application.
kubectl create namespace taskflow
kubectl config set-context --current --namespace=taskflow
kubectl get namespaces
6. PostgreSQL
PostgreSQL constitue la base de données de l'application.
Configuration :
Base : taskflow
Utilisateur : taskflow
Port : 5432
Les ressources Kubernetes créées pour PostgreSQL sont :
- ConfigMap ;
- Secret ;
- PersistentVolumeClaim ;
- Deployment ;
- Service.
ConfigMap
La ConfigMap contient les paramètres non sensibles :
POSTGRES_DB
POSTGRES_USER
Vérification :
kubectl get configmaps
Secret
Le Secret contient le mot de passe PostgreSQL.
Vérification :
kubectl get secrets
PersistentVolumeClaim
Un PVC de 1 Gi a été créé afin de conserver les données PostgreSQL même si le Pod est supprimé.
kubectl get pvc
Le PVC doit être dans l'état :
Bound
Deployment PostgreSQL
PostgreSQL est déployé avec un seul replica.
kubectl get deployments
kubectl get pods
Le Pod PostgreSQL doit être :
Running
Service PostgreSQL
Le Service PostgreSQL est de type :
ClusterIP
L'API utilise le nom du Service :
postgres
et non l'adresse IP du Pod.
kubectl get svc
kubectl get endpointslices
7. API REST
L'API TaskFlow a été développée avec FastAPI.
Image Docker :
taskflow-api:1.0
Port :
8000
Endpoints principaux :
GET  /api/tasks
POST /api/tasks
Exemple de tâche :
{
  "name": "Alice",
  "email": "alice@example.com",
  "title": "Installer Kubernetes",
  "description": "Creer mon premier Deployment"
}
Construction de l'image
docker build -t taskflow-api:1.0 .
minikube image load taskflow-api:1.0
Communication avec PostgreSQL
L'API utilise :
POSTGRES_HOST=postgres
Elle récupère le nom de la base et l'utilisateur depuis la ConfigMap, ainsi que le mot de passe depuis le Secret.
Service API
Le Service API est de type :
ClusterIP
Il expose le port :
8000
Vérification :
kubectl get pods -l app=api
kubectl get svc
kubectl logs NOM_DU_POD_API
8. Tests de l'API
Un port-forward a été utilisé pour tester l'API depuis Windows :
kubectl port-forward service/api 18000:8000
Test GET :
Invoke-RestMethod -Uri "http://localhost:18000/api/tasks"
Test POST :
$body = @{
    name = "Alice"
    email = "alice@example.com"
    title = "Installer Kubernetes"
    description = "Creer mon premier Deployment"
} | ConvertTo-Json

$utf8Body = [System.Text.Encoding]::UTF8.GetBytes($body)

Invoke-RestMethod `
    -Uri "http://localhost:18000/api/tasks" `
    -Method Post `
    -ContentType "application/json; charset=utf-8" `
    -Body $utf8Body
Cela confirme la chaîne :
Client
   ↓
Service API
   ↓
Pod FastAPI
   ↓
Service PostgreSQL
   ↓
Pod PostgreSQL
   ↓
PVC
9. Frontend
Le Frontend TaskFlow contient un formulaire permettant de saisir :
- Nom ;
- Email ;
- Titre ;
- Description.
Le frontend est servi par Nginx.
Image Docker :
taskflow-frontend:1.0
Construction de l'image
docker build -t taskflow-frontend:1.0 .
minikube image load taskflow-frontend:1.0
Deployment Frontend
Le frontend utilise plusieurs replicas :
2 replicas
Service Frontend
Le Service Frontend est de type :
NodePort
Il permet l'accès depuis l'extérieur du cluster Minikube.
minikube service frontend -n taskflow --url
10. Test réel depuis le navigateur
Le frontend a été ouvert dans le navigateur.
Une tâche a été créée depuis le formulaire, envoyée à l'API, puis enregistrée dans PostgreSQL.
Chaîne complète :
Navigateur
   ↓
Frontend
   ↓
Nginx
   ↓
Service API
   ↓
Pod FastAPI
   ↓
Service PostgreSQL
   ↓
Pod PostgreSQL
   ↓
PVC
11. Résilience Kubernetes
Suppression d'un Pod Frontend
kubectl get pods -l app=frontend
kubectl delete pod NOM_DU_POD
kubectl get pods -w
Kubernetes recrée automatiquement un nouveau Pod afin de conserver le nombre de replicas demandé.
Suppression d'un Pod API
La même expérience a été réalisée avec l'API.
12. Scaling
Frontend
Passage à 3 replicas :
kubectl scale deployment frontend --replicas=3
kubectl get pods -l app=frontend
Retour à 2 replicas :
kubectl scale deployment frontend --replicas=2
API
kubectl scale deployment api --replicas=2
kubectl get pods -l app=api
Le Service API continue de fonctionner sans modification car il sélectionne tous les Pods avec le label app=api.
13. Rolling Update
Une nouvelle version du frontend a été créée, par exemple :
taskflow-frontend:1.1
Construction et chargement :
docker build -t taskflow-frontend:1.1 .
minikube image load taskflow-frontend:1.1
Suivi du déploiement :
kubectl rollout status deployment/frontend
kubectl get pods -w
kubectl rollout history deployment/frontend
Le Rolling Update permet de remplacer progressivement les anciens Pods par les nouveaux sans arrêter complètement l'application.
14. Rollback
Un rollback a été réalisé avec :
kubectl rollout undo deployment/frontend
Puis :
kubectl rollout status deployment/frontend
kubectl rollout history deployment/frontend
Le rollback permet de revenir rapidement à une version précédente lorsqu'une nouvelle version présente un problème.
15. Diagnostic ImagePullBackOff
Une image incorrecte a volontairement été configurée dans le Deployment Frontend.
Exemple :
taskflow-frontend:9.9
Les états observés peuvent être :
ErrImagePull
ImagePullBackOff
Commandes de diagnostic :
kubectl get pods
kubectl describe pod NOM_DU_POD
kubectl get events --sort-by=.lastTimestamp
kubectl logs NOM_DU_POD
La correction consiste à remettre une image existante puis à réappliquer le Deployment.
16. Diagnostic du Service
Un mauvais selector a été testé dans le Service Frontend.
Selector correct :
selector:
  app: frontend
Commandes de diagnostic :
kubectl get svc
kubectl describe svc frontend
kubectl get endpointslices
kubectl get pods --show-labels
Le selector du Service doit correspondre aux labels des Pods.
17. Commandes principales
Cluster
minikube status
kubectl get nodes
kubectl cluster-info
Namespace
kubectl get namespaces
kubectl config current-context
Pods
kubectl get pods
kubectl get pods -w
kubectl get pods --show-labels
kubectl get pods -o wide
Deployments
kubectl get deployments
kubectl scale deployment frontend --replicas=3
kubectl scale deployment api --replicas=2
Services
kubectl get svc
kubectl describe svc frontend
kubectl get endpointslices
Stockage
kubectl get pvc
kubectl get pv
kubectl get storageclass
Configuration
kubectl get configmaps
kubectl get secrets
Logs et diagnostic
kubectl logs NOM_DU_POD
kubectl describe pod NOM_DU_POD
kubectl get events --sort-by=.lastTimestamp
Déploiement
kubectl apply -f fichier.yaml
kubectl delete -f fichier.yaml
Rolling Update
kubectl rollout status deployment/frontend
kubectl rollout history deployment/frontend
Rollback
kubectl rollout undo deployment/frontend
Accès Frontend
minikube service frontend -n taskflow --url
Accès API
kubectl port-forward service/api 18000:8000
18. Problèmes rencontrés et solutions
Image Docker non disponible dans Minikube
Erreur :
ErrImagePull
Solution :
minikube image load taskflow-frontend:1.0
minikube image load taskflow-api:1.0
Mauvais namespace avec Minikube
Commande initiale :
minikube service frontend --url
Erreur : le Service était recherché dans le namespace default.
Solution :
minikube service frontend -n taskflow --url
JSON mal interprété sous PowerShell
Solution :
$body = @{
    name = "Alice"
    email = "alice@example.com"
    title = "Installer Kubernetes"
    description = "Creer mon premier Deployment"
} | ConvertTo-Json

$utf8Body = [System.Text.Encoding]::UTF8.GetBytes($body)

Invoke-RestMethod `
    -Uri "http://localhost:18000/api/tasks" `
    -Method Post `
    -ContentType "application/json; charset=utf-8" `
    -Body $utf8Body
YAML exécuté dans PowerShell
Les lignes YAML comme apiVersion, kind, metadata ne sont pas des commandes PowerShell.
Il faut créer un fichier :
code deployment.yaml
puis y coller le YAML avant d'utiliser :
kubectl apply -f deployment.yaml
19. Validation finale
L'application est considérée comme fonctionnelle car :
- le Node Minikube est Ready ;
- le namespace taskflow existe ;
- PostgreSQL est Running ;
- le PVC est Bound ;
- la ConfigMap existe ;
- le Secret existe ;
- les Services Frontend, API et PostgreSQL existent ;
- le Frontend est accessible depuis le navigateur ;
- le formulaire permet de créer une tâche ;
- l'API reçoit la requête ;
- PostgreSQL conserve les données ;
- Kubernetes recrée automatiquement les Pods supprimés ;
- le scaling fonctionne ;
- le Rolling Update fonctionne ;
- le rollback fonctionne ;
- les erreurs de type ImagePullBackOff peuvent être diagnostiquées.
20. Schéma final
                        KUBERNETES
                            │
                    Namespace taskflow
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
       ▼                    ▼                    ▼
   FRONTEND                API              POSTGRESQL
       │                    │                    │
   Deployment           Deployment           Deployment
       │                    │                    │
  ReplicaSet            ReplicaSet           ReplicaSet
       │                    │                    │
  ┌────┴────┐          ┌────┴────┐              │
  ▼         ▼          ▼         ▼              ▼
Pod F1    Pod F2     Pod API1  Pod API2      Pod PostgreSQL
  │         │          │         │              │
  └────┬────┘          └────┬────┘              │
       │                    │                    │
       ▼                    ▼                    ▼
Service Frontend       Service API       Service PostgreSQL
 NodePort               ClusterIP            ClusterIP
       │                    │                    │
       │                    │                    ▼
       │                    │                   PVC
       │                    │                    │
       ▼                    ▼                    ▼
Utilisateur           API REST             Données
21. Conclusion
Ce projet a permis de déployer une application complète dans Kubernetes.
Kubernetes gère :
- la configuration ;
- les données sensibles ;
- le stockage persistant ;
- le réseau ;
- les Services ;
- la résilience ;
- le scaling ;
- les mises à jour progressives ;
- les rollbacks ;
- le diagnostic des erreurs.
Architecture finale :
Utilisateur
   ↓
Frontend
   ↓
API
   ↓
PostgreSQL
   ↓
PVC
L'ensemble est orchestré par Kubernetes dans le namespace taskflow.