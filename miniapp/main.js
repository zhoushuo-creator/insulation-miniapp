import Vue from "vue";
import App from "./App";

// 引入 uView UI
import uView from "uview-ui";
Vue.use(uView);

// 引入全局样式
import "./styles/base.scss";

// 引入 Vuex Store
import store from "./store";

Vue.config.productionTip = false;

App.mpType = "app";

const app = new Vue({
  store,
  ...App,
});
app.$mount();
