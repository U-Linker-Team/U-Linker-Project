import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: () => import('../components/loginPage.vue')
  },
  {
    path: '/login',
    redirect: '/'
  },
  {
    path: '/register', 
    name: 'Register',
    component: () => import('../components/RegisterPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router