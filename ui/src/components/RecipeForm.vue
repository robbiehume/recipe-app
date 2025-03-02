<template>
  <div class="recipe-form-container">
    <div class="form-header">
      <h1>Recipe Helper</h1>
    </div>

    <div class="form-card">
      <div class="form-instructions">
        Enter a prompt, ingredients, or both to generate a custom recipe. Leave
        both empty for a random recipe.
      </div>

      <div class="prompt-section">
        <FloatLabel>
          <Textarea
            @keydown="handleKeyDown"
            rows="1"
            id="prompt"
            class="prompt-input"
            autoResize
            v-model="prompt"
            placeholder="Describe what you're looking for..."
          />
          <label class="label-sm pt-1" for="prompt"
            >Prompt <span class="required-indicator">*</span></label
          >
        </FloatLabel>
      </div>

      <div class="ingredients-section">
        <FloatLabel>
          <Chips
            v-model="ingredients"
            id="ingredients"
            separator=","
            placeholder="Add ingredients..."
            class="ingredients-input"
          />
          <label class="label-sm" for="ingredients">
            Ingredients (press enter or a comma after each one)
            <span class="required-indicator">*</span>
          </label>
        </FloatLabel>
        <small class="helper-text">
          <span class="required-indicator">*</span> At least one of these fields
          is required for a custom recipe
        </small>
      </div>

      <div class="options-section">
        <div class="options-container">
          <div class="option-item">
            <span>Maximum ingredients:</span>
            <InputNumber
              class="input-number"
              ref="inputNumberRef"
              v-model="maxIngredients"
              showButtons
              :min="0"
              :max="20"
            />
          </div>

          <div class="option-item">
            <span>Servings:</span>
            <InputNumber
              class="input-number"
              ref="servingsRef"
              v-model="servings"
              showButtons
              :min="0"
              :max="20"
            />
          </div>

          <div class="option-item diet-container">
            <span>Diet(s):</span>
            <InputText
              @keydown.enter="getRecipe()"
              class="diet-input"
              v-model="diets"
              :style="{ width: `${inputWidth}ch` }"
            />
          </div>

          <div class="option-item image-toggle">
            <label for="gen-image">Generate image:</label>
            <InputSwitch
              id="gen-image"
              v-model="dataStore.generateImage"
              class="blue-switch"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from "vue";
import Textarea from "primevue/textarea";
import InputText from "primevue/inputtext";
import Chips from "primevue/chips";
import FloatLabel from "primevue/floatlabel";
import InputNumber from "primevue/inputnumber";
import InputSwitch from "primevue/inputswitch";
import { useDataStore } from "@/stores/dataStore";

const dataStore = useDataStore();

const emit = defineEmits(["get-recipe"]);

// Form data
const prompt = ref("");
const ingredients = ref([]);
const maxIngredients = ref();
const inputNumberRef = ref(null);
const servings = ref(4);
const servingsRef = ref(null);
const diets = ref("");

const inputWidth = computed(() => {
  const placeholderLength = "Paleo, Veg., etc.".length;
  const contentLength = diets.value.length;
  return Math.max(contentLength + 2, placeholderLength + 2);
});

const fullPrompt = computed(() => {
  let _prompt = "";
  if (prompt.value.length > 0) _prompt += "Prompt: " + prompt.value + ". ";
  if (ingredients.value.length > 0)
    _prompt += "Ingredients: " + ingredients.value.join(", ") + ". ";
  if (_prompt === "")
    _prompt = "Prompt: Random new recipe you haven't suggested in awhile. ";
  if (maxIngredients.value > 0)
    _prompt += "Maximum ingredients: " + maxIngredients.value + ". ";
  if (servings.value > 0) _prompt += "Servings: " + servings.value + ". ";
  if (diets.value) _prompt += "Diets: " + diets.value + ". ";
  return _prompt.slice(0, -1);
});

const emptyPromptAndIngredients = computed(() => {
  return prompt.value == "" && ingredients.value.length == 0;
});

defineExpose({
  fullPrompt,
  emptyPromptAndIngredients,
});

watch(maxIngredients, (newVal) => {
  checkInputValue(maxIngredients, inputNumberRef, newVal);
});

watch(servings, (newVal) => {
  checkInputValue(servings, servingsRef, newVal);
});

function checkInputValue(valueRef, componentRef, newVal) {
  if (newVal == 0) {
    valueRef.value = null;
  }
  setCursorPosition(componentRef);
}

// Set cursor to end of input
const setCursorPosition = (componentRef) => {
  nextTick(() => {
    const inputElement = componentRef.value.$el.querySelector("input");
    if (inputElement) {
      const length = inputElement.value.length;
      inputElement.setSelectionRange(length, length);
      inputElement.focus();
    }
  });
};

// While inside Textarea: submit if enter key pressed; enter new line if shift+enter
const handleKeyDown = (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    emit("get-recipe", fullPrompt.value);
  }
};
</script>

<style>
.p-inputtext.p-inputnumber-input {
  width: 50px;
  padding: 8px 14px 8px 0;
  text-align: center;
}

.p-inputnumber {
  width: 50px;
  height: 30px;
}

.p-inputnumber-button {
  width: 20px;
}
</style>

<style scoped>
.recipe-form-container {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
}

.form-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.form-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.form-card {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-instructions {
  margin-bottom: 1.5rem;
  color: #6c757d;
  font-size: 0.9rem;
  text-align: center;
  line-height: 1.5;
}

.required-indicator {
  color: #4361ee;
  font-weight: bold;
}

.helper-text {
  display: block;
  color: #6c757d;
  font-size: 0.8rem;
  margin-top: 0.5rem;
  font-style: italic;
}

.prompt-section {
  margin-bottom: 1.5rem;
}

.prompt-input {
  min-height: fit-content;
  max-height: 150px;
  width: 100%;
  border-radius: 8px;
}

.ingredients-section {
  margin-bottom: 1.5rem;
}

.ingredients-input {
  width: 100%;
  border-radius: 8px;
}

.options-section {
  display: flex;
  justify-content: center;
  width: 100%;
  overflow-x: auto;
}

.options-container {
  display: flex;
  flex-wrap: nowrap;
  gap: 1rem;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
}

.diet-container {
  flex: 1;
  min-width: 120px;
}

.diet-input {
  min-width: 80px;
  border-radius: 8px;
  text-align: center;
  height: 30px;
}

.image-toggle {
  min-width: auto;
}

.label-sm {
  font-size: 15px;
}

.p-chips .p-chips-multiple-container .p-chips-input-token {
  width: 25%;
}

@media (max-width: 768px) {
  .options-container {
    padding-bottom: 0.5rem;
  }

  .option-item {
    flex-shrink: 0;
  }
}

/* Blue styling for the InputSwitch to match the Random Recipe button */
:deep(.blue-switch) .p-inputswitch.p-inputswitch-checked .p-inputswitch-slider {
  background-color: #4361ee !important;
}

:deep(.blue-switch)
  .p-inputswitch.p-inputswitch-checked:not(.p-disabled):hover
  .p-inputswitch-slider {
  background-color: #3a56d4 !important;
}

:deep(.blue-switch) .p-inputswitch.p-focus .p-inputswitch-slider {
  box-shadow: 0 0 0 0.2rem rgba(67, 97, 238, 0.2) !important;
}
</style>
