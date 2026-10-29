import { ref, onMounted } from 'vue'

const isDarkMode = ref(false)

export function useTheme() {
  const initTheme = () => {
    const saved = localStorage.getItem('brokerage_desk_theme')
    if (saved) {
      isDarkMode.value = saved === 'dark'
    } else {
      isDarkMode.value = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    applyTheme()
  }

  const toggleTheme = () => {
    isDarkMode.value = !isDarkMode.value
    localStorage.setItem('brokerage_desk_theme', isDarkMode.value ? 'dark' : 'light')
    applyTheme()
  }

  const applyTheme = () => {
    if (typeof document !== 'undefined') {
      if (isDarkMode.value) {
        document.body.classList.add('dark-mode')
        document.documentElement.classList.add('dark-mode')
      } else {
        document.body.classList.remove('dark-mode')
        document.documentElement.classList.remove('dark-mode')
      }
    }
  }

  onMounted(() => {
    initTheme()
  })

  return {
    isDarkMode,
    toggleTheme,
    initTheme,
  }
}

