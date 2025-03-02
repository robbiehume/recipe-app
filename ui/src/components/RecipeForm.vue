<template>
  <div class="recipe-form-container">
    <div class="form-header">
      <h1>Recipe Helper</h1>
      <p class="form-subtitle">
        Enter a prompt, ingredients, or both to generate a custom recipe
      </p>
    </div>

    <div class="form-card">
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
          <label class="label-sm" for="prompt">
            Prompt <span class="required-indicator">*</span>
          </label>
        </FloatLabel>
        <small class="helper-text"
          >Required for custom recipe (or use ingredients below)</small
        >
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
            Ingredients <span class="required-indicator">*</span>
          </label>
        </FloatLabel>
        <small class="helper-text"
          >Required for custom recipe (or use prompt above)</small
        >
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
              placeholder="e.g., vegan"
            />
          </div>

          <div class="option-item">
            <label for="gen-image">Generate image:</label>
            <InputSwitch id="gen-image" v-model="dataStore.generateImage" />
          </div>
        </div>
      </div>

      <div class="form-note">
        <i class="pi pi-info-circle"></i>
        <span
          >Leave both prompt and ingredients empty to generate a random
          recipe</span
        >
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

const inputWidth = computed(() =>
  Math.min(Math.max(diets.value.length + 1, 6), 12)
);

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
}

.options-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  justify-content: center;
  align-items: center;
  max-width: 800px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  white-space: nowrap;
}

.diet-container {
  width: 180px;
}

.diet-input {
  flex: 1;
  min-width: 80px;
  border-radius: 8px;
  text-align: center;
  height: 30px;
}

.label-sm {
  font-size: 15px;
}

.p-chips .p-chips-multiple-container .p-chips-input-token {
  width: 25%;
}

@media (max-width: 992px) {
  .options-container {
    max-width: 700px;
  }
}

@media (max-width: 768px) {
  .options-container {
    flex-direction: column;
    align-items: flex-start;
    width: 100%;
  }

  .option-item {
    width: 100%;
    justify-content: space-between;
  }

  .diet-container {
    width: 100%;
  }
}

.form-subtitle {
  font-size: 0.95rem;
  color: #6c757d;
  margin: 0.5rem 0 0;
}

.required-indicator {
  color: #4361ee;
  margin-left: 2px;
}

.helper-text {
  display: block;
  color: #6c757d;
  font-size: 0.8rem;
  margin-top: 0.25rem;
  margin-left: 0.25rem;
}

.form-note {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: rgba(67, 97, 238, 0.08);
  border-radius: 8px;
  font-size: 0.9rem;
  color: #4361ee;
}

.form-note i {
  font-size: 1rem;
}
</style>
