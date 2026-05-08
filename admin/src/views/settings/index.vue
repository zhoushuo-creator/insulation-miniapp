<template>
  <div class="settings">
    <el-card>
      <template #header><span>系统设置</span></template>
      <el-form label-width="140px">
        <el-divider content-position="left">DeepSeek 对话配置</el-divider>
        <el-form-item label="API Key">
          <el-input type="password" placeholder="sk-..." show-password />
        </el-form-item>
        <el-form-item label="模型">
          <el-input value="deepseek-chat" disabled />
        </el-form-item>

        <el-divider content-position="left">通义千问 嵌入配置</el-divider>
        <el-form-item label="API Key">
          <el-input type="password" placeholder="sk-..." show-password />
        </el-form-item>
        <el-form-item label="嵌入模型">
          <el-input value="text-embedding-v3" disabled />
        </el-form-item>

        <el-divider content-position="left">微信小程序</el-divider>
        <el-form-item label="AppID">
          <el-input placeholder="wx..." />
        </el-form-item>
        <el-form-item label="AppSecret">
          <el-input type="password" placeholder="密钥..." show-password />
        </el-form-item>

        <el-form-item>
          <el-button type="primary">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
// TODO: Phase 3 实现配置持久化（环境变量 or 数据库）
</script>
