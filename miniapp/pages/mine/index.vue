<template>
  <view class="mine-page">
    <view class="user-header" @click="doLogin">
      <image class="avatar" :src="(userInfo && userInfo.avatar_url) || '/static/icons/default-avatar.png'" mode="aspectFill" />
      <view class="user-info">
        <text class="nickname">{{ (userInfo && userInfo.nickname) || '点击登录' }}</text>
        <text v-if="userInfo" class="user-id">ID: {{ userInfo.openid ? userInfo.openid.slice(0,12) : '' }}...</text>
      </view>
    </view>

    <view class="menu-section">
      <u-cell-group>
        <u-cell title="我的订单" icon="/static/icons/order.png" @click="goOrder" />
        <u-cell title="AI对话记录" icon="/static/icons/chat.png" @click="goAiChat" />
        <u-cell title="关于我们" icon="/static/icons/info.png" />
      </u-cell-group>
    </view>

    <view class="admin-entry">
      <u-button type="primary" size="small" @click="goAdminScan">管理后台扫码</u-button>
    </view>
  </view>
</template>

<script>
import { mapState, mapMutations } from "vuex";
import api from "@/common/api.js";

export default {
  computed: {
    ...mapState(["userInfo", "token"]),
  },
  methods: {
    ...mapMutations(["SET_USER_INFO", "SET_TOKEN"]),
    goOrder() {
      uni.navigateTo({ url: "/pagesB/pages/order/index" });
    },
    goAiChat() {
      uni.navigateTo({ url: "/pagesB/pages/ai-chat/index" });
    },
    async doLogin() {
      if (this.userInfo) return;
      try {
        uni.showLoading({ title: "登录中..." });
        const loginRes = await uni.login();
        if (!loginRes || !loginRes.code) {
          uni.hideLoading();
          return;
        }
        const nickname = "";
        const avatar_url = "";

        const res = await api.wxLogin(loginRes.code, nickname, avatar_url);
        this.SET_TOKEN(res.token);
        this.SET_USER_INFO(res.user);
        uni.hideLoading();
        uni.showToast({ title: "登录成功", icon: "success" });
      } catch (e) {
        uni.hideLoading();
        // Dev fallback
        const devRes = await api.wxLogin("dev-code", "开发者", "");
        this.SET_TOKEN(devRes.token);
        this.SET_USER_INFO(devRes.user);
      }
    },
    goAdminScan() {
      uni.navigateTo({ url: "/pagesB/pages/admin-scan/index" });
    },
  },
};
</script>

<style scoped lang="scss">
.mine-page { min-height: 100vh; background: #f5f5f5; }
.user-header {
  background: #2979ff; padding: 60rpx 30rpx 40rpx;
  display: flex; align-items: center;
}
.avatar {
  width: 120rpx; height: 120rpx; border-radius: 50%;
  border: 4rpx solid rgba(255,255,255,0.3); margin-right: 24rpx;
}
.nickname { color: #fff; font-size: 34rpx; font-weight: 500; }
.user-id { color: rgba(255,255,255,0.6); font-size: 22rpx; margin-top: 4rpx; }
.menu-section { margin-top: 20rpx; }
.admin-entry { padding: 30rpx; text-align: center; margin-top: 40rpx; }
</style>
