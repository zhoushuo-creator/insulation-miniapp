<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <template #header>
            <div class="stat-header">
              <span>产品数量</span>
              <el-icon :size="20" color="#409eff"><Box /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.product_count }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <template #header>
            <div class="stat-header">
              <span>分类数量</span>
              <el-icon :size="20" color="#67c23a"><FolderOpened /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.category_count }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <template #header>
            <div class="stat-header">
              <span>订单总数</span>
              <el-icon :size="20" color="#e6a23c"><Document /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.order_count }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <template #header>
            <div class="stat-header">
              <span>今日对话</span>
              <el-icon :size="20" color="#f56c6c"><ChatDotRound /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.today_chat_count }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import request from "@/utils/request";

const stats = reactive({
  product_count: 0,
  category_count: 0,
  order_count: 0,
  today_chat_count: 0,
});

onMounted(async () => {
  try {
    const res: any = await request.get("/dashboard");
    if (res) {
      stats.product_count = res.product_count ?? 0;
      stats.category_count = res.category_count ?? 0;
      stats.order_count = res.order_count ?? 0;
      stats.today_chat_count = res.today_chat_count ?? 0;
    }
  } catch (e) {
    console.error("Failed to load dashboard stats", e);
  }
});
</script>

<style scoped>
.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  text-align: center;
  padding: 8px 0;
}
</style>
