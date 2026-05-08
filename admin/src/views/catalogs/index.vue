<template>
  <div class="catalogs">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>资料管理</span>
          <el-upload action="#" :auto-upload="false">
            <el-button type="primary" size="small">上传资料</el-button>
          </el-upload>
        </div>
      </template>
      <el-empty description="暂无资料，请上传纸质产品资料进行数字化" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
// TODO: Phase 5 实现资料上传 + OCR + 数字化
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
