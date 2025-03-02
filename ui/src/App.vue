<template>
  <div
    class="app-container flex-column align-items-center"
    style="width: 90vw; max-width: 1000px"
  >
    <div class="content-container" style="width: 100%; max-width: 800px">
      <!-- Navigation Area -->
      <div
        class="app-navigation flex justify-content-between mb-3"
        style="width: 100%"
      >
        <SavedRecipesList
          ref="savedRecipesListRef"
          @get-saved-recipe="getSavedRecipe"
          @show-error="showError"
        />
        <Login class="p-0 align-self-end" />
      </div>

      <!-- Main Content Area -->
      <div class="app-content flex-column gap-2">
        <RecipeForm ref="recipeFormRef" @get-recipe="getRecipe" />

        <div class="flex justify-content-center gap-3 action-buttons my-2">
          <Button
            id="generate-button"
            :disabled="gettingRecipe"
            @click="getRecipe()"
            class="p-button-primary"
          >
            <span v-if="gettingRecipe" class="px-3">Generating...</span>
            <span v-else-if="recipeFormRef?.emptyPromptAndIngredients">
              <i class="pi pi-refresh mr-2"></i>Random Recipe
            </span>
            <span v-else> <i class="pi pi-book mr-2"></i>Generate Recipe </span>
          </Button>

          <Button
            :disabled="displayedRecipe === ''"
            id="save-button"
            severity="secondary"
            @click="saveRecipe()"
            class="p-button-outlined"
          >
            <i class="pi pi-save mr-2"></i>Save Recipe
          </Button>

          <Button
            :disabled="displayedRecipe === ''"
            severity="secondary"
            @click="exportToPDF"
            class="p-button-outlined"
          >
            <i class="pi pi-file-pdf mr-2"></i>Export to PDF
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
    </div>
    <Toast style="width: fit-content" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import "primeflex/primeflex.css";
import { useDataStore } from "@/stores/dataStore";
import SavedRecipesList from "@/components/SavedRecipesList.vue";
import RecipeForm from "@/components/RecipeForm.vue";
import RecipeDisplay from "@/components/RecipeDisplay.vue";
import Login from "@/components/Login.vue";
import axios from "axios";
import Button from "primevue/button";
import jsPDF from "jspdf";
import Toast from "primevue/toast";
import { useToast } from "primevue/usetoast";

const toast = useToast();

const dataStore = useDataStore();

onMounted(() => {
  if (dataStore.isLoggedIn) {
    savedRecipesListRef.value.getUserSavedRecipes();
  }
});

const gettingRecipe = ref(false);
const gettingImage = ref(false);
const imageResponse = ref("");
const imageSrc = ref("");
const displayedRecipe = ref("");

const savedRecipesListRef = ref(null);
const recipeFormRef = ref(null);
const recipeDisplayRef = ref(null);

// const menuItems = ref([
// {label: 'Home', icon: 'pi pi-home'},
// {label: 'Saved Recipes', icon: 'pi pi-star'}
// ])

function showSuccess(message) {
  toast.add({
    severity: "success",
    detail: message,
    life: 3000,
    closable: false,
  });
}

function showError(message) {
  toast.add({
    severity: "error",
    detail: message,
    life: 3000,
    closable: false,
  });
}

async function saveRecipe() {
  if (!dataStore.isLoggedIn) {
    dataStore.showLoginDialog = true;
    return;
  }

  const recipe = displayedRecipe.value;
  console.log("Saved recipes; recipe:", recipe);

  await axios
    .post(`${dataStore.backendServer}/save_recipe`, {
      user_id: dataStore.userId,
      title: recipe.title,
      ingredients: recipe.ingredients,
      instructions: recipe.instructions,
      image_prompt: recipe.image_prompt,
      servings: recipe.servings,
    })
    .then((resp) => {
      console.log("Resp:", resp);
      showSuccess("Recipe saved successfully");
      savedRecipesListRef.value.getUserSavedRecipes();
    })
    .catch((err) => {
      console.log("error:", err);
      showError("Recipe failed to save");
    });
}

async function getSavedRecipe(recipeId) {
  console.log("Getting saved recipe");
  await axios
    .get(`${dataStore.backendServer}/get_saved_recipe`, {
      params: { recipe_id: recipeId },
    })
    .then((resp) => {
      console.log("Resp:", resp);
      displayedRecipe.value = resp.data;
      if (dataStore.generateImage) {
        getSavedImage(resp.data.title);
      }
    })
    .catch((err) => {
      console.log("error:", err);
    });
}

async function getSavedImage(imageTitle) {
  imageResponse.value = "";
  gettingImage.value = true;
  await axios
    .get(`${dataStore.backendServer}/get_saved_image`, {
      params: { title: imageTitle, user_id: dataStore.userId },
    })
    .then((resp) => {
      console.log(resp.data);
      imageResponse.value = resp.data;
      imageSrc.value = "data:image/png;base64," + resp.data.image;
      gettingImage.value = false;
    })
    .catch((err) => {
      console.log(err);
      if (err.response.status === 404) {
        getImage(imageTitle, displayedRecipe.value.image_prompt);
      } else {
        imageResponse.value = "error";
        gettingImage.value = false;
      }
    });
}

const exportToPDF = () => {
  const element = recipeDisplayRef.value.contentToExport;
  const pdf = new jsPDF("p", "mm", "a4");

  pdf.html(element, {
    callback: (doc) => {
      doc.save(`${displayedRecipe.value.title} Recipe.pdf`);
    },
    x: 17,
    y: 10,
    html2canvas: {
      scale: 0.15,
      useCORS: true,
    },
    width: 190,
    windowWidth: element.scrollWidth,
  });
};

watch(
  () => dataStore.generateImage,
  (newVal) => {
    console.log(
      "generateImage change:",
      newVal,
      displayedRecipe.value,
      imageSrc.value
    );
    if (
      newVal === true &&
      displayedRecipe.value !== "" &&
      imageSrc.value === ""
    ) {
      getImage(displayedRecipe.value.title, displayedRecipe.value.image_prompt);
    }
  }
);

async function getRecipe() {
  displayedRecipe.value = "";
  gettingRecipe.value = true;
  const img = document.getElementById("recipe-img");

  if (img) {
    img.style.display = "none";
    console.log(img);
  }

  console.log("fullPrompt:", recipeFormRef.value.fullPrompt);

  await axios
    .get(`${dataStore.backendServer}/generate_recipe`, {
      params: { prompt: recipeFormRef.value.fullPrompt },
    })
    .then((resp) => {
      if (img) {
        img.style.display = "";
      }
      console.log(resp.data);
      displayedRecipe.value = resp.data;
      if (dataStore.generateImage) {
        getImage(resp.data.title, resp.data.image_prompt);
      }
    })
    .catch((err) => {
      console.log("error:", err);
      showError("Recipe failed to generate");
    });

  gettingRecipe.value = false;
}

async function getImage(imageTitle, imagePrompt) {
  imageResponse.value = "";
  gettingImage.value = true;
  await axios
    .post(`${dataStore.backendServer}/image`, {
      title: imageTitle,
      prompt: imagePrompt,
      user_id: dataStore.userId,
    })
    .then((resp) => {
      console.log(resp.data);
      imageResponse.value = resp.data;
      imageSrc.value = "data:image/png;base64," + resp.data.img;
    })
    .catch((err) => {
      console.log(err);
      imageResponse.value = "error";
    });
  gettingImage.value = false;
}

const likeRecipe = () => {
  console.log("Liked recipes");
};

const dislikeRecipe = () => {
  console.log("Disliked recipes");
};
</script>

<style>
/* Add these to your existing styles */
body {
  background-color: #f8f9fa;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica,
    Arial, sans-serif;
}

.app-container {
  display: flex;
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 1rem;
}

/* Improve focus states for accessibility */
:focus-visible {
  outline: 2px solid #4361ee;
  outline-offset: 2px;
}

/* Smooth transitions for all interactive elements */
a,
button,
.p-button,
.p-inputtext,
.p-chips,
.p-inputswitch {
  transition: all 0.2s ease;
}

/* Consistent card styling */
.card {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 1.5rem;
}

/* Toast improvements */
.p-toast {
  opacity: 0.95;
}

.p-toast .p-toast-message {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.header {
  flex: 1;
  display: flex;
}

Button {
  border-radius: 8px;
  transition: all 0.2s ease;
}

Button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

#generate-button {
  background-color: #4361ee;
  border: none;
  font-weight: 600;
  min-width: 161px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.p-button-outlined {
  border: 1px solid #4361ee;
  color: #4361ee;
  background-color: transparent;
}

.p-button-outlined:hover:not(:disabled) {
  background-color: rgba(67, 97, 238, 0.04);
}

.p-toast-detail {
  margin: 0;
}

h2,
h4 {
  margin: 0px;
  color: #2c3e50;
}

.p-float-label .p-chips .p-inputtext {
  width: 100%;
  overflow: hidden;
}

ol {
  margin-top: 0;
}

.content {
  background: #fff;
  padding: 20px;
  color: #000;
}

@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }

  Button {
    width: 100%;
    max-width: 300px;
  }
}

/* Add to your existing styles */
.content-container {
  display: flex;
  flex-direction: column;
}

.app-navigation {
  padding-top: 1rem;
}

.app-content {
  display: flex;
}

/* Override PrimeVue InputSwitch colors globally */
.p-inputswitch.p-inputswitch-checked .p-inputswitch-slider {
  background-color: #4361ee !important;
}

.p-inputswitch.p-inputswitch-checked:not(.p-disabled):hover
  .p-inputswitch-slider {
  background-color: #3a56d4 !important;
}

.p-inputswitch.p-focus .p-inputswitch-slider {
  box-shadow: 0 0 0 0.2rem rgba(67, 97, 238, 0.2) !important;
}
</style>
