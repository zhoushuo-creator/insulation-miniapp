<template>
  <div class="orders">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>订单管理</span>
          <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width:160px" @change="fetchOrders">
            <el-option label="待付款" value="pending" />
            <el-option label="已付款" value="paid" />
            <el-option label="已发货" value="shipped" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </div>
      </template>

      <el-table :data="orders" v-loading="loading" stripe>
        <el-table-column prop="order_no" label="订单编号" width="180" />
        <el-table-column prop="total_amount" label="金额" width="100">
          <template #default="{ row }">¥{{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="商品" min-width="200">
          <template #default="{ row }">
            <div v-for="it in row.items" :key="it.id" class="order-item-line">
              产品#{{ it.product_id }} × {{ it.quantity }} (¥{{ it.unit_price }})
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" width="120">
          <template #default="{ row }">{{ row.remark || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" link type="primary" @click="changeStatus(row.id, 'paid')">标记付款</el-button>
            <el-button v-if="row.status === 'paid'" link type="primary" @click="changeStatus(row.id, 'shipped')">标记发货</el-button>
            <el-button v-if="row.status === 'shipped'" link type="success" @click="changeStatus(row.id, 'completed')">完成</el-button>
            <el-button v-if="row.status === 'pending'" link type="danger" @click="changeStatus(row.id, 'cancelled')">取消</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total > pageSize"
        style="margin-top:16px"
        :current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="onPage"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import request from "@/utils/request";

const orders = ref<any[]>([]);
const loading = ref(false);
const filterStatus = ref("");
const page = ref(1);
const pageSize = ref(20);
const total = ref(0);

const statusMap: Record<string, string> = {
  pending: "待付款", paid: "已付款", shipped: "已发货",
  completed: "已完成", cancelled: "已取消",
};
const statusTypeMap: Record<string, string> = {
  pending: "warning", paid: "primary", shipped: "info",
  completed: "success", cancelled: "danger",
};

function statusLabel(s: string) { return statusMap[s] || s; }
function statusType(s: string) { return statusTypeMap[s] || "info"; }

onMounted(() => fetchOrders());

async function fetchOrders() {
  loading.value = true;
  try {
    const params: any = { page: page.value, page_size: pageSize.value };
    if (filterStatus.value) params.status = filterStatus.value;
    const res: any = await request.get("/orders", { params });
    orders.value = res?.items || [];
    total.value = res?.total || 0;
  } finally {
    loading.value = false;
  }
}

async function changeStatus(orderId: number, status: string) {
  try {
    await request.put(`/orders/${orderId}/status?status=${status}`);
    ElMessage.success(status === "cancelled" ? "订单已取消" : `状态已更新`);
    fetchOrders();
  } catch {
    ElMessage.error("操作失败");
  }
}

function onPage(p: number) {
  page.value = p;
  fetchOrders();
}
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.order-item-line { font-size: 13px; color: #666; line-height: 1.6; }
</style>
