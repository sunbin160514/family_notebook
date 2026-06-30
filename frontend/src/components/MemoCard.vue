<template>
  <div class="memo-card" :class="`priority-${memo.priority}`">
    <div class="card-header">
      <el-tag :type="categoryType" size="small">{{ categoryLabel }}</el-tag>
      <el-tag :type="priorityType" size="small" effect="dark">
        {{ priorityLabel }}
      </el-tag>
    </div>

    <h3 class="title">{{ memo.title }}</h3>
    <p class="content">{{ memo.content || '暂无内容' }}</p>

    <div v-if="hasReminder" class="reminder-info" :class="{ 'reminder-urgent': isUrgent }">
      <span class="reminder-text">
        {{ reminderLabel }}
      </span>
    </div>

    <div class="card-footer">
      <div class="meta">
        <span v-if="memo.member_name" class="member">
          <el-icon><User /></el-icon> {{ memo.member_name }}
        </span>
        <span class="date" v-if="memo.created_at">
          <el-icon><Clock /></el-icon> {{ formatDate(memo.created_at) }}
        </span>
      </div>
      <div class="actions">
        <router-link :to="`/memos/${memo.id}`">
          <el-button type="primary" size="small" plain>查看详情</el-button>
        </router-link>
        <el-popconfirm
          title="确定要删除吗？"
          confirm-button-text="确定"
          cancel-button-text="取消"
          @confirm="handleDelete"
        >
          <template #reference>
            <el-button type="danger" size="small" plain>删除</el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  memo: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['delete'])

const hasReminder = computed(() => {
  return props.memo.reminders && props.memo.reminders.length > 0
})

const reminderInfo = computed(() => {
  if (!hasReminder.value) return null
  return props.memo.reminders[0]
})

const isUrgent = computed(() => {
  if (!reminderInfo.value) return false
  const remindAt = new Date(reminderInfo.value.remind_at)
  const now = new Date()
  const diff = (remindAt - now) / (1000 * 60 * 60) // 小时
  return diff < 24 && diff > 0
})

const reminderLabel = computed(() => {
  if (!reminderInfo.value) return ''
  const remindAt = new Date(reminderInfo.value.remind_at)
  const now = new Date()
  const diff = (remindAt - now) / (1000 * 60 * 60) // 小时

  if (diff < 0) return '已过期'
  if (diff < 24) return `⏰ ${Math.ceil(diff)}小时后提醒`
  if (diff < 48) return '⏰ 明天提醒'
  return `⏰ ${remindAt.toLocaleDateString('zh-CN')} 提醒`
})

const categoryMap = {
  life: { label: '生活', type: '' },
  medical: { label: '医疗', type: 'success' },
  education: { label: '教育', type: 'warning' },
  work: { label: '工作', type: 'info' },
  other: { label: '其他', type: 'info' }
}

const priorityMap = {
  low: { label: '低', type: 'success' },
  normal: { label: '中', type: 'warning' },
  high: { label: '高', type: 'danger' }
}

const categoryLabel = computed(() => {
  return categoryMap[props.memo.category]?.label || '其他'
})

const categoryType = computed(() => {
  return categoryMap[props.memo.category]?.type || ''
})

const priorityLabel = computed(() => {
  return priorityMap[props.memo.priority]?.label || '中'
})

const priorityType = computed(() => {
  return priorityMap[props.memo.priority]?.type || 'warning'
})

const formatDate = (dateStr) => {
  if (!dateStr || dateStr === 'None') return ''
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return ''
  return date.toLocaleDateString('zh-CN', {
    month: 'numeric',
    day: 'numeric'
  })
}

const handleDelete = () => {
  emit('delete', props.memo.id)
}
</script>

<style scoped>
.memo-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #ddd;
  transition: all 0.3s ease;
}

.memo-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.memo-card.priority-high {
  border-left-color: #F56C6C;
}

.memo-card.priority-normal {
  border-left-color: #E6A23C;
}

.memo-card.priority-low {
  border-left-color: #67C23A;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.title {
  margin: 0 0 10px 0;
  font-size: 1.1rem;
  color: #4A4A4A;
  font-weight: 600;
  line-height: 1.4;
}

.content {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.6;
  margin-bottom: 15px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.reminder-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 12px;
  padding: 10px 14px;
  background: linear-gradient(135deg, #FFF8F0 0%, #FDF2E9 100%);
  border-radius: 12px;
  border: 1px solid rgba(232, 196, 160, 0.3);
}

.reminder-icon {
  font-size: 1.1rem;
  color: #E8A87C;
  animation: swing 2s ease-in-out infinite;
}

@keyframes swing {
  0%, 100% { transform: rotate(-5deg); }
  50% { transform: rotate(5deg); }
}

.reminder-text {
  font-weight: 500;
}

.reminder-urgent {
  background: linear-gradient(135deg, #FFF0E8 0%, #FFE4D6 100%);
  border-color: rgba(232, 150, 120, 0.5);
}

.reminder-urgent .reminder-icon {
  color: #D47A5C;
}

.reminder-urgent .reminder-text {
  color: #C85A3A;
  font-weight: 600;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.meta {
  display: flex;
  gap: 15px;
  font-size: 0.85rem;
  color: #999;
  flex: 1;
  min-width: 0;
}

.meta span {
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.date {
  color: #888;
}

.actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 480px) {
  .card-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
