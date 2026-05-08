<template>
  <view class="category-page">
    <view class="category-tree" v-if="categories.length">
      <view
        v-for="cat in categories"
        :key="cat.id"
        class="category-node"
        @click="onCategoryTap(cat)"
      >
        <text class="node-name">{{ cat.name }}</text>
        <view v-if="cat.children && cat.children.length" class="sub-list">
          <text
            v-for="sub in cat.children"
            :key="sub.id"
            class="sub-item"
          >{{ sub.name }}</text>
        </view>
      </view>
    </view>
    <view v-else class="empty-state">
      <u-empty text="暂无分类数据" mode="list" />
    </view>

    <!-- AI 智能选材快捷入口 -->
    <view class="ai-shortcut" @click="goToAi">
      <text>🤖 AI智能选材，帮我推荐</text>
    </view>
  </view>
</template>

<script>
import api from "@/common/api.js";

export default {
  data() {
    return { categories: [] };
  },
  onLoad() {
    this.loadCategories();
  },
  methods: {
    async loadCategories() {
      try {
        const res = await api.getCategories();
        this.categories = res.items || [];
      } catch (e) {}
    },
    onCategoryTap(cat) {
      uni.navigateTo({
        url: `/pagesA/pages/product-list/index?category_id=${cat.id}`,
      });
    },
    goToAi() {
      uni.navigateTo({ url: "/pagesB/pages/smart-recommend/index" });
    },
  },
};
</script>

<style scoped lang="scss">
.category-page {
  padding: 20rpx 30rpx;
}
.category-node {
  background: #fff;
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
}
.node-name {
  font-size: 30rpx;
  font-weight: 500;
}
.sub-list {
  display: flex;
  flex-wrap: wrap;
  margin-top: 12rpx;
}
.sub-item {
  background: #f0f8ff;
  color: #2979ff;
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
  font-size: 24rpx;
  margin-right: 12rpx;
  margin-bottom: 8rpx;
}
.ai-shortcut {
  position: fixed;
  bottom: 30rpx;
  left: 30rpx;
  right: 30rpx;
  background: linear-gradient(135deg, #2979ff, #448aff);
  color: #fff;
  text-align: center;
  padding: 24rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
}
</style>
