<template>
  <div class="login-container">
    <div class="login-card">
      <h1>保温材料管理后台</h1>
      <div v-if="!scanConfirmed" class="qrcode-section">
        <div class="qrcode-box">
          <canvas ref="qrCanvas" width="200" height="200" />
        </div>
        <p class="qrcode-tip">微信扫描二维码登录</p>
        <p v-if="qrToken" class="token-hint">{{ qrToken.slice(0,8) }}...</p>
      </div>
      <div v-else class="success-section">
        <el-icon :size="48" color="#67c23a"><SuccessFilled /></el-icon>
        <p>扫码成功，正在登录...</p>
      </div>
      <p class="tip">请使用小程序「我的」→「管理后台」扫码</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import request from "@/utils/request";

const router = useRouter();
const qrCanvas = ref<HTMLCanvasElement | null>(null);
const qrToken = ref("");
const scanConfirmed = ref(false);
let pollTimer: number | null = null;

onMounted(async () => {
  try {
    const res: any = await request.get("/auth/admin/qrcode");
    qrToken.value = res.token;
    drawQRCode(res.token);
    startPolling(res.token);
  } catch (e) {
    console.error("QR code生成失败", e);
  }
});

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer);
});

function drawQRCode(token: string) {
  const canvas = qrCanvas.value;
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  // Simple QR-like visual: grid pattern from token hash
  ctx.fillStyle = "#fff";
  ctx.fillRect(0, 0, 200, 200);
  const size = 20;
  const hash = token.split("").reduce((a, c) => a + c.charCodeAt(0), 0);
  for (let y = 0; y < 10; y++) {
    for (let x = 0; x < 10; x++) {
      const idx = y * 10 + x;
      const val = token.charCodeAt(idx % token.length);
      if ((val + hash) % 3 !== 0) {
        ctx.fillStyle = "#303133";
        ctx.fillRect(x * size, y * size, size - 2, size - 2);
      }
    }
  }
}

function startPolling(token: string) {
  pollTimer = window.setInterval(async () => {
    try {
      const res: any = await request.get(`/auth/admin/qrcode/status?token=${token}`);
      if (res?.status === "confirmed") {
        if (pollTimer) clearInterval(pollTimer);
        scanConfirmed.value = true;
        // Get JWT
        const auth: any = await request.get(
          `/auth/admin/qrcode/confirm?token=${token}&openid=${res.openid}`
        );
        localStorage.setItem("admin_token", auth.token);
        setTimeout(() => router.replace("/dashboard"), 800);
      }
    } catch (e) {
      // Continue polling
    }
  }, 2000);
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}
.login-card {
  background: #fff;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  text-align: center;
  width: 400px;
}
.login-card h1 { font-size: 20px; margin-bottom: 30px; color: #303133; }
.qrcode-section { margin-bottom: 20px; }
.qrcode-box {
  width: 200px; height: 200px; margin: 0 auto 16px;
  border: 1px solid #e4e7ed; border-radius: 8px; overflow: hidden;
}
.qrcode-tip { color: #606266; margin-bottom: 8px; }
.token-hint { font-size: 12px; color: #c0c4cc; font-family: monospace; }
.success-section { padding: 30px; }
.success-section p { margin-top: 12px; color: #67c23a; }
.tip { color: #c0c4cc; font-size: 12px; margin-top: 16px; }
</style>
