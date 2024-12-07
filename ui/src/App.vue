<template>
  <div class="app-container flex-column align-items-center" style="width: 90vw; max-width: 1000px">
      
    <div class="flex justify-content-between" style="width: 100%" >
      <SavedRecipesList ref="savedRecipesListRef" @get-saved-recipe="getSavedRecipe" @show-error="showError" />
      <Login class="p-0 align-self-end" />
    </div>

    <div class="header flex-column gap-3" style="">
      <RecipeForm ref="recipeFormRef" @get-recipe="getRecipe" />
      <div class="flex justify-content-center gap-3">
        <Button id="generate-button" :disabled="gettingRecipe" @click="getRecipe()" class="flex justify-content-center" style="margin-left: 0; width: 161px">
          <span v-if="gettingRecipe" class="px-3">Generating...</span>
          <span v-else-if="recipeFormRef?.emptyPromptAndIngredients" class="" style="">Random Recipe</span>
          <span v-else>Generate Recipe</span>
        </Button>
        <Button raised :disabled="displayedRecipe === ''" id="save-button" severity="secondary" label="" @click="saveRecipe()" >
          Save Recipe
        </Button>
        <!-- <Button raised icon="pi pi-thumbs-up-fill" severity="success" @click="likeRecipe()" /> -->
        <!-- <Button raised icon="pi pi-thumbs-down-fill" severity="danger" @click="dislikeRecipe()" /> -->
        <Button raised :disabled="displayedRecipe === ''" severity="secondary" label="" @click="exportToPDF">
          Export to PDF
        </Button>
      </div>

      <RecipeDisplay 
        ref="recipeDisplayRef"
        :displayedRecipe="displayedRecipe" 
        :imageSrc="imageSrc" 
        :imageResponse="imageResponse" 
        :gettingRecipe="gettingRecipe" 
        :gettingImage="gettingImage" 
      />

    </div> 
    <Toast style="width: fit-content" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import "primeflex/primeflex.css";
import { useDataStore } from '@/stores/dataStore';
import SavedRecipesList from '@/components/SavedRecipesList.vue';
import RecipeForm from '@/components/RecipeForm.vue';
import RecipeDisplay from '@/components/RecipeDisplay.vue';
import Login from '@/components/Login.vue'
import axios from 'axios'
import Button from 'primevue/button';
import jsPDF from 'jspdf'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast';

const toast = useToast();

const dataStore = useDataStore();

onMounted(() => {
  if (dataStore.isLoggedIn) {
    savedRecipesListRef.value.getUserSavedRecipes()
  }
});

const gettingRecipe = ref(false)
const gettingImage = ref(false)
const imageResponse = ref('')
const imageSrc = ref('')
const displayedRecipe = ref('')

const savedRecipesListRef = ref(null)
const recipeFormRef = ref(null)
const recipeDisplayRef = ref(null)

// const menuItems = ref([
  // {label: 'Home', icon: 'pi pi-home'},
  // {label: 'Saved Recipes', icon: 'pi pi-star'}
// ])

function showSuccess(message) {
    toast.add({ severity: 'success', detail: message, life: 3000, closable: false });
};

function showError(message) {
    toast.add({ severity: 'error', detail: message, life: 3000, closable: false });
};

async function saveRecipe() {
  if (!dataStore.isLoggedIn) {
    dataStore.showLoginDialog = true
    return
  }

  const recipe = displayedRecipe.value
  console.log('Saved recipes; recipe:', recipe);

  await axios
    .post(`${dataStore.backendServer}/save_recipe`, 
        { user_id: dataStore.userId,
          title: recipe.title, 
          ingredients: recipe.ingredients,
          instructions: recipe.instructions,
          image_prompt: recipe.image_prompt,
          servings: recipe.servings
        })
    .then((resp) => {
      console.log('Resp:', resp)
      showSuccess('Recipe saved successfully')
      savedRecipesListRef.value.getUserSavedRecipes()
    })
    .catch((err) => {
      console.log('error:', err)
      showError('Recipe failed to save')
    })
};

async function getSavedRecipe(recipeId) {
  console.log('Getting saved recipe');
  await axios
    .get(`${dataStore.backendServer}/get_saved_recipe`, { 
      params: { recipe_id: recipeId } 
    })
    .then((resp) => {
      console.log('Resp:', resp)
      displayedRecipe.value = resp.data
      if (dataStore.generateImage){
        getSavedImage(resp.data.title)
      }
    })
    .catch((err) => {
      console.log('error:', err)
    })
}

async function getSavedImage(imageTitle){
  imageResponse.value = ''
  gettingImage.value = true
  await axios
    .get(`${dataStore.backendServer}/get_saved_image`, { params: { title: imageTitle, user_id: dataStore.userId } })
    .then((resp) => {
      console.log(resp.data)
      imageResponse.value = resp.data
      imageSrc.value = "data:image/png;base64," + resp.data.image
      gettingImage.value = false
    })
    .catch((err) => {
      console.log(err)
      if (err.response.status === 404) {
        getImage(imageTitle, displayedRecipe.value.image_prompt)
      }
      else {
        imageResponse.value = 'error'
        gettingImage.value = false
      }
    })
}

const exportToPDF = () => {
  const element = recipeDisplayRef.value.contentToExport;
  const pdf = new jsPDF('p', 'mm', 'a4');

  pdf.html(element, {
    callback: (doc) => {
      doc.save(`${displayedRecipe.value.title} Recipe.pdf`);
    },
    x: 17,
    y: 10,
    html2canvas: {
      scale: .15, 
      useCORS: true
    },
    width: 190, 
    windowWidth: element.scrollWidth 
  });
};

watch(() => dataStore.generateImage, (newVal) => {
  console.log('generateImage change:', newVal, displayedRecipe.value, imageSrc.value)
  if (newVal === true && displayedRecipe.value !== '' && imageSrc.value === '') {
    getImage(displayedRecipe.value.title, displayedRecipe.value.image_prompt)
  }
})

async function getRecipe(){
  displayedRecipe.value = ''
  gettingRecipe.value = true
  const img = document.getElementById('recipe-img')

  if (img) {
    img.style.display = 'none'
    console.log(img)
  }

  console.log('fullPrompt:', recipeFormRef.value.fullPrompt)

  await axios
    .get(`${dataStore.backendServer}/generate_recipe`, { 
      params: { prompt: recipeFormRef.value.fullPrompt }
    })
    .then((resp) => {
      if (img) {
        img.style.display = ''
      }
      console.log(resp.data)
      displayedRecipe.value = resp.data
      if (dataStore.generateImage){
        getImage(resp.data.title, resp.data.image_prompt)
      }
    })
    .catch((err) => {
      console.log('error:', err)
      showError('Recipe failed to generate')
    })
  
  gettingRecipe.value = false
};

async function getImage(imageTitle, imagePrompt){
  imageResponse.value = ''
  gettingImage.value = true
  await axios
    .post(`${dataStore.backendServer}/image`, { title: imageTitle, prompt: imagePrompt, user_id: dataStore.userId })
    .then((resp) => {
      console.log(resp.data)
      imageResponse.value = resp.data
      imageSrc.value = "data:image/png;base64," + resp.data.img
    })
    .catch((err) => {
      console.log(err)
      imageResponse.value = 'error'
    })
  gettingImage.value = false
}

const likeRecipe = () => {
  console.log('Liked recipes');
};

const dislikeRecipe = () => {
  console.log('Disliked recipes');
};


</script>

<style>
.app-container {
  display: flex;
  height: 100vh;
}

.header {
  flex: 1;
  display: flex;
  /* min-width: fit-content;  flex-direction: column;  align-items: center;  justify-content: center; */
}

Button {
  border-radius: 10px;
}

ol {
  margin-top: 0;
}

.p-float-label .p-chips .p-inputtext{
  width: 100%;
  overflow: hidden;
}

#generate-button {
  background-color: blue;
}

h2,
h4 {
  margin: 0px;
}

.content {
  background: #fff;
  padding: 20px;
  /* border: 1px solid #ccc; */
  color: #000; /* Explicitly set text color */
}

.p-toast-detail {
  margin: 0;
}

</style>
