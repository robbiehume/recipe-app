<template>
  <div>
    <Button icon="pi pi-star" class="p-button-sm" label="Saved Recipes" @click="toggleSidebar" />
    <Sidebar v-model:visible="sidebarVisible"  position="left">
      <div class="flex flex-column align-items-center">
      <h2>Saved Recipes</h2>
      <div class="p-0 pt-2">
        <div
        v-for="recipe in savedRecipes"
        :key="recipe.id"
        class="py-1 flex gap-2 align-items-center"
        >
          <i
            class="pi pi-trash text-red-300"
            style="cursor: pointer;"
            @click="deleteRecipe(recipe.id, recipe.title)"
          />
          <a @click="handleGetSavedRecipe(recipe.id)" style="cursor: pointer;">
              {{ recipe.title }}
          </a>
        </div>
      </div>
      </div>
    </Sidebar>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import Sidebar from 'primevue/sidebar';
import { useDataStore } from '@/stores/dataStore';
import Button from 'primevue/button';
import axios from 'axios';

defineExpose({
  getUserSavedRecipes,
});

// const props = defineProps(['sidebarVisible']);
const emit = defineEmits(['get-saved-recipe', 'show-error']);
const dataStore = useDataStore();
const sidebarVisible = ref(false);

const savedRecipes = ref([]);

watch(() => dataStore.isLoggedIn, (newVal) => {
  console.log('isLoggedIn change:', newVal)
  if (newVal === true) {
    getUserSavedRecipes()
  }
})

const toggleSidebar = () => {
  sidebarVisible.value = !sidebarVisible.value;
};

const handleGetSavedRecipe = (recipeId) => {
  emit('get-saved-recipe', recipeId);
};

async function getUserSavedRecipes() {
  try {
    const response = await axios.get('http://webserverloadbalancer-248097766.us-east-2.elb.amazonaws.com/api/get_user_saved_recipes', {
      params: { user_id: dataStore.userId },
    });
    savedRecipes.value = response.data;
  } catch (error) {
    console.error('Failed getting user saved recipes:', error);
  }
};

async function deleteRecipe(recipeId, recipeTitle) {
  console.log('Deleting saved recipe:', recipeId, recipeTitle);
  await axios
    .delete(`${dataStore.backendServer}/delete_recipe`, {
      headers: {'Content-Type': 'application/json'},
      data: { recipe_id: recipeId, title: recipeTitle, user_id: dataStore.userId } 
    })
    .then((resp) => {
      console.log('Resp:', resp)
      getUserSavedRecipes()
    })
    .catch((err) => {
      console.log('error:', err)
      emit('show-error', 'Recipe failed to delete')
    })
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

.side-panel {
  width: 200px;
  display: flex;
  align-items: center;
  background-color: #f4f4f4;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.side-panel .p-button {
  margin-bottom: 10px;
}
</style>