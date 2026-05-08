<template>
  <view class="product-card" @click="onTap">
    <image
      class="card-image"
      :src="product.cover_image || '/static/images/placeholder.png'"
      mode="aspectFill"
    />
    <view class="card-body">
      <text class="card-name">{{ product.name }}</text>
      <view class="card-meta">
        <text v-if="product.brand" class="card-brand">{{ product.brand }}</text>
        <text v-if="product.model" class="card-model">{{ product.model }}</text>
      </view>
      <view class="card-scenarios" v-if="product.scenarios && product.scenarios.length">
        <text
          v-for="s in product.scenarios"
          :key="s.id"
          class="scenario-tag"
        >{{ s.name }}</text>
      </view>
      <view class="card-bottom">
        <text v-if="product.reference_price != null" class="card-price">
          ¥{{ product.reference_price }}<text v-if="product.unit" class="card-unit"> / {{ product.unit }}</text>
        </text>
        <text v-else class="card-price card-price--na">价格面议</text>
        <text v-if="product.category" class="card-category">{{ product.category.name }}</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: "ProductCard",
  props: {
    product: {
      type: Object,
      required: true,
    },
  },
  methods: {
    onTap() {
      this.$emit("click", this.product);
      uni.navigateTo({
        url: `/pagesA/pages/product-detail/index?id=${this.product.id}`,
      });
    },
  },
};
</script>

<style scoped lang="scss">
.product-card {
  background: #fff;
  border-radius: 16rpx;
  overflow: hidden;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.card-image {
  width: 100%;
  height: 320rpx;
  background: #f5f5f5;
}
.card-body {
  padding: 20rpx 24rpx;
}
.card-name {
  font-size: 30rpx;
  font-weight: 500;
  color: #333;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-meta {
  display: flex;
  align-items: center;
  margin-top: 8rpx;
  gap: 12rpx;
}
.card-brand {
  font-size: 24rpx;
  color: #2979ff;
}
.card-model {
  font-size: 24rpx;
  color: #999;
}
.card-scenarios {
  display: flex;
  flex-wrap: wrap;
  margin-top: 12rpx;
  gap: 8rpx;
}
.scenario-tag {
  font-size: 22rpx;
  color: #2979ff;
  background: #ecf2ff;
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
}
.card-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16rpx;
}
.card-price {
  font-size: 32rpx;
  font-weight: bold;
  color: #fa3534;
}
.card-price--na {
  font-size: 26rpx;
  font-weight: normal;
  color: #999;
}
.card-unit {
  font-size: 22rpx;
  font-weight: normal;
  color: #999;
}
.card-category {
  font-size: 22rpx;
  color: #999;
}
</style>
