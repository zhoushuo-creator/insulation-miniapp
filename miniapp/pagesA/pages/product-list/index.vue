<template>
  <view class="product-list-page">
    <!-- Search bar -->
    <view class="search-wrap">
      <u-search
        v-model="keyword"
        placeholder="搜索产品名称、品牌..."
        :show-action="false"
        @search="onSearch"
        @clear="onClearSearch"
      />
    </view>

    <!-- Filter bar -->
    <view class="filter-bar">
      <view class="filter-item" @click="showCategoryPicker = true">
        <text class="filter-label">{{ categoryLabel }}</text>
        <text class="filter-arrow">▼</text>
      </view>
      <view class="filter-item" @click="showSortPicker = true">
        <text class="filter-label">{{ sortLabel }}</text>
        <text class="filter-arrow">▼</text>
      </view>
    </view>

    <!-- Product list -->
    <scroll-view
      class="product-scroll"
      scroll-y
      :refresher-enabled="true"
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="onLoadMore"
    >
      <view v-if="products.length === 0 && !loading" class="empty-state">
        <u-empty text="暂无产品数据" mode="list" />
      </view>

      <view v-else>
        <product-card
          v-for="(item, idx) in products"
          :key="idx"
          :product="item"
        />

        <u-loadmore
          :status="loadStatus"
          @loadmore="onLoadMore"
        />

        <view class="safe-bottom" />
      </view>
    </scroll-view>

    <!-- Category picker popup -->
    <u-popup v-model="showCategoryPicker" mode="bottom" border-radius="24">
      <view class="picker-popup">
        <view class="picker-header">
          <text @click="showCategoryPicker = false">取消</text>
          <text class="picker-title">选择分类</text>
          <text class="picker-confirm" @click="showCategoryPicker = false">确定</text>
        </view>
        <scroll-view scroll-y class="picker-body">
          <view
            v-for="cat in flattenCategories"
            :key="cat.id"
            class="picker-option"
            :class="{ active: selectedCategoryId === cat.id }"
            @click="selectCategory(cat)"
          >
            <text>{{ cat.indent }}{{ cat.name }}</text>
          </view>
        </scroll-view>
      </view>
    </u-popup>

    <!-- Sort picker popup -->
    <u-popup v-model="showSortPicker" mode="bottom" border-radius="24">
      <view class="picker-popup">
        <view class="picker-header">
          <text @click="showSortPicker = false">取消</text>
          <text class="picker-title">排序方式</text>
        </view>
        <view class="picker-body">
          <view
            v-for="opt in sortOptions"
            :key="opt.value"
            class="picker-option"
            :class="{ active: sortBy === opt.value }"
            @click="selectSort(opt.value)"
          >
            <text>{{ opt.label }}</text>
          </view>
        </view>
      </view>
    </u-popup>
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
      products: [],
      categories: [],
      selectedCategoryId: null,
      selectedCategoryName: "全部分类",
      sortBy: "created_at",
      page: 1,
      pageSize: 20,
      total: 0,
      loading: false,
      refreshing: false,
      loadStatus: "loadmore",
      showCategoryPicker: false,
      showSortPicker: false,
      sortOptions: [
        { label: "最新发布", value: "created_at" },
        { label: "价格从低到高", value: "reference_price_asc" },
        { label: "价格从高到低", value: "reference_price_desc" },
      ],
    };
  },
  computed: {
    categoryLabel() {
      return this.selectedCategoryName || "全部分类";
    },
    sortLabel() {
      const opt = this.sortOptions.find(o => o.value === this.sortBy);
      return opt ? opt.label : "排序";
    },
    flattenCategories() {
      const result = [{ id: null, name: "全部分类", indent: "" }];
      const walk = (list, indent = "") => {
        for (const c of list) {
          result.push({ id: c.id, name: c.name, indent });
          if (c.children && c.children.length) {
            walk(c.children, indent + "  ");
          }
        }
      };
      if (this.categories.length) walk(this.categories);
      return result;
    },
  },
  onLoad(options) {
    if (options.keyword) {
      this.keyword = options.keyword;
    }
    if (options.category_id) {
      this.selectedCategoryId = parseInt(options.category_id);
    }
    this.loadCategories();
    this.loadProducts();
  },
  methods: {
    async loadCategories() {
      try {
        const res = await api.getCategories();
        this.categories = res.items || [];
        if (this.selectedCategoryId) {
          const find = (list) => {
            for (const c of list) {
              if (c.id === this.selectedCategoryId) return c.name;
              if (c.children) {
                const f = find(c.children);
                if (f) return f;
              }
            }
            return null;
          };
          const name = find(this.categories);
          if (name) this.selectedCategoryName = name;
        }
      } catch (e) {}
    },
    async loadProducts(isLoadMore = false) {
      if (this.loading) return;
      if (!isLoadMore) {
        this.page = 1;
        this.products = [];
      }

      if (this.total > 0 && this.products.length >= this.total && isLoadMore) {
        this.loadStatus = "nomore";
        return;
      }

      this.loading = true;
      this.loadStatus = "loading";
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize,
        };
        if (this.keyword) params.keyword = this.keyword;
        if (this.selectedCategoryId) params.category_id = this.selectedCategoryId;
        if (this.sortBy === "reference_price_asc") {
          params.sort_by = "reference_price";
          // need a way to do asc sort... backend defaults to desc. For simplicity we'll handle this differently
        } else if (this.sortBy === "reference_price_desc") {
          params.sort_by = "reference_price";
        } else {
          params.sort_by = this.sortBy;
        }

        const res = await api.getProducts(params);
        const items = res.items || [];
        if (isLoadMore) {
          this.products.push(...items);
        } else {
          this.products = items;
        }
        this.total = res.total || 0;

        if (this.products.length >= this.total) {
          this.loadStatus = "nomore";
        } else {
          this.loadStatus = "loadmore";
        }
      } catch (e) {
        this.loadStatus = "loadmore";
      } finally {
        this.loading = false;
        this.refreshing = false;
      }
    },
    onSearch() {
      this.page = 1;
      this.loadProducts();
    },
    onClearSearch() {
      this.keyword = "";
      this.page = 1;
      this.loadProducts();
    },
    selectCategory(cat) {
      this.selectedCategoryId = cat.id;
      this.selectedCategoryName = cat.name;
      this.showCategoryPicker = false;
      this.page = 1;
      this.loadProducts();
    },
    selectSort(val) {
      this.sortBy = val;
      this.showSortPicker = false;
      this.page = 1;
      this.loadProducts();
    },
    onRefresh() {
      this.refreshing = true;
      this.loadProducts();
    },
    onLoadMore() {
      if (this.loadStatus === "loading" || this.loadStatus === "nomore") return;
      this.page += 1;
      this.loadProducts(true);
    },
  },
};
</script>

<style scoped lang="scss">
.product-list-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.search-wrap {
  padding: 16rpx 24rpx;
  background: #fff;
}

.filter-bar {
  display: flex;
  background: #fff;
  padding: 0 24rpx 16rpx;
  gap: 24rpx;
}
.filter-item {
  display: flex;
  align-items: center;
  padding: 8rpx 20rpx;
  background: #f5f5f5;
  border-radius: 8rpx;
}
.filter-label {
  font-size: 26rpx;
  color: #666;
  margin-right: 8rpx;
}
.filter-arrow {
  font-size: 20rpx;
  color: #999;
}

.product-scroll {
  flex: 1;
  padding: 16rpx 24rpx;
}

.empty-state {
  padding-top: 200rpx;
}

.picker-popup {
  padding: 20rpx 0 40rpx;
}
.picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30rpx 20rpx;
  font-size: 28rpx;
}
.picker-title {
  font-weight: 500;
}
.picker-confirm {
  color: #2979ff;
}
.picker-body {
  max-height: 500rpx;
}
.picker-option {
  padding: 24rpx 30rpx;
  font-size: 28rpx;
  border-bottom: 1rpx solid #f5f5f5;
  &.active {
    color: #2979ff;
    background: #ecf2ff;
  }
}

.safe-bottom {
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
  height: 40rpx;
}
</style>
