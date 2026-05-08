<template>
  <view class="order-page">
    <view v-if="orders.length === 0 && !loading" class="empty">
      <u-empty text="暂无订单" mode="list" />
    </view>

    <view v-for="o in orders" :key="o.id" class="order-card">
      <view class="order-header">
        <text class="order-no">{{ o.order_no }}</text>
        <text class="order-status" :style="{color: statusColor(o.status)}">{{ statusLabel(o.status) }}</text>
      </view>
      <view class="order-items">
        <view v-for="it in o.items" :key="it.id" class="item-line">
          <text class="item-desc">产品#{{ it.product_id }} × {{ it.quantity }}</text>
          <text class="item-price">¥{{ it.unit_price }}</text>
        </view>
      </view>
      <view class="order-footer">
        <text class="order-total">合计: ¥{{ o.total_amount }}</text>
        <view class="order-actions">
          <text v-if="o.status === 'pending'" class="action-btn action-cancel" @click="cancelOrder(o.id)">取消</text>
          <text class="order-time">{{ o.created_at.slice(0,10) }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import api from "@/common/api.js";

const STATUS_MAP = {
  pending: "待付款", paid: "已付款", shipped: "已发货",
  completed: "已完成", cancelled: "已取消",
};
const STATUS_COLOR = {
  pending: "#f0ad4e", paid: "#007aff", shipped: "#409eff",
  completed: "#19be6b", cancelled: "#999",
};

export default {
  data() {
    return { orders: [], loading: false };
  },
  onShow() {
    this.loadOrders();
  },
  methods: {
    statusLabel(s) { return STATUS_MAP[s] || s; },
    statusColor(s) { return STATUS_COLOR[s] || "#999"; },
    async loadOrders() {
      this.loading = true;
      try {
        const res = await api.getOrders();
        this.orders = res.items || [];
      } catch (e) {
        console.error(e);
      } finally {
        this.loading = false;
      }
    },
    async cancelOrder(id) {
      try {
        await api.cancelOrder(id);
        uni.showToast({ title: "已取消", icon: "success" });
        this.loadOrders();
      } catch (e) {
        uni.showToast({ title: "取消失败", icon: "none" });
      }
    },
  },
};
</script>

<style scoped lang="scss">
.order-page { padding: 20rpx 24rpx; background: #f5f5f5; min-height: 100vh; }
.order-card { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 20rpx; }
.order-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }
.order-no { font-size: 26rpx; color: #333; font-weight: 500; }
.order-status { font-size: 26rpx; font-weight: 500; }
.order-items { border-top: 1rpx solid #f5f5f5; padding-top: 12rpx; }
.item-line { display: flex; justify-content: space-between; padding: 8rpx 0; }
.item-desc { font-size: 26rpx; color: #666; }
.item-price { font-size: 26rpx; color: #333; }
.order-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 16rpx; padding-top: 12rpx; border-top: 1rpx solid #f5f5f5; }
.order-total { font-size: 28rpx; font-weight: bold; color: #333; }
.order-actions { display: flex; align-items: center; gap: 16rpx; }
.action-cancel { font-size: 24rpx; color: #fa3534; padding: 4rpx 16rpx; border: 1rpx solid #fa3534; border-radius: 8rpx; }
.order-time { font-size: 22rpx; color: #999; }
</style>
