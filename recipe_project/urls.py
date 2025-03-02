from django.contrib import admin
from django.urls import path
from recipe_api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Update URL patterns to match Flask API exactly (without /api prefix)
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('generate_recipe/', views.generate_recipe, name='generate_recipe'),
    path('image/', views.generate_image, name='generate_image'),
    path('get_saved_image/', views.get_saved_image, name='get_saved_image'),
    path('save_recipe/', views.RecipeViewSet.create, name='save_recipe'),
    path('get_saved_recipe/', views.RecipeViewSet.get_recipe, name='get_saved_recipe'),
    path('delete_recipe/', views.RecipeViewSet.delete_recipe, name='delete_recipe'),
    path('get_user_saved_recipes/', views.RecipeViewSet.get_user_recipes, name='get_user_saved_recipes'),
] 