<template>
  <div>
    <Button
      icon="pi pi-star"
      class="p-button-sm p-button-outlined"
      label="Saved Recipes"
      @click="toggleSidebar"
    />
    <Sidebar
      v-model:visible="sidebarVisible"
      position="left"
      class="saved-recipes-sidebar"
    >
      <div class="sidebar-content">
        <h2>Saved Recipes</h2>
        <div v-if="savedRecipes.length === 0" class="empty-state">
          <i
            class="pi pi-info-circle mb-2"
            style="font-size: 2rem; color: #6c757d"
          ></i>
          <p>No saved recipes yet</p>
        </div>
        <div v-else class="recipe-list">
          <div
            v-for="recipe in savedRecipes"
            :key="recipe.id"
            class="recipe-item"
          >
            <Button
              icon="pi pi-trash"
              class="p-button-text p-button-danger p-button-sm"
              @click="deleteRecipe(recipe.id, recipe.title)"
            />
            <a @click="handleGetSavedRecipe(recipe.id)" class="recipe-link">
              {{ recipe.title }}
            </a>
          </div>
        </div>
      </div>
    </Sidebar>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import Sidebar from "primevue/sidebar";
import { useDataStore } from "@/stores/dataStore";
import Button from "primevue/button";
import axios from "axios";

defineExpose({
  getUserSavedRecipes,
});

// const props = defineProps(['sidebarVisible']);
const emit = defineEmits(["get-saved-recipe", "show-error"]);
const dataStore = useDataStore();
const sidebarVisible = ref(false);

const savedRecipes = ref([]);

watch(
  () => dataStore.isLoggedIn,
  (newVal) => {
    console.log("isLoggedIn change:", newVal);
    if (newVal === true) {
      getUserSavedRecipes();
    }
  }
);

const toggleSidebar = () => {
  sidebarVisible.value = !sidebarVisible.value;
};

const handleGetSavedRecipe = (recipeId) => {
  emit("get-saved-recipe", recipeId);
};

async function getUserSavedRecipes() {
  try {
    const response = await axios.get(
      `${dataStore.backendServer}/get_user_saved_recipes`,
      {
        params: { user_id: dataStore.userId },
      }
    );
    savedRecipes.value = response.data;
  } catch (error) {
    console.error("Failed getting user saved recipes:", error);
  }
}

async function deleteRecipe(recipeId, recipeTitle) {
  console.log("Deleting saved recipe:", recipeId, recipeTitle);
  await axios
    .delete(`${dataStore.backendServer}/delete_recipe`, {
      headers: { "Content-Type": "application/json" },
      data: {
        recipe_id: recipeId,
        title: recipeTitle,
        user_id: dataStore.userId,
      },
    })
    .then((resp) => {
      console.log("Resp:", resp);
      getUserSavedRecipes();
    })
    .catch((err) => {
      console.log("error:", err);
      emit("show-error", "Recipe failed to delete");
    });
}

onMounted(() => {
  getUserSavedRecipes();
});
</script>

<style>
.p-sidebar-header {
  justify-content: end;
  padding-bottom: 0px;
}
</style>

<style scoped>
.saved-recipes-sidebar :deep(.p-sidebar) {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.saved-recipes-sidebar :deep(.p-sidebar-header) {
  padding: 0;
}

.sidebar-content {
  padding: 1rem;
}

.sidebar-content h2 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-weight: 600;
  text-align: center;
}

.recipe-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.recipe-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.recipe-item:hover {
  background-color: rgba(67, 97, 238, 0.04);
}

.recipe-link {
  color: #4361ee;
  cursor: pointer;
  text-decoration: none;
  flex: 1;
  font-weight: 500;
}

.recipe-link:hover {
  text-decoration: underline;
  background-color: transparent;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: #6c757d;
  text-align: center;
  background-color: #f8f9fa;
  border-radius: 8px;
}
</style>
