from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Recipe
from .serializers import UserSerializer, RecipeSerializer, RecipeListSerializer
import bcrypt
import json
import os
import base64
from openai import OpenAI
import requests
from django.conf import settings
from django.http import JsonResponse

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# User Registration
@api_view(['POST'])
def register(request):
    if not request.data.get('username') or not request.data.get('password'):
        return Response({'message': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if username exists
    if User.objects.filter(username=request.data.get('username')).exists():
        return Response({'message': 'Username already exists'}, status=status.HTTP_409_CONFLICT)
    
    # Create new user
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Login
@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    try:
        user = User.objects.get(username=username)
        
        # Check password using bcrypt
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token),
                'user_id': user.id
            }, status=status.HTTP_200_OK)
        
        return Response({'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

# Recipe Generation
@api_view(['GET'])
def generate_recipe(request):
    prompt = request.query_params.get('prompt')
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "I'd like you to please help generate recipes for me if I give you a list of ingredients and/or maximum number of ingredients (salt and pepper don't count) or describe what I'm in the mood for. I may also give a number of servings. Can you please format your whole response in JSON format, with separate keys for the title, ingredients, instructions, servings, an image_prompt, and any other response message. Each ingredient and instruction should be a single string without any numbering"},
            {"role": "user", "content": prompt}
        ],
        response_format={'type': 'json_object'},
        temperature=1,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    resp = dict(response)['choices'][0].message.content
    resp = resp.replace('```json', '').replace('```', '')
    
    return Response(json.loads(resp))

# Image Generation
@api_view(['POST'])
def generate_image(request):
    engine_id = "stable-diffusion-v1-6"
    api_host = settings.API_HOST
    api_key = settings.STABILITY_API_KEY
    title = request.data.get('title').replace(' ', '_')
    user_id = request.data.get('user_id')
    prompt = request.data.get('prompt')
    
    if not api_key:
        return Response({'error': 'Missing Stability API key'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "text_prompts": [{"text": prompt}],
            "height": 1024,
            "width": 1024,
        },
    )
    
    if response.status_code != 200:
        return Response({'error': f'Non-200 response: {response.text}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    data = response.json()
    for i, image in enumerate(data["artifacts"]):
        image_path = f"{settings.MEDIA_ROOT}{title}_{user_id}.png"
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image["base64"]))
    
    return Response({'img': data['artifacts'][0]['base64']})

# Get Saved Image
@api_view(['GET'])
def get_saved_image(request):
    user_id = request.query_params.get('user_id')
    title = request.query_params.get('title').replace(' ', '_')
    image_path = f"{settings.MEDIA_ROOT}{title}_{user_id}.png"
    
    if not os.path.exists(image_path):
        return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
    
    with open(image_path, "rb") as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
    
    return Response({'image': encoded_image})

# Recipe CRUD Operations
class RecipeViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    # Save Recipe
    def create(request):
        user_id = request.data.get('user_id')
        title = request.data.get('title')
        ingredients = request.data.get('ingredients')
        instructions = request.data.get('instructions')
        image_prompt = request.data.get('image_prompt')
        servings = request.data.get('servings')
        
        if not all([user_id, title, ingredients, instructions, image_prompt, servings]):
            return Response({'message': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            recipe, created = Recipe.objects.update_or_create(
                user=user,
                title=title,
                defaults={
                    'ingredients': ingredients,
                    'instructions': instructions,
                    'image_prompt': image_prompt,
                    'servings': servings
                }
            )
            
            if created:
                return Response({'message': 'Recipe saved successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Recipe updated'}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Get Recipe by ID
    @api_view(['GET'])
    def get_recipe(request):
        recipe_id = request.query_params.get('recipe_id')
        
        try:
            recipe = Recipe.objects.get(id=recipe_id)
            serializer = RecipeSerializer(recipe)
            return Response(serializer.data)
        except Recipe.DoesNotExist:
            return Response({'message': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Delete Recipe
    @api_view(['DELETE'])
    def delete_recipe(request):
        recipe_id = request.data.get('recipe_id')
        user_id = request.data.get('user_id')
        title = request.data.get('title').replace(' ', '_')
        
        try:
            recipe = Recipe.objects.get(id=recipe_id, user_id=user_id)
            recipe.delete()
            
            # Delete associated image
            image_path = f"{settings.MEDIA_ROOT}{title}_{user_id}.png"
            if os.path.exists(image_path):
                os.remove(image_path)
                return Response({'message': 'Recipe deleted successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Recipe image not found'}, status=status.HTTP_404_NOT_FOUND)
                
        except Recipe.DoesNotExist:
            return Response({'message': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get User's Saved Recipes
    @api_view(['GET'])
    def get_user_recipes(request):
        user_id = request.query_params.get('user_id')
        
        try:
            recipes = Recipe.objects.filter(user_id=user_id)
            serializer = RecipeListSerializer(recipes, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 