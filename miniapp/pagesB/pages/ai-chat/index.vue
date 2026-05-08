<template>
  <view class="ai-chat-page">
    <scroll-view class="chat-body" scroll-y :scroll-into-view="scrollTarget" :scroll-with-animation="true">
      <view v-if="messages.length === 0" class="welcome">
        <text class="welcome-title">AI 智能顾问</text>
        <text class="welcome-desc">描述您的保温需求，AI 为您推荐合适材料</text>
        <view class="quick-questions">
          <text class="quick-label">试试问：</text>
          <view v-for="(q, i) in quickQuestions" :key="i" class="quick-item" @click="sendMessage(q)">{{ q }}</view>
        </view>
      </view>

      <view v-for="(m, idx) in messages" :key="idx" :id="'msg-'+idx" class="msg-wrapper">
        <view class="message-item" :class="m.role">
          <view class="msg-avatar"><text v-if="m.role==='assistant'">AI</text><text v-else>我</text></view>
          <view class="msg-bubble">
            <text class="msg-content">{{ m.content }}</text>
            <view v-if="m.sources && m.sources.length" class="msg-sources">
              <text class="source-title">相关产品：</text>
              <view v-for="(src,si) in m.sources" :key="si" class="source-item" @click="goDetail(src.id)">
                <text class="source-name">{{ src.name }}</text>
                <text v-if="src.reference_price" class="source-price">¥{{ src.reference_price }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <view v-if="loading" class="typing"><text>AI 思考中...</text></view>
      <view id="msg-bottom" style="height:20rpx" />
    </scroll-view>

    <view class="chat-input-bar">
      <input class="chat-input" v-model="inputText" :disabled="loading" placeholder="输入需求，如：耐高温管道保温材料" confirm-type="send" @confirm="sendCurrent" />
      <button class="send-btn" :disabled="loading||!inputText.trim()" @click="sendCurrent">发送</button>
    </view>
  </view>
</template>

<script>
import api from "@/common/api.js";
export default {
  data() {
    return {
      messages: [], inputText: "", loading: false,
      sessionId: null, scrollTarget: "",
      quickQuestions: [
        "我需要外墙保温，A1级防火有什么推荐？",
        "管道保温耐高温材料有哪些？",
        "冷库保温用什么材料好，要防潮的",
        "屋顶保温材料选什么？性价比高的",
      ],
    };
  },
  methods: {
    sendCurrent() {
      if (this.loading || !this.inputText.trim()) return;
      this.sendMessage(this.inputText.trim());
      this.inputText = "";
    },
    async sendMessage(text) {
      this.messages.push({ role: "user", content: text });
      this.scrollToBottom();
      this.loading = true;
      try {
        const res = await api.sendChatMessage({
          message: text,
          session_id: this.sessionId,
          openid: "dev-user",
        });
        this.sessionId = res.session_id;
        this.messages.push({
          role: "assistant",
          content: res.message.content,
          sources: res.message.sources || [],
        });
      } catch (e) {
        this.messages.push({
          role: "assistant",
          content: "抱歉，AI 服务暂不可用，请稍后重试。",
          sources: [],
        });
      } finally {
        this.loading = false;
        this.scrollToBottom();
      }
    },
    scrollToBottom() {
      this.$nextTick(() => { this.scrollTarget = "msg-bottom"; });
    },
    goDetail(productId) {
      uni.navigateTo({ url: `/pagesA/pages/product-detail/index?id=${productId}` });
    },
  },
};
</script>

<style scoped lang="scss">
.ai-chat-page { display:flex; flex-direction:column; height:100vh; background:#f5f5f5; }
.chat-body { flex:1; padding:20rpx 24rpx; }
.welcome { text-align:center; padding:60rpx 40rpx; }
.welcome-title { font-size:36rpx; font-weight:bold; color:#2979ff; display:block; }
.welcome-desc { font-size:26rpx; color:#999; margin-top:16rpx; display:block; }
.quick-questions { margin-top:40rpx; text-align:left; }
.quick-label { font-size:24rpx; color:#999; display:block; margin-bottom:16rpx; }
.quick-item { background:#fff; border:1rpx solid #e0e0e0; border-radius:12rpx; padding:16rpx 20rpx; margin-bottom:12rpx; font-size:26rpx; color:#333; }
.quick-item:active { background:#ecf2ff; border-color:#2979ff; }
.msg-wrapper { margin-bottom:24rpx; }
.message-item { display:flex; align-items:flex-start; }
.message-item.user { flex-direction:row-reverse; }
.msg-avatar { width:60rpx; height:60rpx; border-radius:50%; background:#2979ff; color:#fff; font-size:24rpx; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.message-item.user .msg-avatar { background:#19be6b; }
.msg-bubble { max-width:500rpx; background:#fff; border-radius:16rpx; padding:16rpx 20rpx; margin:0 16rpx; }
.message-item.user .msg-bubble { background:#2979ff; color:#fff; }
.msg-content { font-size:28rpx; line-height:1.6; white-space:pre-wrap; }
.msg-sources { margin-top:12rpx; padding-top:12rpx; border-top:1rpx solid #eee; }
.source-title { font-size:22rpx; color:#999; }
.source-item { display:flex; justify-content:space-between; align-items:center; background:#f8f8f8; padding:8rpx 12rpx; border-radius:8rpx; margin-top:8rpx; }
.source-name { font-size:24rpx; color:#2979ff; }
.source-price { font-size:24rpx; color:#fa3534; }
.typing { text-align:center; font-size:24rpx; color:#999; padding:20rpx; }
.chat-input-bar { display:flex; align-items:center; background:#fff; padding:16rpx 20rpx; border-top:1rpx solid #eee; padding-bottom:calc(16rpx+env(safe-area-inset-bottom)); }
.chat-input { flex:1; height:70rpx; background:#f5f5f5; border-radius:35rpx; padding:0 24rpx; font-size:28rpx; }
.send-btn { margin-left:16rpx; background:#2979ff; color:#fff; border:none; border-radius:35rpx; padding:0 30rpx; height:70rpx; line-height:70rpx; font-size:28rpx; }
.send-btn[disabled] { background:#ccc; }
</style>
