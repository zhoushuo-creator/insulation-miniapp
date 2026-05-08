<template>
  <view class="cart-page">
    <view v-if="cartItems.length === 0" class="empty-cart">
      <u-empty text="询价清单为空" mode="car" />
      <u-button type="primary" @click="goShopping">去逛逛</u-button>
    </view>

    <view v-else>
      <view
        v-for="(item, index) in cartItems"
        :key="index"
        class="cart-item"
      >
        <u-checkbox v-model="item.checked" />
        <image class="item-img" :src="item.cover_image || '/static/images/placeholder.png'" mode="aspectFill" />
        <view class="item-info">
          <text class="item-name">{{ item.name }}</text>
          <view class="item-bottom">
            <text class="item-price" v-if="item.reference_price">¥{{ item.reference_price }}</text>
            <text class="item-price" v-else>面议</text>
            <u-number-box v-model="item.quantity" :min="1" :max="999" />
          </view>
        </view>
      </view>

      <view class="cart-footer safe-area-bottom">
        <view class="total">
          <text>合计：</text>
          <text class="total-price">¥{{ totalPrice }}</text>
        </view>
        <u-button type="primary" size="small" @click="onSubmit">提交询价</u-button>
      </view>
    </view>
  </view>
</template>

<script>
import { mapState, mapMutations } from "vuex";
import api from "@/common/api.js";

export default {
  computed: {
    ...mapState(["cartItems"]),
    totalPrice() {
      return this.cartItems
        .filter((i) => i.checked !== false)
        .reduce((sum, i) => sum + (i.reference_price || 0) * i.quantity, 0)
        .toFixed(2);
    },
  },
  methods: {
    ...mapMutations(["CLEAR_CART", "REMOVE_FROM_CART"]),
    goShopping() {
      uni.switchTab({ url: "/pages/index/index" });
    },
    async onSubmit() {
      const checked = this.cartItems.filter((i) => i.checked !== false);
      if (checked.length === 0) {
        uni.showToast({ title: "请勾选要询价的产品", icon: "none" });
        return;
      }
      const items = checked.map((it) => ({
        product_id: it.product_id,
        variant_id: it.variant_id || null,
        quantity: it.quantity,
        unit_price: it.reference_price || 0,
      }));
      try {
        await api.createOrder({ items, remark: "小程序提交" });
        uni.showToast({ title: "询价已提交", icon: "success" });
        this.CLEAR_CART();
        setTimeout(() => {
          uni.navigateTo({ url: "/pagesB/pages/order/index" });
        }, 800);
      } catch (e) {
        uni.showToast({ title: "提交失败，请重试", icon: "none" });
      }
    },
  },
};
</script>

<style scoped lang="scss">
.cart-page {
  min-height: 100vh;
  padding-bottom: 120rpx;
}
.empty-cart {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 200rpx;
}
.cart-item {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 20rpx 30rpx;
  margin-bottom: 1rpx;
}
.item-img {
  width: 160rpx;
  height: 160rpx;
  border-radius: 8rpx;
  margin: 0 20rpx;
}
.item-info {
  flex: 1;
}
.item-name {
  font-size: 28rpx;
  display: block;
  margin-bottom: 8rpx;
}
.item-spec {
  font-size: 24rpx;
  color: #999;
}
.item-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12rpx;
}
.item-price {
  color: #dd524d;
  font-size: 32rpx;
  font-weight: bold;
}
.cart-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 20rpx 30rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
}
.total-price {
  color: #dd524d;
  font-size: 36rpx;
  font-weight: bold;
}
</style>
