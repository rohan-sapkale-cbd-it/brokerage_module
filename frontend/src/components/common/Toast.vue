<template>
  <div v-if="globalUiState.toastVisible.value" class="toast-box">
    <span>ℹ️</span>
    <span>{{ globalUiState.toastMessage.value }}</span>
  </div>
</template>

<script setup>
import { globalUiState } from '../../composables/useKeyboardEngine'
</script>

