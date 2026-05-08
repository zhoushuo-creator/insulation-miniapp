<template>
  <view class="home-page">
    <!-- 搜索栏 -->
    <view class="search-section">
      <u-search
        v-model="keyword"
        placeholder="搜索保温材料..."
        :show-action="false"
        @search="onSearch"
      />
    </view>

    <!-- AI 顾问入口 -->
    <view class="ai-entry" @click="goToAiChat">
      <view class="ai-entry-left">
        <text class="ai-icon">🤖</text>
        <text class="ai-title">AI 智能顾问</text>
      </view>
      <text class="ai-desc">告诉我需求，帮你选材</text>
    </view>

    <!-- 分类快速入口 -->
    <view class="category-section">
      <text class="section-title">产品分类</text>
      <view class="category-grid" v-if="categories.length">
        <view
          v-for="cat in categories"
          :key="cat.id"
          class="category-item"
          @click="goToCategory(cat.id)"
        >
          <view class="cat-icon">{{ cat.icon || '📦' }}</view>
          <text class="cat-name">{{ cat.name }}</text>
        </view>
      </view>
    </view>

    <!-- 推荐产品 -->
    <view class="recommend-section">
      <text class="section-title">推荐产品</text>
      <view v-if="recommended.length === 0" class="empty-state">
        <text class="empty-text">暂无推荐产品</text>
      </view>
      <view v-else>
        <product-card
          v-for="item in recommended"
          :key="item.id"
          :product="item"
        />
      </view>
    </view>
  </view>
</template>

<script>
import api from "@/common/api.js";
import ProductCard from "@/components/product-card/product-card.vue";

export default {
  components: { ProductCard },
  data() {
    return {
      keyword: "",
      categories: [],
      recommended: [],
    };
  },
  onLoad() {
    this.loadCategories();
    this.loadRecommended();
  },
  methods: {
    async loadCategories() {
      try {
        const res = await api.getCategories();
        this.categories = res.items || [];
        console.log("分类加载完成:", this.categories.length, "个");
      } catch (e) {
        console.error("分类加载失败:", JSON.stringify(e));
      }
    },
    async loadRecommended() {
      try {
        const res = await api.getRecommendedProducts(6);
        this.recommended = res.items || [];
        console.log("推荐产品加载完成:", this.recommended.length, "个");
      } catch (e) {
        console.error("推荐产品加载失败:", JSON.stringify(e));
      }
    },
    onSearch() {
      uni.navigateTo({
        url: `/pagesA/pages/product-list/index?keyword=${this.keyword}`,
      });
    },
    goToAiChat() {
      uni.navigateTo({ url: "/pagesB/pages/ai-chat/index" });
    },
    goToCategory(id) {
      uni.navigateTo({
        url: `/pagesA/pages/product-list/index?category_id=${id}`,
      });
    },
  },
};
</script>

<style scoped lang="scss">
.home-page {
  padding: 20rpx 30rpx;
}
.search-section {
  margin-bottom: 20rpx;
}
.ai-entry {
  background: linear-gradient(135deg, #2979ff, #448aff);
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  color: #fff;
  .ai-entry-left {
    display: flex;
    align-items: center;
    margin-bottom: 8rpx;
  }
  .ai-icon { font-size: 40rpx; margin-right: 16rpx; }
  .ai-title { font-size: 32rpx; font-weight: bold; }
  .ai-desc { font-size: 26rpx; opacity: 0.85; }
}
.section-title {
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
  display: block;
}
.category-grid {
  display: flex;
  flex-wrap: wrap;
}
.category-item {
  width: 25%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx 0;
}
.cat-icon { font-size: 48rpx; margin-bottom: 8rpx; }
.cat-name { font-size: 24rpx; color: #666; }
.recommend-section {
  margin-top: 20rpx;
}
.empty-state {
  padding: 60rpx 0;
  text-align: center;
}
.empty-text {
  color: #999;
  font-size: 28rpx;
}
</style>
