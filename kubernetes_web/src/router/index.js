import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    roles: ['admin','editor']    control the page roles (you can set multiple roles)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'             the icon show in the sidebar
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },

  {
    path: '/404',
    component: () => import('@/views/404'),
    hidden: true
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [{
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/dashboard/index'),
      meta: { title: '主页', icon: 'dashboard' }
    }]
  }
]

/**
 * asyncRoutes
 * the routes that need to be dynamically loaded based on user roles
 */
export const asyncRoutes = [
  {
    path: '/cluster',
    component: Layout,
    redirect: '/cluster/',
    name: 'cluster',
    meta: { title: '集群', icon: 'Kubernetes_logo', roles: ['superuser'] },
    children: [
      {
        path: 'clusterconfig',
        name: 'clusterconfig',
        component: () => import('@/views/cluster/index'),
        meta: { title: '集群配置', icon: 'Kubernetes_logo', roles: ['superuser'] }
      }
    ]
  },
  {
    path: '/kubernetes',
    component: Layout,
    redirect: '/kubernetes/',
    name: 'kubernetes',
    meta: { title: 'kubernetes_' + process.env.VUE_APP_K8S_TAG + '集群', icon: 'Kubernetes_logo' },
    children: [
      {
        path: 'node',
        name: 'node',
        component: () => import('@/views/kubernetes/node/index'),
        meta: { title: '计算节点', icon: 'Cloud Storage' }
      },
      {
        path: 'pod',
        name: 'pod',
        component: () => import('@/views/kubernetes/pod/index'),
        meta: { title: '容器', icon: 'Cloud Storage' }
      },
      {
        path: 'webterminal',
        name: 'SSH',
        component: () => import('@/views/kubernetes/webterminal/index'),
        meta: { title: 'SSH', icon: 'Kubernetes_logo' },
        hidden: true
      },
      {
        path: 'containerlog',
        name: 'LOG',
        component: () => import('@/views/kubernetes/containerlog/index'),
        meta: { title: 'LOG', icon: 'Kubernetes_logo' },
        hidden: true
      },
      {
        path: 'svc',
        name: 'svc',
        component: () => import('@/views/kubernetes/svc/index'),
        meta: { title: '服务', icon: 'Cloud Load Balancing' }
      },
      {
        path: 'deployment',
        name: 'deployment',
        component: () => import('@/views/kubernetes/deployment/index'),
        meta: { title: '部署集', icon: 'Kubernetes_logo' }
      },
      {
        path: 'statefulset',
        name: 'statefulset',
        component: () => import('@/views/kubernetes/statefulset/index'),
        meta: { title: '有状态副本集', icon: 'Kubernetes_logo' }
      }
    ]
  },
  {
    path: '/items',
    component: Layout,
    redirect: '/items/',
    name: 'items',
    meta: { title: '立项管理', icon: 'Kubernetes_logo' },
    children: [
      {
        path: 'project',
        name: 'project',
        component: () => import('@/views/items/project/index'),
        meta: { title: '项目立项', icon: 'Kubernetes_logo' }
      }
    ]
  },
  {
    path: '/user',
    component: Layout,
    redirect: '/user/',
    name: 'user',
    meta: { title: '用户管理', icon: 'Kubernetes_logo', roles: ['superuser'] },
    children: [
      {
        path: 'userlist',
        name: 'userlist',
        component: () => import('@/views/users/userlist/index'),
        meta: { title: '用户列表', icon: 'Kubernetes_logo' }
      },
      {
        path: 'userpermission',
        name: 'userpermission',
        component: () => import('@/views/users/userpermission/index'),
        meta: { title: 'k8s权限', icon: 'Kubernetes_logo' }
      }
    ]
  },
  // 404 page must be placed at the end !!!
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  // mode: 'history', // require service support
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export default router
