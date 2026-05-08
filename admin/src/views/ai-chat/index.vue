<template>
  <div class="ai-chat-records">
    <el-row :gutter="16">
      <!-- Left: Session List -->
      <el-col :span="8">
        <el-card>
          <template #header><span>对话会话</span></template>
          <div v-loading="loadingSessions">
            <el-empty v-if="!sessions.length" description="暂无对话记录" />
            <div
              v-for="s in sessions"
              :key="s.id"
              class="session-item"
              :class="{ active: selectedId === s.id }"
              @click="selectSession(s.id)"
            >
              <div class="session-title">{{ s.title || '新对话' }}</div>
              <div class="session-meta">
                <span v-if="s.openid">{{ s.openid.slice(0, 10) }}...</span>
                <span>{{ formatTime(s.updated_at) }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Right: Messages -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>{{ detail ? detail.title || '新对话' : '对话详情' }}</span>
          </template>
          <div v-if="!selectedId">
            <el-empty description="请选择左侧会话查看" />
          </div>
          <div v-else-if="loadingDetail" v-loading="loadingDetail" style="min-height:200px" />
          <div v-else class="chat-messages">
            <div
              v-for="m in detail?.messages || []"
              :key="m.id"
              class="message-item"
              :class="m.role"
            >
              <div class="msg-role">{{ m.role === 'user' ? '用户' : 'AI' }}</div>
              <div class="msg-content">{{ m.content }}</div>
              <div v-if="m.sources && m.sources.length" class="msg-sources">
                <el-tag
                  v-for="(src, i) in m.sources"
                  :key="i"
                  size="small"
                  effect="plain"
                >
                  {{ src.name }}
                </el-tag>
              </div>
              <div class="msg-meta">
                <span v-if="m.llm_model">{{ m.llm_model }}</span>
                <span>{{ formatTime(m.created_at) }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import request from "@/utils/request";

const sessions = ref<any[]>([]);
const detail = ref<any>(null);
const selectedId = ref<number | null>(null);
const loadingSessions = ref(false);
const loadingDetail = ref(false);

onMounted(() => fetchSessions());

async function fetchSessions() {
  loadingSessions.value = true;
  try {
    const res: any = await request.get("/ai/sessions");
    sessions.value = res?.items || [];
  } finally {
    loadingSessions.value = false;
  }
}

async function selectSession(id: number) {
  selectedId.value = id;
  loadingDetail.value = true;
  try {
    detail.value = await request.get(`/ai/sessions/${id}`);
  } catch {
    detail.value = null;
  } finally {
    loadingDetail.value = false;
  }
}

function formatTime(t: string | null): string {
  if (!t) return "-";
  return new Date(t).toLocaleString("zh-CN");
}
</script>

<style scoped>
.session-item {
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background 0.2s;
}
.session-item:hover,
.session-item.active {
  background: #ecf2ff;
}
.session-title {
  font-size: 14px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.session-meta {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  display: flex;
  justify-content: space-between;
}

.chat-messages {
  max-height: 600px;
  overflow-y: auto;
}
.message-item {
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
}
.message-item.user .msg-role {
  color: #2979ff;
}
.message-item.assistant .msg-role {
  color: #19be6b;
}
.msg-role {
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 4px;
}
.msg-content {
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}
.msg-sources {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.msg-meta {
  font-size: 11px;
  color: #999;
  margin-top: 6px;
  display: flex;
  gap: 12px;
}
</style>
