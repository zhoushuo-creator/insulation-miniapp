<template>
  <view class="scan-page">
    <view class="scan-header">
      <text class="scan-title">管理后台扫码登录</text>
      <text class="scan-desc">输入管理后台显示的二维码Token</text>
    </view>
    <view class="scan-input-area">
      <input class="scan-input" v-model="token" placeholder="粘贴二维码Token" />
      <button class="scan-btn" :disabled="!token.trim()" @click="doConfirm">确认登录</button>
    </view>
    <view v-if="result" class="scan-result" :class="result.success ? 'success' : 'fail'">
      <text>{{ result.msg }}</text>
    </view>
  </view>
</template>

<script>
import { mapState } from "vuex";
import api from "@/common/api.js";

export default {
  data() {
    return { token: "", result: null };
  },
  computed: {
    ...mapState(["userInfo"]),
  },
  methods: {
    async doConfirm() {
      if (!this.token.trim()) return;
      const openid = (this.userInfo && this.userInfo.openid) || "dev-user";
      try {
        const res = await api.adminScanConfirm(this.token.trim(), openid);
        this.result = { success: true, msg: res.message || "确认成功，请查看管理后台" };
      } catch (e) {
        this.result = { success: false, msg: "确认失败，请重试" };
      }
    },
  },
};
</script>

<style scoped lang="scss">
.scan-page { padding: 60rpx 40rpx; background: #f5f5f5; min-height: 100vh; }
.scan-header { text-align: center; margin-bottom: 60rpx; }
.scan-title { font-size: 34rpx; font-weight: bold; color: #333; display: block; }
.scan-desc { font-size: 26rpx; color: #999; margin-top: 12rpx; display: block; }
.scan-input-area { margin-bottom: 40rpx; }
.scan-input {
  width: 100%; height: 80rpx; background: #fff; border-radius: 12rpx;
  padding: 0 24rpx; font-size: 28rpx; margin-bottom: 24rpx; border: 1rpx solid #e0e0e0;
}
.scan-btn {
  width: 100%; height: 80rpx; background: #2979ff; color: #fff;
  border: none; border-radius: 12rpx; font-size: 30rpx; line-height: 80rpx;
}
.scan-btn[disabled] { background: #ccc; }
.scan-result { text-align: center; padding: 30rpx; border-radius: 12rpx; }
.scan-result.success { background: #f0f9eb; color: #67c23a; }
.scan-result.fail { background: #fef0f0; color: #f56c6c; }
</style>
