import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/members',
    name: 'Members',
    component: () => import('../views/Members.vue')
  },
  {
    path: '/members/add',
    name: 'AddMember',
    component: () => import('../views/AddMember.vue')
  },
  {
    path: '/members/:id',
    name: 'MemberDetail',
    component: () => import('../views/MemberDetail.vue')
  },
  {
    path: '/members/:id/edit',
    name: 'EditMember',
    component: () => import('../views/EditMember.vue')
  },
  {
    path: '/memos',
    name: 'Memos',
    component: () => import('../views/Memos.vue')
  },
  {
    path: '/memos/:id',
    name: 'MemoDetail',
    component: () => import('../views/MemoDetail.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue')
  }
]

const router = createRouter({
  history: createWebHistory('/family_notebook/'),
  routes
})

export default router
