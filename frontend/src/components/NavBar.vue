<template>
  <header class="navbar">
    <div class="container">
      <router-link to="/" class="logo">
        🏠 温馨家庭记事本
      </router-link>

      <button class="menu-toggle" @click="toggleMenu" :class="{ active: isMenuOpen }">
        <span></span>
        <span></span>
        <span></span>
      </button>

      <nav class="nav-menu" :class="{ active: isMenuOpen }">
        <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }" @click="closeMenu">
          🏡 首页
        </router-link>
        <router-link to="/memos" class="nav-link" :class="{ active: $route.path.startsWith('/memos') }" @click="closeMenu">
          📝 备忘录
        </router-link>
        <router-link to="/members/add" class="nav-link btn-add" :class="{ active: $route.path === '/members/add' }" @click="closeMenu">
          ➕ 添加家人
        </router-link>
        <router-link to="/settings" class="nav-link" :class="{ active: $route.path === '/settings' }" @click="closeMenu">
          ⚙️ 设置
        </router-link>
      </nav>

      <div class="overlay" :class="{ active: isMenuOpen }" @click="closeMenu"></div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'

const isMenuOpen = ref(false)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
  document.body.style.overflow = isMenuOpen.value ? 'hidden' : ''
}

const closeMenu = () => {
  isMenuOpen.value = false
  document.body.style.overflow = ''
}
</script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #E8C4A0 0%, #E6B89A 100%);
  padding: 15px 0;
  box-shadow: 0 4px 20px rgba(232, 196, 160, 0.3);
  border-radius: 0 0 24px 24px;
  margin: 0 10px;
  max-width: calc(100% - 20px);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  color: #FFF;
  font-size: 1.4rem;
  font-weight: 500;
  text-decoration: none;
  letter-spacing: 1px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-menu {
  display: flex;
  gap: 10px;
  align-items: center;
}

.nav-link {
  color: #FFF;
  text-decoration: none;
  padding: 10px 20px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.15);
  transition: all 0.25s ease;
  font-weight: 400;
  font-size: 0.95rem;
  backdrop-filter: blur(4px);
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.28);
  transform: translateY(-2px);
}

.nav-link.active {
  background: rgba(255, 255, 255, 0.35);
}

.btn-add {
  background: rgba(255, 255, 255, 0.95) !important;
  color: #D4A574 !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.btn-add:hover {
  background: white !important;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.menu-toggle {
  display: none;
  flex-direction: column;
  justify-content: space-around;
  width: 28px;
  height: 24px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 110;
}

.menu-toggle span {
  width: 100%;
  height: 2px;
  background: white;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.menu-toggle.active span:nth-child(1) {
  transform: rotate(45deg) translate(6px, 6px);
}

.menu-toggle.active span:nth-child(2) {
  opacity: 0;
}

.menu-toggle.active span:nth-child(3) {
  transform: rotate(-45deg) translate(6px, -6px);
}

.overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 99;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.overlay.active {
  display: block;
  opacity: 1;
}

@media (max-width: 768px) {
  .menu-toggle {
    display: flex;
  }

  .nav-menu {
    position: fixed;
    top: 0;
    right: -100%;
    width: 280px;
    height: 100vh;
    background: linear-gradient(180deg, #E8C4A0 0%, #D4A574 100%);
    flex-direction: column;
    padding: 80px 20px 20px;
    gap: 12px;
    transition: right 0.3s ease;
    z-index: 100;
    box-shadow: -2px 0 20px rgba(0, 0, 0, 0.1);
    align-items: stretch;
    border-radius: 24px 0 0 24px;
  }

  .nav-menu.active {
    right: 0;
  }

  .nav-link {
    padding: 14px 18px;
    font-size: 1rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    text-align: center;
  }
}
</style>
