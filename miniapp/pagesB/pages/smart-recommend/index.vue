<template>
  <view class="recommend-page">
    <view class="search-section">
      <input class="search-input" v-model="requirements" placeholder="描述您的需求，如：需要耐高温800℃的工业窑炉保温材料" confirm-type="search" @confirm="doSearch" />
      <button class="search-btn" :disabled="loading||!requirements.trim()" @click="doSearch">推荐</button>
    </view>

    <view class="quick-tags">
      <text class="tag" v-for="(t,i) in quickTags" :key="i" @click="requirements=t;doSearch()">{{ t }}</text>
    </view>

    <view v-if="loading" class="loading-area">
      <text>正在分析需求，匹配产品...</text>
    </view>

    <view v-if="products.length" class="results">
      <text class="result-title">为您推荐 {{ products.length }} 个产品</text>
      <product-card v-for="p in products" :key="p.id" :product="p" />
    </view>

    <view v-if="!loading && searched && products.length===0" class="empty">
      <u-empty text="暂无匹配产品" mode="search" />
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
      requirements: "",
      products: [],
      loading: false,
      searched: false,
      quickTags: [
        "外墙保温 A1级防火",
        "管道保温 耐高温",
        "冷库保温 防潮",
        "屋顶保温 高性价比",
        "工业窑炉 耐1000℃",
        "暖通空调 橡塑海绵",
      ],
    };
  },
  methods: {
    async doSearch() {
      if (this.loading || !this.requirements.trim()) return;
      this.loading = true;
      this.searched = true;
      try {
        const res = await api.getRecommendations({ requirements: this.requirements.trim() });
        this.products = res.products || [];
      } catch (e) {
        uni.showToast({ title: "推荐失败", icon: "none" });
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped lang="scss">
.recommend-page { padding: 24rpx 30rpx; background: #f5f5f5; min-height: 100vh; }
.search-section { display: flex; gap: 16rpx; margin-bottom: 20rpx; }
.search-input { flex: 1; height: 80rpx; background: #fff; border-radius: 16rpx; padding: 0 24rpx; font-size: 28rpx; }
.search-btn { background: #2979ff; color: #fff; border: none; border-radius: 16rpx; padding: 0 36rpx; height: 80rpx; line-height: 80rpx; font-size: 28rpx; }
.search-btn[disabled] { background: #ccc; }
.quick-tags { display: flex; flex-wrap: wrap; gap: 12rpx; margin-bottom: 30rpx; }
.tag { font-size: 24rpx; color: #2979ff; background: #ecf2ff; padding: 10rpx 20rpx; border-radius: 8rpx; }
.tag:active { background: #d0e0ff; }
.loading-area { text-align: center; padding: 60rpx; font-size: 26rpx; color: #999; }
.results { margin-top: 20rpx; }
.result-title { font-size: 28rpx; font-weight: 500; color: #333; display: block; margin-bottom: 20rpx; }
</style>
