<template>
  <div class="recipe-display">
    <div v-if="gettingRecipe" class="recipe-wrapper loading-state">
      <div class="skeleton-title"></div>
      <div class="recipe-metadata">
        <div class="servings-badge skeleton-badge">
          <div class="skeleton-line" style="width: 100px; height: 16px"></div>
        </div>
      </div>
      <div v-if="dataStore.generateImage" class="recipe-image-container">
        <div class="skeleton-image"></div>
      </div>
      <div class="recipe-content">
        <div class="ingredients-section">
          <div class="section-header">
            <div class="badge-container">
              <div class="ingredients-badge skeleton-badge">
                <div
                  class="skeleton-line"
                  style="width: 120px; height: 16px"
                ></div>
              </div>
            </div>
          </div>
          <div class="ingredients-list-container">
            <div class="skeleton-ingredients-list">
              <div class="skeleton-line mb-2"></div>
              <div class="skeleton-line mb-2"></div>
              <div class="skeleton-line mb-2"></div>
              <div class="skeleton-line mb-2"></div>
            </div>
            <div class="skeleton-ingredients-list">
              <div class="skeleton-line mb-2"></div>
              <div class="skeleton-line mb-2"></div>
              <div class="skeleton-line mb-2"></div>
              <div class="skeleton-line mb-2"></div>
            </div>
          </div>
        </div>
      </div>
      <div id="instructions-div">
        <div class="section-header">
          <div class="badge-container">
            <div class="instructions-badge skeleton-badge">
              <div
                class="skeleton-line"
                style="width: 120px; height: 16px"
              ></div>
            </div>
          </div>
        </div>
        <div class="skeleton-instructions">
          <div class="skeleton-instruction-item">
            <div class="skeleton-line"></div>
          </div>
          <div class="skeleton-instruction-item">
            <div class="skeleton-line"></div>
          </div>
          <div class="skeleton-instruction-item">
            <div class="skeleton-line"></div>
          </div>
          <div class="skeleton-instruction-item">
            <div class="skeleton-line"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="recipe-wrapper" v-if="displayedRecipe" ref="contentToExport">
      <h2 class="recipe-title">{{ displayedRecipe.title }}</h2>

      <div class="recipe-metadata">
        <div class="servings-badge">
          <i class="pi pi-users mr-2"></i>
          <span><b>Servings</b>: {{ displayedRecipe.servings }}</span>
        </div>
      </div>

      <div v-if="dataStore.generateImage" class="recipe-image-container">
        <img
          :src="imageSrc"
          :style="{
            display:
              ['', 'error'].includes(imageResponse) || gettingRecipe
                ? 'none'
                : '',
          }"
          id="recipe-img"
          class="recipe-image"
        />
        <div
          v-if="imageResponse == '' && !gettingImage"
          class="recipe-image-placeholder flex justify-content-center align-items-center text-center"
        ></div>
        <div
          v-else-if="gettingImage"
          class="recipe-image-placeholder flex flex-column gap-2 justify-content-center align-items-center"
        >
          Generating image...
          <ProgressSpinner />
        </div>
        <div
          v-else-if="imageResponse == 'error'"
          class="recipe-image-placeholder flex justify-content-center align-items-center text-center"
        >
          <span style="font-size: 15px">Unable to generate image.</span>
        </div>
      </div>

      <div class="recipe-content">
        <div class="ingredients-section">
          <div class="section-header">
            <div class="badge-container">
              <div class="ingredients-badge">
                <i class="pi pi-shopping-cart mr-2"></i>
                <span
                  ><b>Ingredients</b> ({{
                    displayedRecipe.ingredients.length
                  }})</span
                >
              </div>
            </div>
          </div>
          <div class="ingredients-list-container">
            <ul class="ingredients-list" :class="ingredientsListClass">
              <li
                v-for="(ingredient, index) in leftColumnIngredients"
                :key="`left-${index}`"
                class="ingredient-item"
              >
                {{ ingredient }}
              </li>
            </ul>
            <ul v-if="showTwoColumns" class="ingredients-list">
              <li
                v-for="(ingredient, index) in rightColumnIngredients"
                :key="`right-${index}`"
                class="ingredient-item"
              >
                {{ ingredient }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div id="instructions-div">
        <div class="section-header">
          <div class="badge-container">
            <div class="instructions-badge">
              <i class="pi pi-list mr-2"></i>
              <span><b>Instructions</b></span>
            </div>
          </div>
        </div>
        <ol>
          <li
            v-for="instruction of displayedRecipe.instructions"
            :key="instruction"
            class="instruction-item"
          >
            {{ instruction }}
          </li>
        </ol>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch, onUnmounted } from "vue";
import ProgressSpinner from "primevue/progressspinner";
import { useDataStore } from "@/stores/dataStore";

const dataStore = useDataStore();

const props = defineProps([
  "displayedRecipe",
  "imageSrc",
  "imageResponse",
  "gettingRecipe",
  "gettingImage",
]);

const listContainer = ref(null);
const thresholdHeight = 150;

const contentToExport = ref(null);

defineExpose({
  contentToExport,
});

const listStyle = computed(() => {
  const currentHeight = listContainer.value?.offsetHeight || 0;
  return {
    columnCount: currentHeight > thresholdHeight ? 2 : 1,
    columnGap: "10px",
  };
});

const showTwoColumns = ref(false);

// Compute whether to show in two columns based on number of ingredients and screen size
const ingredientsListClass = computed(() => {
  return { "single-column": !showTwoColumns.value };
});

// Split ingredients into two balanced columns
const leftColumnIngredients = computed(() => {
  if (!props.displayedRecipe) return [];

  if (!showTwoColumns.value) {
    return props.displayedRecipe.ingredients;
  }

  const halfLength = Math.ceil(props.displayedRecipe.ingredients.length / 2);
  return props.displayedRecipe.ingredients.slice(0, halfLength);
});

const rightColumnIngredients = computed(() => {
  if (!props.displayedRecipe || !showTwoColumns.value) return [];

  const halfLength = Math.ceil(props.displayedRecipe.ingredients.length / 2);
  return props.displayedRecipe.ingredients.slice(halfLength);
});

// Determine column layout based on ingredient count and container size
const updateColumnLayout = () => {
  if (!props.displayedRecipe) return;

  const ingredientCount = props.displayedRecipe.ingredients.length;
  const isMobile = window.innerWidth <= 600;

  // Use two columns if there are more than 4 ingredients and not on mobile,
  // or if there are more than 6 ingredients on mobile
  showTwoColumns.value =
    (ingredientCount > 4 && !isMobile) || ingredientCount > 6;
};

// Watch for changes in the recipe and update layout
watch(
  () => props.displayedRecipe,
  () => {
    nextTick(() => {
      updateColumnLayout();
    });
  },
  { immediate: true }
);

// Update layout on window resize
onMounted(() => {
  window.addEventListener("resize", updateColumnLayout);
  nextTick(() => {
    updateColumnLayout();
  });
});

// Clean up event listener
onUnmounted(() => {
  window.removeEventListener("resize", updateColumnLayout);
});
</script>

<style scoped>
.recipe-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 2rem;
  margin-top: 1rem;
}

.recipe-title {
  text-align: center;
  margin-bottom: 20px;
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
}

.recipe-metadata {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.recipe-image-container {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
}

.recipe-image {
  width: 250px;
  height: 250px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.recipe-image-placeholder {
  width: 250px;
  height: 250px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
}

.recipe-content {
  width: 100%;
  max-width: 800px;
  display: flex;
  justify-content: center;
}

.ingredients-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 600px;
}

.section-header {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.badge-container {
  display: inline-flex;
}

.servings-badge,
.ingredients-badge,
.instructions-badge {
  display: flex;
  align-items: center;
  background-color: #f8f9fa;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.95rem;
  color: #2c3e50;
  border: 1px solid #e9ecef;
}

.ingredients-list-container {
  display: flex;
  width: 100%;
  gap: 20px;
  justify-content: center;
}

.ingredients-list {
  list-style-type: disc;
  padding: 0 0 0 20px;
  margin: 0;
  flex: 1;
  max-width: 280px;
}

.ingredients-list.single-column {
  max-width: 560px;
}

.ingredient-item {
  padding-bottom: 0.5rem;
  line-height: 1.5;
  break-inside: avoid;
}

.instruction-item {
  padding-top: 0.5rem;
  line-height: 1.5;
}

#instructions-div {
  width: 100%;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef;
  max-width: 800px;
}

/* Loading state styles */
.loading-state {
  opacity: 0.7;
}

.skeleton-title,
.skeleton-line {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
}

.skeleton-title {
  height: 32px;
  width: 70%;
  margin: 0 auto 20px auto;
}

.skeleton-image {
  width: 200px;
  height: 200px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

.skeleton-ingredients {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  width: 100%;
  margin-top: 10px;
}

.skeleton-line {
  height: 16px;
  width: 100%;
}

.skeleton-instructions {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@media (max-width: 768px) {
  .recipe-image {
    width: 220px;
    height: 220px;
  }

  .recipe-image-placeholder {
    width: 220px;
    height: 220px;
  }

  .ingredients-list {
    max-width: 240px;
  }

  .ingredients-list.single-column {
    max-width: 480px;
  }
}

@media (max-width: 480px) {
  .recipe-wrapper {
    padding: 1rem;
  }

  .recipe-title {
    font-size: 22px;
  }

  .recipe-image,
  .recipe-image-placeholder {
    width: 180px;
    height: 180px;
  }

  .servings-badge,
  .ingredients-badge,
  .instructions-badge {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }

  .ingredients-list {
    max-width: 100%;
  }

  .ingredients-list.single-column {
    max-width: 100%;
  }
}

/* Add these new skeleton styles */
.skeleton-badge {
  display: flex;
  align-items: center;
  background-color: #f8f9fa;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  border: 1px solid #e9ecef;
}

.skeleton-ingredients-list {
  flex: 1;
  max-width: 280px;
  padding-left: 20px;
}

.skeleton-instruction-item {
  display: flex;
  padding: 0.5rem 0;
  position: relative;
  padding-left: 24px;
}

.skeleton-instruction-item::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0.75rem;
  width: 16px;
  height: 16px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 50%;
}
</style>
