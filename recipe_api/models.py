from django.db import models
from django.contrib.auth.models import User

class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=255)
    ingredients = models.JSONField()  # Store as JSON
    instructions = models.JSONField()  # Store as JSON
    image_path = models.CharField(max_length=255, blank=True, null=True)
    image_prompt = models.TextField()
    servings = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'title')  # Each user can have unique recipe titles
        
    def __str__(self):
        return f"{self.user.username} - {self.title}" 