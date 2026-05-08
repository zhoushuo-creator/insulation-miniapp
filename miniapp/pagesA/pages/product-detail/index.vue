<template>
  <view class="product-detail-page">
    <!-- Image carousel -->
    <swiper
      v-if="images.length"
      class="image-swiper"
      indicator-dots
      autoplay
      circular
      indicator-color="rgba(255,255,255,0.5)"
      indicator-active-color="#fff"
    >
      <swiper-item v-for="(url, idx) in images" :key="idx">
        <image :src="url" mode="aspectFill" class="swiper-image" />
      </swiper-item>
    </swiper>
    <view v-else class="no-image">
      <image src="/static/images/placeholder.png" mode="aspectFit" class="placeholder-img" />
    </view>

    <!-- Basic info -->
    <view class="info-section">
      <view class="info-header">
        <text class="product-name">{{ product.name }}</text>
        <text v-if="product.brand" class="product-brand">{{ product.brand }}</text>
      </view>
      <view v-if="product.model" class="product-model">型号: {{ product.model }}</view>
      <view class="price-row" v-if="product.reference_price != null">
        <text class="price">¥{{ product.reference_price }}</text>
        <text class="unit" v-if="product.unit"> / {{ product.unit }}</text>
      </view>
      <view class="price-row" v-else>
        <text class="price-na">价格面议</text>
      </view>
    </view>

    <!-- Category & Scenarios -->
    <view class="tags-section" v-if="product.category || (scenarios.length > 0)">
      <text v-if="product.category" class="info-tag info-tag--cat">{{ product.category.name }}</text>
      <text v-for="s in scenarios" :key="s.id" class="info-tag info-tag--scene">{{ s.name }}</text>
    </view>

    <!-- Specs -->
    <view class="section" v-if="specItems.length">
      <view class="section-title">技术参数</view>
      <view class="spec-grid">
        <view v-for="(item, idx) in specItems" :key="idx" class="spec-item">
          <text class="spec-label">{{ item.label }}</text>
          <text class="spec-value">{{ item.value }}</text>
        </view>
      </view>
    </view>

    <!-- Variants -->
    <view class="section" v-if="variants.length">
      <view class="section-title">规格变体</view>
      <view class="variant-table">
        <view class="variant-header">
          <text class="v-col v-col--name">规格</text>
          <text class="v-col">厚度(mm)</text>
          <text class="v-col">密度(kg/m³)</text>
          <text class="v-col">价格</text>
          <text class="v-col">库存</text>
        </view>
        <view v-for="(v, idx) in variants" :key="idx" class="variant-row">
          <text class="v-col v-col--name">{{ v.name || '-' }}</text>
          <text class="v-col">{{ v.thickness || '-' }}</text>
          <text class="v-col">{{ v.density || '-' }}</text>
          <text class="v-col v-col--price">{{ v.price ? `¥${v.price}` : '-' }}</text>
          <text class="v-col">{{ v.stock }}</text>
        </view>
      </view>
    </view>

    <!-- Description -->
    <view class="section" v-if="product.description">
      <view class="section-title">产品描述</view>
      <view class="desc-content">
        <text>{{ product.description }}</text>
      </view>
    </view>

    <!-- Bottom bar -->
    <view class="bottom-bar">
      <view class="bar-left" @click="addToCart">
        <text class="bar-icon">📋</text>
        <text class="bar-text">加入询价</text>
      </view>
      <view class="bar-right" @click="goToAiChat">
        <text>🤖 AI 咨询该产品</text>
      </view>
    </view>
  </view>
</template>

<script>
import api from "@/common/api.js";
import { mapState, mapMutations } from "vuex";

export default {
  data() {
    return {
      productId: null,
      product: {},
      images: [],
      scenarios: [],
      variants: [],
      specItems: [],
    };
  },
  computed: {
    ...mapState(["cartItems"]),
  },
  onLoad(options) {
    if (options.id) {
      this.productId = parseInt(options.id);
      this.loadProduct();
    }
  },
  methods: {
    ...mapMutations(["ADD_TO_CART"]),
    async loadProduct() {
      try {
        const res = await api.getProductDetail(this.productId);
        if (res) {
          this.product = res;
          this.images = res.cover_image
            ? [res.cover_image, ...(res.images || [])]
            : (res.images || []);
          this.scenarios = res.scenarios || [];
          this.variants = res.variants || [];

          // Extract specs into label-value pairs
          if (res.specs) {
            const labelMap = {
              fire_rating: "防火等级",
              thermal_conductivity: "导热系数",
              max_temp: "最高使用温度",
              min_temp: "最低使用温度",
              compressive_strength: "抗压强度",
              bulk_density: "体积密度",
              water_absorption: "吸水率",
              dimension: "规格尺寸",
            };
            this.specItems = Object.entries(res.specs)
              .filter(([, v]) => v != null)
              .map(([k, v]) => ({
                label: labelMap[k] || k,
                value: typeof v === "number" ? String(v) : String(v),
              }));
          }
        }
      } catch (e) {
        uni.showToast({ title: "加载失败", icon: "none" });
      }
    },
    addToCart() {
      this.ADD_TO_CART({
        product_id: this.product.id,
        name: this.product.name,
        cover_image: this.product.cover_image,
        reference_price: this.product.reference_price,
        unit: this.product.unit,
        quantity: 1,
      });
      uni.showToast({ title: "已加入询价清单", icon: "success" });
    },
    goToAiChat() {
      uni.navigateTo({ url: "/pagesB/pages/ai-chat/index" });
    },
  },
};
</script>

<style scoped lang="scss">
.product-detail-page {
  padding-bottom: 120rpx;
}

.image-swiper {
  width: 100%;
  height: 500rpx;
}
.swiper-image {
  width: 100%;
  height: 100%;
}
.no-image {
  width: 100%;
  height: 400rpx;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}
.placeholder-img {
  width: 200rpx;
  height: 200rpx;
}

.info-section {
  background: #fff;
  padding: 30rpx;
  margin-bottom: 16rpx;
}
.info-header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12rpx;
}
.product-name {
  font-size: 34rpx;
  font-weight: 600;
  color: #333;
}
.product-brand {
  font-size: 24rpx;
  color: #2979ff;
  background: #ecf2ff;
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
}
.product-model {
  font-size: 26rpx;
  color: #999;
  margin-top: 12rpx;
}
.price-row {
  margin-top: 16rpx;
}
.price {
  font-size: 40rpx;
  font-weight: bold;
  color: #fa3534;
}
.unit {
  font-size: 26rpx;
  color: #999;
}
.price-na {
  font-size: 30rpx;
  color: #999;
  font-weight: 500;
}

.tags-section {
  background: #fff;
  padding: 0 30rpx 20rpx;
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-bottom: 16rpx;
}
.info-tag {
  font-size: 24rpx;
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
}
.info-tag--cat {
  background: #fef0f0;
  color: #f56c6c;
}
.info-tag--scene {
  background: #ecf2ff;
  color: #2979ff;
}

.section {
  background: #fff;
  padding: 24rpx 30rpx;
  margin-bottom: 16rpx;
}
.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 16rpx;
  display: block;
}

.spec-grid {
  display: flex;
  flex-wrap: wrap;
}
.spec-item {
  width: 50%;
  display: flex;
  justify-content: space-between;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #f5f5f5;
}
.spec-label {
  font-size: 26rpx;
  color: #999;
}
.spec-value {
  font-size: 26rpx;
  color: #333;
}

.variant-table {
  border: 1rpx solid #eee;
  border-radius: 8rpx;
  overflow: hidden;
}
.variant-header {
  display: flex;
  background: #f5f5f5;
}
.variant-row {
  display: flex;
  border-top: 1rpx solid #eee;
}
.v-col {
  flex: 1;
  font-size: 24rpx;
  padding: 12rpx 8rpx;
  text-align: center;
}
.v-col--name {
  flex: 1.5;
  text-align: left;
}
.v-col--price {
  color: #fa3534;
}

.desc-content {
  font-size: 28rpx;
  color: #666;
  line-height: 1.8;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  background: #fff;
  border-top: 1rpx solid #eee;
  z-index: 100;
}
.bar-left, .bar-right {
  flex: 1;
  text-align: center;
  padding: 24rpx 0;
  font-size: 28rpx;
}
.bar-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  border-right: 1rpx solid #eee;
}
.bar-icon {
  font-size: 36rpx;
}
.bar-text {
  font-size: 22rpx;
  color: #666;
  margin-top: 4rpx;
}
.bar-right {
  background: linear-gradient(135deg, #2979ff, #448aff);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
