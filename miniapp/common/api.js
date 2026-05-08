/**
 * 保温材料小程序 API 封装
 * 后端地址需在 manifest.json 或此处配置
 */

// 开发环境使用本地地址，生产环境替换为实际域名
const BASE_URL = "http://192.168.101.30:8000/api/v1";

function request(url, options = {}) {
  const token = uni.getStorageSync("token");

  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + url,
      method: options.method || "GET",
      data: options.data,
      header: {
        "Content-Type": "application/json",
        Authorization: token ? `Bearer ${token}` : "",
        ...options.header,
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data);
        } else {
          console.error("API " + res.statusCode + ":", res.data);
          reject(res);
        }
      },
      fail: (err) => {
        console.error("Network error:", err.errMsg);
        reject(err);
      },
    });
  });
}

export default {
  // ===== 产品 =====
  getProducts(params) {
    return request("/products", { data: params });
  },
  getProductDetail(id) {
    return request(`/products/${id}`);
  },
  getRecommendedProducts(limit = 10) {
    return request("/products/recommended", { data: { limit } });
  },
  searchProducts(q) {
    return request("/products/search", { data: { q } });
  },

  // ===== 分类 & 场景 =====
  getCategories() {
    return request("/categories");
  },
  getCategoryProducts(id, params) {
    return request(`/categories/${id}/products`, { data: params });
  },
  getScenarios() {
    return request("/scenarios");
  },

  // ===== AI 助手 =====
  sendChatMessage(data) {
    return request("/ai/chat", { method: "POST", data });
  },
  getRecommendations(data) {
    return request("/ai/recommend", { method: "POST", data });
  },
  getChatSessions() {
    return request("/ai/sessions");
  },

  // ===== 订单 =====
  createOrder(data) {
    return request("/orders", { method: "POST", data });
  },
  getOrders(params) {
    return request("/orders", { data: params });
  },
  getOrderDetail(id) {
    return request(`/orders/${id}`);
  },
  cancelOrder(id) {
    return request(`/orders/${id}/cancel`, { method: "PUT" });
  },

  // ===== 收货地址 =====
  getAddresses() {
    return request("/addresses");
  },
  createAddress(data) {
    return request("/addresses", { method: "POST", data });
  },
  updateAddress(id, data) {
    return request(`/addresses/${id}`, { method: "PUT", data });
  },
  deleteAddress(id) {
    return request(`/addresses/${id}`, { method: "DELETE" });
  },

  // ===== 认证 =====
  wxLogin(code, nickname, avatar_url) {
    return request("/auth/wx-login", { method: "POST", data: { code, nickname, avatar_url } });
  },
  adminScanConfirm(token, openid) {
    return request("/auth/admin/scan", { method: "POST", data: { token, openid } });
  },
};
