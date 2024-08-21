from django.utils import timezone
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError, AuthenticationFailed
from django.http import JsonResponse
import logging
import jwt
import os
from authentification.models import User

logger = logging.getLogger(__name__)

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Liste des URL à exclure de la vérification JWT
        paths_to_exclude = ['/auth/login', '/auth/signup', '/auth/token/refresh', '/auth/login42', '/metrics']

        # Récupère le chemin de la requête actuelle
        path = request.path_info

        # Vérifie si le chemin actuel est dans la liste des exclusions
        if path not in paths_to_exclude and not path.startswith('/media/') and not path.startswith('/local/'):
            try:

                # Tente d'authentifier le token JWT
                jwt_token = request.headers.get('Authorization').split(' ')[1]
                payload = jwt.decode(jwt_token, os.getenv('SECRET_KEY'), algorithms=['HS256'])

                if 'user_id' in payload:
                    user_id = payload['user_id']
                    user = User.objects.get(id=user_id)

                    # Change l'utilisateur en ligne
                    user.online_at = timezone.now()
                    user.is_active = True
                    user.save()

                    # Ajoute l'utilisateur à la requête
                    request.user = user

            except (InvalidToken, TokenError, AuthenticationFailed) as e:
                # Gère les erreurs de token invalide ou d'authentification échouée
                return JsonResponse({'authErrorMessage': str(e)}, status=401)

        response = self.get_response(request)
        return response