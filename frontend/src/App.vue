<template>
  <div class="app-container">
    <Navbar />
    <main class="main-wrapper">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from './components/Navbar.vue'
import { useFrappeApi } from './composables/useFrappeApi'

const router = useRouter()
const { boot } = useFrappeApi()

onMounted(async () => {
  await boot()

  // Global Keyboard shortcuts
  window.addEventListener('keydown', (e) => {
    // If inside an active text/number input, don't hijack simple keys
    const tag = document.activeElement ? document.activeElement.tagName.toLowerCase() : ''
    const isEditing = ['input', 'textarea', 'select'].includes(tag)

    if (e.key === 'F9') {
      e.preventDefault()
      router.push('/purchase')
    } else if (e.key === 'F8') {
      e.preventDefault()
      router.push('/sell')
    } else if (e.altKey && (e.key === 'l' || e.key === 'L')) {
      e.preventDefault()
      router.push('/registers')
    }
  })
})
</script>
