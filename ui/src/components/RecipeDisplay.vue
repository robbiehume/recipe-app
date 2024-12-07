<template>
  <div class="recipe-wrapper" v-if="displayedRecipe" ref="contentToExport">
    <h2 class="recipe-title">{{ displayedRecipe.title }}</h2>
    <div id="recipe-container" class="recipe-container" >
    <div v-if="dataStore.generateImage" class="recipe-image">
      <img
        :src="imageSrc"
        :style="{'display': ['', 'error'].includes(imageResponse) || gettingRecipe ? 'none' : ''}"
        id="recipe-img"
        width="200px"
      />
      <div
        v-if="imageResponse == '' && !gettingImage"
        style="width:200px; height: 200px; border: solid 1px"
        class="flex justify-content-center align-items-center text-center"
      ></div>
      <div
        v-else-if="gettingImage"
        style="width:200px; height: 200px; border: solid 1px"
        class="flex flex-column gap-2 justify-content-center align-items-center"
      >
        Generating image...
        <ProgressSpinner />
      </div>
      <div
        v-else-if="imageResponse == 'error'"
        style="width:200px; height: 200px; border: solid 1px"
        class="flex justify-content-center align-items-center text-center"
      >
        <span style="font-size: 15px">Unable to generate image.</span>
      </div>
    </div>
    <div class="ingredients-container flex-column align-items-center">
      <div class="pb-2"><b>Servings</b>: {{ displayedRecipe.servings }}</div>
      <div class="pb-1">
        <b>Ingredients</b> ({{ displayedRecipe.ingredients.length }}):
      </div>
      <ul ref="listContainer" :style="listStyle" class="ingredients-list">
        <li
          v-for="ingredient of displayedRecipe.ingredients"
          :key="ingredient"
          class="pb-1"
        >
          {{ ingredient }}
        </li>
      </ul>
    </div>
    </div>
    <div id="instructions-div">
      <h4 class="pt-2">Instructions:</h4>
      <ol>
        <li
          v-for="instruction of displayedRecipe.instructions"
          :key="instruction"
          class="pt-1"
        >
          {{ instruction }}
        </li>
      </ol>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import ProgressSpinner from 'primevue/progressspinner';
import { useDataStore } from '@/stores/dataStore';

const dataStore = useDataStore();

onMounted(() => {
  nextTick(() => {   // Use nextTick to ensure the DOM is updated before checking the height
    listStyle.value;  // Update the computed property by referencing the height
  });
});

const props = defineProps([
  'displayedRecipe',
  'imageSrc',
  'imageResponse',
  'gettingRecipe',
  'gettingImage',
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
    columnGap: '10px',
  };
});

</script>


<style scoped>

.recipe-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.recipe-title {
  text-align: center;
  margin-bottom: 20px;
  font-size: 24px;
  font-weight: bold;
}

.recipe-container {
  display: flex;
  flex-direction: column; /* Stack vertically by default */
  align-items: center;
  justify-content: center; /* Center the elements horizontally */
  gap: 20px; /* Space between image and list */
  max-width: 100%; /* Ensure the container fits within the window */
}

.recipe-image {
  width: 200px;
  height: 200px;
  object-fit: cover;
  align-self: center;
  order: 0; /* Ensure the image is above the list by default */
}

.ingredients-container {
  width: fit-content;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: left; /* Align text to the left */
  order: 1; /* Ensure the ingredients are below the image by default */
}

.ingredients-list {
  column-count: 2; /* Split the list into two columns by default */
  column-gap: 20px;
  list-style-type: disc; /* Add bullet points to list items */
  padding: 0 20px; /* Add padding to align bullet points properly */
  margin: 0;
  height: 100%; /* Utilize full height of the container */
}

@media (min-width: 601px) {
  .recipe-container {
    flex-direction: row; /* Side by side on larger screens */
    justify-content: center; /* Center the elements horizontally */
    align-items: flex-start;
  }

  .recipe-image {
    order: 1; /* Move the image to the right */
    margin-left: 20px; /* Optional: add space between the list and the image */
  }

  .ingredients-container {
    order: 0; /* Keep the ingredients container on the left */
    height: 100%; /* Match the height of the image */
  }

  .ingredients-list {
    column-count: 2; /* Ensure the list stays in two columns */
    height: 100%; /* Match the height of the image */
    display: flex;
    flex-direction: column;
    justify-content: space-between; /* Distribute the items evenly */
  }
}

@media (max-width: 600px) {
  .ingredients-list {
    column-count: 2; /* Keep the list split into columns even when below the image */
  }
}
</style>