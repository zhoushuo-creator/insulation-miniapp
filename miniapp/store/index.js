import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    // 用户信息
    userInfo: null,
    token: uni.getStorageSync("token") || "",
    // 购物车
    cartItems: [],
    // 聊天会话ID (当前)
    chatSessionId: null,
  },
  mutations: {
    SET_USER_INFO(state, userInfo) {
      state.userInfo = userInfo;
    },
    SET_TOKEN(state, token) {
      state.token = token;
      uni.setStorageSync("token", token);
    },
    ADD_TO_CART(state, item) {
      const exist = state.cartItems.find(
        (i) => i.product_id === item.product_id && i.variant_id === item.variant_id
      );
      if (exist) {
        exist.quantity += item.quantity;
      } else {
        state.cartItems.push(item);
      }
      uni.setStorageSync("cart", state.cartItems);
    },
    REMOVE_FROM_CART(state, index) {
      state.cartItems.splice(index, 1);
      uni.setStorageSync("cart", state.cartItems);
    },
    CLEAR_CART(state) {
      state.cartItems = [];
      uni.setStorageSync("cart", []);
    },
    SET_CHAT_SESSION(state, sessionId) {
      state.chatSessionId = sessionId;
    },
  },
  actions: {
    // TODO: 实现登录逻辑
    async login({ commit }, code) {
      // Phase 5: 调用 /api/v1/auth/wx-login
    },
  },
});

// 初始化购物车
const savedCart = uni.getStorageSync("cart");
if (savedCart) {
  store.state.cartItems = savedCart;
}

export default store;
