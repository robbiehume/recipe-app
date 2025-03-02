from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Recipe
import bcrypt

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
    
    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        
        # Create a new user
        user = User.objects.create(
            username=username
        )
        
        # Hash the password using bcrypt
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password = hashed_pw
        user.save()
        
        return user

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'title', 'ingredients', 'instructions', 'image_path', 'image_prompt', 'servings')
        
class RecipeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'title') 