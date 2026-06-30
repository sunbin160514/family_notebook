<template>
  <div class="memo-detail-page">
    <el-page-header title="备忘录详情" @back="$router.push('/memos')" />

    <el-skeleton :rows="5" animated v-if="memoStore.loading" />

    <template v-else-if="memoStore.currentMemo">
      <el-card class="detail-card">
        <div class="memo-header">
          <div class="tags">
            <el-tag :type="categoryType" size="large">{{ categoryLabel }}</el-tag>
            <el-tag :type="priorityType" effect="dark" size="large">
              {{ priorityLabel }}优先级
            </el-tag>
          </div>
        </div>

        <h2 class="title">{{ memoStore.currentMemo.title }}</h2>
        <p class="content">{{ memoStore.currentMemo.content || '暂无内容' }}</p>

        <!-- 提醒信息展示 -->
        <div v-if="reminders.length > 0" class="reminder-section">
          <h4 class="reminder-title"><el-icon><AlarmClock /></el-icon> 提醒设置</h4>
          <div v-for="reminder in reminders" :key="reminder.id" class="reminder-item">
            <div class="reminder-row">
              <span class="reminder-label">提醒时间：</span>
              <span class="reminder-value">{{ formatDateTime(reminder.remind_at) }}</span>
              <el-tag :type="reminder.status === 'pending' ? 'warning' : 'success'" size="small">
                {{ reminder.status === 'pending' ? '待发送' : '已发送' }}
              </el-tag>
            </div>
            <div v-if="reminder.repeat_type !== 'none'" class="reminder-row">
              <span class="reminder-label">重复：</span>
              <span class="reminder-value">{{ repeatTypeLabel(reminder.repeat_type) }}</span>
            </div>
          </div>
        </div>

        <div class="meta-info">
          <span v-if="memoStore.currentMemo.member_name">
            👤 {{ memoStore.currentMemo.member_name }}
          </span>
          <span>⏱ {{ formatDate(memoStore.currentMemo.created_at) }}</span>
          <span v-if="reminders.length > 0"><el-icon><AlarmClock /></el-icon> {{ formatDateTime(reminders[0].remind_at) }}</span>
        </div>

        <div class="actions">
          <el-button type="primary" @click="openEditDialog">编辑</el-button>
          <el-button @click="$router.push('/memos')">返回</el-button>
        </div>
      </el-card>
    </template>

    <el-empty v-else description="备忘录不存在" />

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑备忘录" width="500px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="editForm.content" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="editForm.category" style="width: 100%">
            <el-option label="生活" value="life" />
            <el-option label="医疗" value="medical" />
            <el-option label="教育" value="education" />
            <el-option label="工作" value="work" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-radio-group v-model="editForm.priority">
            <el-radio label="low">低</el-radio>
            <el-radio label="normal">中</el-radio>
            <el-radio label="high">高</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-divider>⏰ 提醒设置</el-divider>
        <el-form-item label="提醒时间">
          <el-date-picker
            v-model="editForm.remind_at"
            type="datetime"
            placeholder="选择提醒时间（提前24小时通知）"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            :disabled-date="disabledDate"
          />
        </el-form-item>
        <el-form-item label="重复">
          <el-select v-model="editForm.repeat_type" style="width: 100%" placeholder="不重复">
            <el-option label="不重复" value="none" />
            <el-option label="每天" value="daily" />
            <el-option label="每周" value="weekly" />
            <el-option label="每月" value="monthly" />
            <el-option label="每年" value="yearly" />
          </el-select>
        </el-form-item>
        <el-form-item label="结束时间" v-if="editForm.repeat_type !== 'none'">
          <el-date-picker
            v-model="editForm.repeat_end_date"
            type="datetime"
            placeholder="重复结束时间（可选，默认23:59）"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            :default-time="new Date(2000, 1, 1, 23, 59, 0)"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdate" :loading="updating">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useMemoStore } from '../stores/memos'
import { reminderApi } from '../api'

const route = useRoute()
const memoStore = useMemoStore()
const showEditDialog = ref(false)
const updating = ref(false)
const reminders = ref([])
const editForm = reactive({
  title: '',
  content: '',
  category: 'life',
  priority: 'normal',
  remind_at: '',
  repeat_type: 'none',
  repeat_end_date: '',
  reminder_id: null
})

const repeatTypeMap = {
  none: '不重复',
  daily: '每天',
  weekly: '每周',
  monthly: '每月',
  yearly: '每年'
}

const disabledDate = (time) => {
  return time.getTime() < Date.now() - 24 * 60 * 60 * 1000
}

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
  return categoryMap[memoStore.currentMemo?.category]?.label || '其他'
})

const categoryType = computed(() => {
  return categoryMap[memoStore.currentMemo?.category]?.type || ''
})

const priorityLabel = computed(() => {
  return priorityMap[memoStore.currentMemo?.priority]?.label || '中'
})

const priorityType = computed(() => {
  return priorityMap[memoStore.currentMemo?.priority]?.type || 'warning'
})

const fetchReminders = async () => {
  try {
    const response = await reminderApi.getAll(route.params.id)
    reminders.value = response.data
  } catch (error) {
    console.error('获取提醒失败:', error)
  }
}

onMounted(async () => {
  const id = route.params.id
  if (id) {
    await memoStore.fetchMemoById(id)
    if (memoStore.currentMemo) {
      Object.assign(editForm, memoStore.currentMemo)
    }
    await fetchReminders()
  }
})

const openEditDialog = () => {
  // 填充备忘录数据
  Object.assign(editForm, memoStore.currentMemo)

  // 填充提醒数据（如果有）
  if (reminders.value.length > 0) {
    const reminder = reminders.value[0]
    editForm.remind_at = reminder.remind_at
    editForm.repeat_type = reminder.repeat_type

    // 处理结束时间格式：如果是纯日期格式，补充时间部分
    if (reminder.repeat_end_date) {
      const endDate = reminder.repeat_end_date
      if (endDate.length === 10) {  // YYYY-MM-DD 格式
        editForm.repeat_end_date = endDate + ' 23:59:00'
      } else {
        editForm.repeat_end_date = endDate
      }
    } else {
      editForm.repeat_end_date = ''
    }

    editForm.reminder_id = reminder.id
  } else {
    editForm.remind_at = ''
    editForm.repeat_type = 'none'
    editForm.repeat_end_date = ''
    editForm.reminder_id = null
  }

  showEditDialog.value = true
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const repeatTypeLabel = (type) => {
  return repeatTypeMap[type] || '不重复'
}

const handleUpdate = async () => {
  updating.value = true
  try {
    // 1. 更新备忘录
    const memoData = {
      title: editForm.title,
      content: editForm.content,
      category: editForm.category,
      priority: editForm.priority
    }
    await memoStore.updateMemo(route.params.id, memoData)

    // 2. 处理提醒更新
    if (editForm.remind_at) {
      const reminderData = {
        memo_id: parseInt(route.params.id),
        title: `📋 ${editForm.title}`,
        remind_at: editForm.remind_at,
        repeat_type: editForm.repeat_type || 'none',
        repeat_end_date: editForm.repeat_end_date || null,
        notify_channels: ['feishu']
      }

      if (editForm.reminder_id) {
        // 更新现有提醒
        await reminderApi.update(editForm.reminder_id, reminderData)
      } else {
        // 创建新提醒
        await reminderApi.create(reminderData)
      }
    } else if (editForm.reminder_id) {
      // 删除提醒
      await reminderApi.delete(editForm.reminder_id)
    }

    // 3. 刷新提醒列表
    await fetchReminders()

    ElMessage.success('更新成功')
    showEditDialog.value = false
  } catch (error) {
    ElMessage.error(error.message || '更新失败')
  } finally {
    updating.value = false
  }
}
</script>

<style scoped>
.memo-detail-page {
  padding: 20px 0;
}

.detail-card {
  max-width: 700px;
  margin: 30px auto;
}

.memo-header {
  margin-bottom: 20px;
}

.tags {
  display: flex;
  gap: 10px;
}

.title {
  margin: 0 0 20px 0;
  font-size: 1.5rem;
  color: #4A4A4A;
}

.content {
  font-size: 1rem;
  line-height: 1.8;
  color: #666;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.reminder-section {
  background: #FDF8F3;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
  border: 1px solid rgba(232, 196, 160, 0.3);
}

.reminder-title {
  margin: 0 0 12px 0;
  font-size: 1rem;
  color: #D4A574;
  font-weight: 500;
}

.reminder-item {
  background: white;
  border-radius: 8px;
  padding: 12px 16px;
}

.reminder-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.reminder-row:last-child {
  margin-bottom: 0;
}

.reminder-label {
  color: #999;
  font-size: 0.9rem;
}

.reminder-value {
  color: #5A5A5A;
  font-weight: 500;
  flex: 1;
}

.meta-info {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  font-size: 0.9rem;
  color: #999;
  margin-bottom: 20px;
}

.actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  padding-top: 20px;
  border-top: 1px solid #eee;
}
</style>
