<template>
  <div class="flex flex-column gap-3">
    <div class="flex justify-content-center"><h1>Recipe Helper</h1></div>
    <div class="flex" style="height: fit-content;">
      <FloatLabel>    
        <Textarea @keydown="handleKeyDown" rows="1" id="prompt" class="" style="min-height: fit-content; max-height:150px; width: 90vw; max-width: 1000px; min-width: 400px;" autoResize v-model="prompt" />
          <label class="pt-1 label-sm" for="prompt">Prompt</label>
      </FloatLabel>  
    </div>
    <div class="flex card gap-2 justify-content-between align-items-start mt-2">
      <div style="width: 100%;" class="">
        <FloatLabel>
          <Chips v-model="ingredients" id="ingredients" separator=","  />
          <label class="label-sm" for="ingredients">Ingredients (press enter or a comma after each one)</label>
        </FloatLabel>
      </div>
    </div>
    <div class="flex card gap-2 justify-content-center align-items-center mt-2 flex-wrap">
      <div class="flex align-items-center gap-2">
        <span style="width: fit-content; align-self: center; text-align: center">Maximum ingredients:</span>
        <InputNumber class="input-number" ref="inputNumberRef" v-model="maxIngredients" showButtons :min="0" :max="20" />
      </div>
      <div class="flex align-items-center gap-2">
        <span style="align-self: center">Servings:</span>
        <InputNumber style="height:" class="input-number" ref="servingsRef" v-model="servings" showButtons :min="0" :max="20" />
      </div>
      <div class="flex align-items-center gap-2">
        Diet(s): 
        <InputText @keydown.enter="getRecipe()" class="growing-input px-1" :style="{ width: inputWidth + 'ch' }" style="max-height:30px; text-align:center" v-model="diets"  />
      </div>
      <div class="flex align-items-center">
        <label for="gen-image" class="mr-2"> Generate image: </label>
        <InputSwitch id="gen-image" v-model="dataStore.generateImage" />
      </div>
    </div>
  </div> 
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue';
import Textarea from 'primevue/textarea';
import InputText from 'primevue/inputtext';
import Chips from 'primevue/chips';
import FloatLabel from 'primevue/floatlabel';
import InputNumber from 'primevue/inputnumber';
import InputSwitch from 'primevue/inputswitch';
import { useDataStore } from '@/stores/dataStore';

const dataStore = useDataStore();

const emit = defineEmits(['get-recipe']);

// Form data
const prompt = ref('');
const ingredients = ref([]);
const maxIngredients = ref();
const inputNumberRef = ref(null);
const servings = ref(4);
const servingsRef = ref(null);
const diets = ref('');

const inputWidth = computed(() =>
  Math.min(Math.max(diets.value.length + 1, 6), 12)
);

const fullPrompt = computed(() => {
  let _prompt = '';
  if (prompt.value.length > 0) _prompt += 'Prompt: ' + prompt.value + '. ';
  if (ingredients.value.length > 0) _prompt += 'Ingredients: ' + ingredients.value.join(', ') + '. ';
  if (_prompt === '') _prompt = 'Prompt: Random new recipe you haven\'t suggested in awhile. ';
  if (maxIngredients.value > 0) _prompt += 'Maximum ingredients: ' + maxIngredients.value + '. ';
  if (servings.value > 0) _prompt += 'Servings: ' + servings.value + '. ';
  if (diets.value) _prompt += 'Diets: ' + diets.value + '. ';
  return _prompt.slice(0, -1);
});

const emptyPromptAndIngredients = computed(() => {
  return prompt.value == '' && ingredients.value.length == 0
});

defineExpose({
  fullPrompt,
  emptyPromptAndIngredients,
});

watch(maxIngredients, (newVal) => {
  checkInputValue(maxIngredients, inputNumberRef, newVal) 
})

watch(servings, (newVal) => {
  checkInputValue(servings, servingsRef, newVal)
})

function checkInputValue(valueRef, componentRef, newVal){
  if (newVal == 0) {
    valueRef.value = null
  }
  setCursorPosition(componentRef); 
}

// Set cursor to end of input
const setCursorPosition = (componentRef) => {
  nextTick(() => {
    const inputElement = componentRef.value.$el.querySelector('input');
    if (inputElement) {
      const length = inputElement.value.length;
      inputElement.setSelectionRange(length, length);
      inputElement.focus();
    }
  });
};

// While inside Textarea: submit if enter key pressed; enter new line if shift+enter
const handleKeyDown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    emit('get-recipe', fullPrompt.value);
  }
};

</script>


<style>

.p-inputtext.p-inputnumber-input {
  width: 50px; /* Adjust the width as needed */
  padding: 8px 14px 8px 0;
  text-align: center;
}

.p-inputnumber {
  width: 50px;
  height: 30px
}

.p-inputnumber-button {
  width: 20px
}

</style>


<style scoped>

.growing-input {
  min-width: 6ch; 
  max-width: 12ch; 
  overflow: hidden; 

}
.p-chips {
  width: 100%;
  /* width: 50vw */
  /* width: 20rem; */
}

/* .p-chips .p-chips-multiple-container .p-chips-input-token input, */
.p-chips .p-chips-multiple-container .p-chips-input-token {
  width: 25%;
}

.label-sm {
  font-size: 15px;
}

</style>