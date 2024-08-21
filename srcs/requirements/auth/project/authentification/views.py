from django.utils import timezone
import json
import logging
import os
import random
from django.http import JsonResponse
from django.shortcuts import render
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from authentification.models import Game, Tournament, User, validate_password, validate_avatar, validate_email
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

#**************************************************************************#
#                          JWT TOKEN                                       #
#**************************************************************************#

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refreshToken': str(refresh),
        'accessToken': str(refresh.access_token),
        'expiresIn': 3600,
    }

def refreshToken(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            refresh_token = data.get('refreshToken')

            if refresh_token is None:
                return JsonResponse({'errorMessage': 'Refresh token is required'}, status=400)

            refresh = RefreshToken(refresh_token)

            if not refresh:
                return JsonResponse({'errorMessage': 'Invalid refresh token'}, status=400)
            
            token = {
                'refreshToken': str(refresh),
                'accessToken': str(refresh.access_token),
                'expiresIn': 3600,
            }

            return JsonResponse(token, status=200)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'errorMessage': 'Server error'}, status=500)
    return JsonResponse({'errorMessage': 'Method not allowed'}, status=405)

#**************************************************************************#
#                           AUTHENTIFICATION                               #
#**************************************************************************#

def login(request):
    if request.method == 'POST':
        try :
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            # Vérifie si l'utilisateur existe
            user = User.objects.filter(username=username).first()
            if user is None:
                return JsonResponse({'errorMessage': 'User does not exist'}, status=400)

            # Vérifie si le mot de passe est correct
            if not user.check_password(password):
                return JsonResponse({'errorMessage': 'Wrong password'}, status=400)
            
            # Génère le token JWT pour l'utilisateur
            token = get_tokens_for_user(user)
            
            return JsonResponse(token, status=200)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'errorMessage': 'Server error'}, status=500)
    return JsonResponse({'errorMessage': 'Method not allowed'}, status=405)

def signup(request):
    if request.method == 'POST':
        try:
            # Pour les données non-fichier, utilisez request.POST au lieu de json.loads(request.body)
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            avatar = request.FILES.get('avatar')  # Accès au fichier uploadé

            if not all ([username, email, password]):
                    logger.warning('Missing required fields in signup form')
                    return JsonResponse({'errorMessage': 'All fields are required'}, status=400)
            
            try:
                validate_password(password)
            except ValidationError as e:
                error_msg = str(e)
                logger.warning('Invalid password: %s', error_msg)
                return JsonResponse({'errorMessage': error_msg}, status=400)
            
            if avatar:
                try:
                    validate_avatar(avatar)
                except ValidationError as e:
                    error_msg = str(e)
                    logger.warning('Invalid avatar: %s', error_msg)
                    return JsonResponse({'errorMessage': error_msg}, status=400)
            
            try:
                validate_email(email)
            except ValidationError as e:
                error_msg = str(e)
                logger.warning('Invalid email: %s', error_msg)
                return JsonResponse({'errorMessage': error_msg}, status=400)

            # Vérifie si l'utilisateur existe
            if User.objects.filter(username=username).exists():
                return JsonResponse({'errorMessage': 'Username already exists'}, status=400)
            elif User.objects.filter(email=email).exists():
                return JsonResponse({'errorMessage': 'Email already exists'}, status=400)
            
            # hash le mot de passe
            hashed_password = make_password(password)

            # Crée un nouvel utilisateur
            user = User(username=username, email=email, hashed_password=hashed_password)
            user.save()

            if avatar:
                # Création d'un nouveau nom de fichier pour l'avatar incluant l'ID de l'utilisateur
                new_avatar_name = f"{user.id}_{avatar.name}"
                
                # Lecture du contenu de l'avatar original
                avatar_content = avatar.read()
                
                # Création d'un nouveau fichier avec le nouveau nom et le contenu original
                user.avatar.save(new_avatar_name, ContentFile(avatar_content))

            # Génère le token JWT pour le nouvel utilisateur (implémentation spécifique nécessaire ici)
            token = get_tokens_for_user(user)
            
            return JsonResponse(token, status=201)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'errorMessage': 'An error occurred'}, status=500)
    else:
        return JsonResponse({'errorMessage': 'Method not allowed'}, status=405)

def login42(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')
            redirect_uri = data.get('redirectUri')

            if code is None:
                return JsonResponse({'errorMessage': 'Code is required'}, status=400)

            post_data = {
                'client_id': os.getenv('FORTYTWO_CLIENT_ID'),
                'client_secret': os.getenv('FORTYTWO_SECRET'),
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri,
            }

            # Get the access token from the 42 API
            token_response = requests.post('https://api.intra.42.fr/oauth/token', data=post_data)

            if token_response.status_code != 200:
                return JsonResponse({'errorMessage': 'Invalid code'}, status=400)
            
            token_data = token_response.json()
            access_token = token_data.get('access_token')
            if access_token is None:
                return JsonResponse({'errorMessage': 'Invalid code'}, status=400)
            
            # Get the user info from the 42 API
            user_response = requests.get('https://api.intra.42.fr/v2/me', headers = {
                'Authorization': f'Bearer {access_token}'
            })

            if user_response.status_code != 200:
                return JsonResponse({'errorMessage': 'An error occurred'}, status=500)
            
            user_data = user_response.json()
            username = user_data.get('login')
            email = user_data.get('email')
            id = user_data.get('id')
            avatar_url = user_data.get('image', {}).get('link')  # Mise à jour ici
            if username is None or email is None or id is None:
                return JsonResponse({'errorMessage': 'An error occurred'}, status=500)
            
            # Vérifie si l'utilisateur existe
            user = User.objects.filter(id42=id).first()
            if user is None:
                if User.objects.filter(username=username).exists():
                    username = f'{username}_{random.randint(0, 1000)}'
                if User.objects.filter(email=email).exists():
                    return JsonResponse({'errorMessage': 'Email already exists'}, status=400)

                # Crée un nouvel utilisateur
                logger.error(f"username: {username}, email: {email}, id: {id}, avatar: {avatar_url}")
                user = User(username=username, email=email, id42=id)
                user.save()

                if avatar_url:
                    # Télécharge l'avatar de l'URL fournie
                    avatar_response = requests.get(avatar_url)

                    if avatar_response.status_code == 200:
                        # Crée un nouveau nom de fichier pour l'avatar incluant l'ID de l'utilisateur
                        new_avatar_name = f"{user.id}_avatar.jpg"
                        
                        # Création d'un nouveau fichier avec le nouveau nom et le contenu téléchargé
                        user.avatar.save(new_avatar_name, ContentFile(avatar_response.content))


            # Génère le token JWT pour l'utilisateur
            token = get_tokens_for_user(user)

            return JsonResponse(token, status=200)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'errorMessage': 'An error occurred'}, status=500)
    return JsonResponse({'errorMessage': 'Method not allowed'}, status=405)

def logout(request):
    if request.method == 'POST':
        if request.user:
            request.user.is_active = False
            request.user.save()

        return JsonResponse({'detail': 'Successfully logged out'}, status=200)
    return JsonResponse({'detail': 'Method not allowed'}, status=405)

#**************************************************************************#
#                       UPDATE USER INFORMATIONS                           #
#**************************************************************************#

def updateEmail(request):
    if request.method == 'PUT':
        try:
            if request.user.id42:
                return JsonResponse({'errorMessage': 'Cannot update email for 42 accounts'}, status=400)

            data = json.loads(request.body)
            email = data.get('email')
            logger.error(f"email: {email}")
            if email is None:
                return JsonResponse({'errorMessage': 'Email is required'}, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'errorMessage': 'Email already exists'}, status=400)

            try:
                validate_email(email)
            except ValidationError as e:
                error_msg = str(e)
                logger.warning('Invalid email: %s', error_msg)
                return JsonResponse({'errorMessage': error_msg}, status=400)

            request.user.email = email
            request.user.save()

            return JsonResponse({'successMessage': 'Email updated successfully'}, status=200)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'errorMessage': 'An error occurred'}, status=500)
    return JsonResponse({'errorMessage': 'Method not allowed'}, status=405)

def updateUsername(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            username = data.get('username')

            if username is None:
                return JsonResponse({'errorMessage': 'Username is required'}, status=400)
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'errorMessage': 'Username already exists'}, status=400)

            request.user.username = username
            request.user.save()

            return JsonResponse({'successMessage': 'Username updated successfully'}, status=200)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'errorMessage': 'An error occurred'}, status=500)
    return JsonResponse({'errorMessage': 'Method not allowed'}, status=405)

def updatePassword(request):
    if request.method == 'PUT':
        try:
            if request.user.id42:
                return JsonResponse({'errorMessage': 'Cannot update password for 42 accounts'}, status=400)

            data = json.loads(request.body)
            new_password = data.get('password')

            if new_password is None:
                return JsonResponse({'errorMessage': 'Password is required'}, status=400)
            
            try:
                validate_password(new_password)
            except ValidationError as e:
                error_msg = str(e)
                logger.warning('Invalid password: %s', error_msg)
                return JsonResponse({'errorMessage': error_msg}, status=400)
            
            request.user.hashed_password = make_password(new_password)
            request.user.save()

            return JsonResponse({'successMessage': 'Password updated successfully'}, status=200)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'errorMessage': 'An error occurred'}, status=500)
    return JsonResponse({'errorMessage': 'Method not allowed'}, status=405)

def updateAvatar(request):
    if request.method == 'POST':
        try:
            avatar = request.FILES.get('avatar')
            logger.error(f"avatar: {avatar}")

            if avatar is None:
                return JsonResponse({'errorMessage': 'Avatar is required'}, status=400)
            
            try:
                validate_avatar(avatar)
            except ValidationError as e:
                error_msg = str(e)
                logger.warning('Invalid avatar: %s', error_msg)
                return JsonResponse({'errorMessage': error_msg}, status=400)
            
            # Crée un nouveau nom de fichier pour l'avatar incluant l'ID de l'utilisateur
            new_avatar_name = f"{request.user.id}_{avatar.name}"
            
            # Lecture du contenu de l'avatar original
            avatar_content = avatar.read()
            
            # Création d'un nouveau fichier avec le nouveau nom et le contenu original
            request.user.avatar.save(new_avatar_name, ContentFile(avatar_content))

            return JsonResponse({'successMessage': 'Avatar updated successfully'}, status=200)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'errorMessage': 'An error occurred'}, status=500)
    return JsonResponse({'errorMessage': 'Method not allowed'}, status=405)

#**************************************************************************#
#                       GET USER INFORMATIONS                              #
#**************************************************************************#

def userInfos(request):
    if request.method == 'GET':
        if request.user:
            return JsonResponse({
                'id': request.user.id,
                'username': request.user.username, 
                'email': request.user.email,
                'avatar': request.user.avatar.url if request.user.avatar else None,
                'tournament_victories': request.user.nb_tournament_victories,
                'victories': request.user.nb_victories,
                'defeats': request.user.nb_defeats,
                'date': request.user.created_at 
            }, status=200)
        return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=401)
    return JsonResponse({'detail': 'Method not allowed'}, status=405)

#**************************************************************************#
#                       FRIENDS MANAGEMENT                                 #
#**************************************************************************#

def friendList(request):
    if request.method == 'GET':
        if request.user:
            # Récupère la liste des amis de l'utilisateur
            friends = request.user.friends.all()

            # Récupère la liste des demandes d'amis recu par l'utilisateur
            friend_requests_received = request.user.friend_requests_received.all()

            # Pour chaque ami, vérifie si il est connecté
            for friend in friends:
                if friend.is_active:
                    if timezone.now() - friend.online_at > timezone.timedelta(minutes=5):
                        friend.is_active = False
                        friend.save()

            # Retourne la liste des amis et des demandes d'amis recu avec leur username et avatar
            return JsonResponse({
                'friends': [
                    {
                        'username': friend.username,
                        'is_active': friend.is_active,
                        'avatar': friend.avatar.url if friend.avatar else None
                    } for friend in friends
                ],
                'friendRequestsReceived': [
                    {
                        'username': friend_request.from_user.username,
                        'avatar': friend_request.from_user.avatar.url if friend_request.from_user.avatar else None
                    } for friend_request in friend_requests_received
                ]
            }, status=200)
        return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=401)
    return JsonResponse({'detail': 'Method not allowed'}, status=405)

def friendRequest(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')

            if username is None:
                return JsonResponse({'errorMessage': 'Username is required'}, status=400)

            # Récupère l'utilisateur cible de la demande d'amis
            to_user = User.objects.filter(username=username).first()

            if to_user is None:
                return JsonResponse({'errorMessage': 'User does not exist'}, status=400)
            
            # Vérifie si l'utilisateur cible n'est pas déjà un ami
            if request.user.friends.filter(id=to_user.id).exists():
                return JsonResponse({'errorMessage': 'User is already a friend'}, status=400)

            # Envoie une demande d'amis
            request.user.send_friend_request(to_user)

            return JsonResponse({'successMessage': 'Friend request sent successfully'}, status=200)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'errorMessage': 'An error occurred'}, status=500)
    return JsonResponse({'errorMessage': 'Method not allowed'}, status=405)

def acceptFriendRequest(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')

            if username is None:
                return JsonResponse({'errorMessage': 'Username is required'}, status=400)

            # Récupère l'utilisateur source de la demande d'amis
            from_user = User.objects.filter(username=username).first()

            if from_user is None:
                return JsonResponse({'errorMessage': 'User does not exist'}, status=400)
            
            # Accepte la demande d'amis
            request.user.accept_friend_request(from_user)

            return JsonResponse({'successMessage': 'Friend request accepted successfully'}, status=200)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'errorMessage': 'An error occurred'}, status=500)
    return JsonResponse({'errorMessage': 'Method not allowed'}, status=405)

def declineFriendRequest(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')

            if username is None:
                return JsonResponse({'errorMessage': 'Username is required'}, status=400)

            # Récupère l'utilisateur source de la demande d'amis
            from_user = User.objects.filter(username=username).first()

            if from_user is None:
                return JsonResponse({'errorMessage': 'User does not exist'}, status=400)
            
            # Refuse la demande d'amis
            request.user.decline_friend_request(from_user)

            return JsonResponse({'successMessage': 'Friend request declined successfully'}, status=200)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'errorMessage': 'An error occurred'}, status=500)
    return JsonResponse({'errorMessage': 'Method not allowed'}, status=405)

#**************************************************************************#
#                       GAME MANAGEMENT                                    #
#**************************************************************************#

def gameResult(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # data = {
            #     'tournament_winner': 'player1',
            #     'tournament_players': ['player1', 'player2'],
            #     'matches': [
            #         {
            #             'winner': 'player1',
            #             'winner_score': 10,
            #             'loser': 'player2',
            #             'loser_score': 5
            #         },
            #         {
            #             'winner': 'player2',
            #             'winner_score': 10,
            #             'loser': 'player1',
            #             'loser_score': 7
            #         }
            #     ],
            # }
            logger.error(f"data: {data}")

            tournament_winner = data.get('tournament_winner')
            tournament_winner = User.objects.filter(id=tournament_winner).first()
            tournament_players = data.get('tournament_players')
            tournament_players = User.objects.filter(id__in=tournament_players)
            matches = data.get('matches')

            logger.error(f"tournament_winner: {tournament_winner}")
            logger.error(f"tournament_players: {tournament_players}")
            logger.error(f"matches: {matches}")

            if tournament_winner is None or not tournament_players.exists() or matches is None:
                logger.error("ret 1")
                return JsonResponse({'errorMessage': 'All fields are required'}, status=400)
            
            if tournament_winner not in tournament_players:
                logger.error("ret 2")
                return JsonResponse({'errorMessage': 'Invalid tournament winner'}, status=400)
            
            for match in matches:
                winner = match.get('winner')
                winner = User.objects.filter(id=winner).first()
                winner_score = match.get('winner_score')
                loser = match.get('loser')
                loser = User.objects.filter(id=loser).first()
                loser_score = match.get('loser_score')

                if winner is None or winner_score is None or loser is None or loser_score is None:
                    logger.error("ret 3")
                    return JsonResponse({'errorMessage': 'All fields are required'}, status=400)
                
                if winner not in tournament_players or loser not in tournament_players:
                    logger.error("ret 4")
                    return JsonResponse({'errorMessage': 'Invalid match players'}, status=400)
                
                if winner == loser:
                    logger.error("ret 5")
                    return JsonResponse({'errorMessage': 'Winner and loser must be different'}, status=400)
                
                if winner_score < 0 or loser_score < 0:
                    logger.error("ret 6")
                    return JsonResponse({'errorMessage': 'Scores must be positive'}, status=400)
                
                # if winner_score == loser_score:
                #     logger.error("ret 7")
                #     return JsonResponse({'errorMessage': 'Winner and loser scores must be different'}, status=400)
                
                if winner_score < loser_score:
                    logger.error("ret 8")
                    return JsonResponse({'errorMessage': 'Winner score must be greater than loser score'}, status=400)
                
            # Create new tournament
            tournament = Tournament(created_at=timezone.now(), winner=tournament_winner)
            tournament.save()  # Save the tournament to generate its ID required for M2M relationships

            # Assign players to the tournament using .set()
            tournament.players.set(tournament_players)

            # Create new games
            for match in matches:
                winner = match.get('winner')
                winner = User.objects.filter(id=winner).first()
                winner_score = match.get('winner_score')
                loser = match.get('loser')
                loser = User.objects.filter(id=loser).first()
                loser_score = match.get('loser_score')

                # Update user statistics
                winner.nb_victories += 1
                winner.save()
                loser.nb_defeats += 1
                loser.save()

                game = Game(winner=winner, winner_score=winner_score, loser=loser, loser_score=loser_score)
                game.save()
                tournament.games.add(game)

            tournament.save()

            # Update user statistics
            tournament_winner.refresh_from_db()
            tournament_winner.nb_tournament_victories += 1
            tournament_winner.save()

            return JsonResponse({'successMessage': 'Result updated successfully'}, status=200)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'errorMessage': 'An error occurred'}, status=500)
    return JsonResponse({'errorMessage': 'Method not allowed'}, status=405)

def gameHistory(request):
    if request.method == 'GET':
        if request.user:
            # Récupérer les tournois où l'utilisateur a participé joins avec les jeux associés
            tournaments = Tournament.objects.filter(players=request.user).prefetch_related('games').order_by('-created_at')

            # Retourne la liste des tournois et des jeux avec les informations associées
            return JsonResponse({
                'tournaments': [
                    {
                        'id': tournament.id,
                        'date': tournament.created_at,
                        'winner': tournament.winner.username,
                        'players': [
                            {
                                'username': player.username, 
                                'avatar': player.avatar.url if player.avatar else None
                            }
                            for player in tournament.players.all()
                        ],
                        'games': [
                            {
                                'winner': game.winner.username,
                                'winner_avatar': game.winner.avatar.url if game.winner.avatar else None,
                                'winner_score': game.winner_score,
                                'loser': game.loser.username,
                                'loser_avatar': game.loser.avatar.url if game.loser.avatar else None,
                                'loser_score': game.loser_score
                            } for game in tournament.games.all()
                        ]
                    } for tournament in tournaments
                ]
            }, status=200)
        return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=401)
    return JsonResponse({'detail': 'Method not allowed'}, status=405)