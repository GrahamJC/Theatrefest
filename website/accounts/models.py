from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    
    user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True, related_name = 'profile')
    address1 = models.CharField(max_length = 64, blank = True, default = '')
    address2 = models.CharField(max_length = 64, blank = True, default = '')
    city = models.CharField(max_length = 32, blank = True, default = '')
    post_code = models.CharField(max_length = 10, blank = True, default = '')
    telno = models.CharField(max_length = 32, blank = True, default = '')
    
    def __str__(self):
        return self.user.username

