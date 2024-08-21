from django.db import models
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
import re

def validate_password(value):
    if len(value) < 8:
        raise ValidationError('The password must contain at least 8 characters.')  
    if not re.findall(r'[A-Z]', value):
        raise ValidationError('The password must contain at least 1 uppercase.')
    if not re.findall(r'[a-z]', value):
        raise ValidationError('LThe password must contain at least 1 lowercase.')
    if not re.findall(r'\d', value):
        raise ValidationError('The password must contain at least one digit.')
    if not re.findall(r'[!@#$%^&*(),.?":{}=|<>]', value):
        raise ValidationError('The password must contain at least one special character.')
 
class PasswordValidator:
    def validate(self, password, user=None):
        validate_password(password)

    def get_help_text(self):
        return 'The password must contain at least 8 characters, 1 uppercase, 1 lowercase, 1 digit, and 1 special character.'

def validate_avatar(file):
    valid_mime_types = ['image/jpeg', 'image/png', 'image/jpg']
    valid_extensions = ['jpg', 'jpeg', 'png']
    if file.content_type not in valid_mime_types:
        raise ValidationError('The type of the selected image is not supported.')
    if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
        raise ValidationError('The format of the selected image is not supported.')
    width, height = get_image_dimensions(file)
    if width > 1024 or height > 1024:
        raise ValidationError('Image dimensions should not exceed 1024x1024 pixels.')

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(fr|com)$'
    if not re.match(pattern, email):
        raise ValidationError("The email must be in the form exemple@exemple.com/fr.")

class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, validators=[validate_email])
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, validators=[validate_avatar])
    hashed_password = models.CharField(max_length=128)
    id42 = models.CharField(null=True, unique=True)
    nb_tournament_victories = models.IntegerField(default=0)
    nb_victories = models.IntegerField(default=0)
    nb_defeats = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    online_at = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)
    
    friends = models.ManyToManyField('User', blank=True)

    def __str__(self):
        return self.username
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.hashed_password)
    
    def send_friend_request(self, to_user):
        if to_user == self:
            raise ValueError("Vous ne pouvez pas vous envoyer une demande d'amitié à vous-même.")
        if not FriendRequest.objects.filter(from_user=self, to_user=to_user).exists():
            FriendRequest.objects.create(from_user=self, to_user=to_user)

    def accept_friend_request(self, from_user):
        try:
            friend_request = FriendRequest.objects.get(from_user=from_user, to_user=self)
            if not self.friends.filter(id=from_user.id).exists():
                self.friends.add(from_user)
                from_user.friends.add(self)
                friend_request.delete()
            else:
                raise ValueError("La demande d'amitié n'existe pas ou a déjà été acceptée.")
        except FriendRequest.DoesNotExist:
            raise ValueError("La demande d'amitié n'existe pas.")

    def decline_friend_request(self, from_user):
        try:
            friend_request = FriendRequest.objects.get(from_user=from_user, to_user=self)
            friend_request.delete()
        except FriendRequest.DoesNotExist:
            raise ValueError("La demande d'amitié n'existe pas.")

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user.username} to {self.to_user.username}"

    class Meta:
        unique_together = ('from_user', 'to_user')

class Game(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='won_games', null=True)
    winner_score = models.IntegerField()
    loser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lost_games', null=True)
    loser_score = models.IntegerField()

    def __str__(self):
        return self.name

class Tournament(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='won_tournaments', null=True)
    players = models.ManyToManyField(User, related_name='tournaments', blank=True)
    games = models.ManyToManyField(Game, related_name='tournaments', blank=True)

    def __str__(self):
        return self.name