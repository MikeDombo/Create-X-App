import Vue from "vue";
import Router from "vue-router";
import Main from "@/components/Main";
import Template from "@/components/Template";

Vue.use(Router);

const router = new Router({
  routes: [
    {
      path: "/",
      name: "Main",
      meta: { title: "Create-X-App | Home" },
      component: Main
    },
    {
      path: "/template",
      name: "Template",
      meta: { title: "Create-X-App | Template" },
      component: Template
    }
  ]
});

router.beforeEach((to, from, next) => {
  document.title = to.meta.title;
  next();
});

export default router;
