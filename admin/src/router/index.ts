import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/login/index.vue"),
    meta: { title: "登录" },
  },
  {
    path: "/",
    component: () => import("@/layouts/DefaultLayout.vue"),
    redirect: "/dashboard",
    children: [
      {
        path: "dashboard",
        name: "Dashboard",
        component: () => import("@/views/dashboard/index.vue"),
        meta: { title: "数据概览" },
      },
      {
        path: "products",
        name: "Products",
        component: () => import("@/views/products/index.vue"),
        meta: { title: "产品管理" },
      },
      {
        path: "categories",
        name: "Categories",
        component: () => import("@/views/categories/index.vue"),
        meta: { title: "分类管理" },
      },
      {
        path: "orders",
        name: "Orders",
        component: () => import("@/views/orders/index.vue"),
        meta: { title: "订单管理" },
      },
      {
        path: "catalogs",
        name: "Catalogs",
        component: () => import("@/views/catalogs/index.vue"),
        meta: { title: "资料管理" },
      },
      {
        path: "ai-chat",
        name: "AiChat",
        component: () => import("@/views/ai-chat/index.vue"),
        meta: { title: "AI对话记录" },
      },
      {
        path: "settings",
        name: "Settings",
        component: () => import("@/views/settings/index.vue"),
        meta: { title: "系统设置" },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
