<template>
  <div class="memos-page">
    <!-- 操作栏 -->
    <div class="action-bar">
      <h2 class="page-title">📝 备忘录</h2>
      <div class="actions">
        <el-input
          v-model="searchQuery"
          placeholder="搜索备忘录..."
          clearable
          style="width: 200px"
          @keyup.enter="handleSearch"
        />
        <el-select v-model="categoryFilter" placeholder="分类" clearable style="width: 120px" @change="handleSearch">
          <el-option label="生活" value="life" />
          <el-option label="医疗" value="medical" />
          <el-option label="教育" value="education" />
          <el-option label="工作" value="work" />
          <el-option label="其他" value="other" />
        </el-select>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon> 新增备忘录
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="memoStore.loading" class="loading">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 备忘录列表 -->
    <div v-else class="memos-grid">
      <MemoCard
        v-for="memo in memoStore.memos"
        :key="memo.id"
        :memo="memo"
        @delete="handleDelete"
      />
    </div>

    <el-empty v-if="!memoStore.loading && memoStore.memos.length === 0" description="暂无备忘录" />

    <!-- 新增备忘录对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="新增备忘录"
      width="500px"
      destroy-on-close
    >
      <el-form :model="form" label-width="80px" :rules="rules" ref="formRef">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="4"
            placeholder="请输入内容"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" style="width: 100%">
            <el-option label="生活" value="life" />
            <el-option label="医疗" value="medical" />
            <el-option label="教育" value="education" />
            <el-option label="工作" value="work" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-radio-group v-model="form.priority">
            <el-radio label="low">低</el-radio>
            <el-radio label="normal">中</el-radio>
            <el-radio label="high">高</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-divider>⏰ 提醒设置</el-divider>
        <el-form-item label="提醒时间">
          <el-date-picker
            v-model="form.remind_at"
            type="datetime"
            placeholder="选择提醒时间（提前24小时通知）"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            :disabled-date="disabledDate"
          />
        </el-form-item>
        <el-form-item label="重复">
          <el-select v-model="form.repeat_type" style="width: 100%" placeholder="不重复">
            <el-option label="不重复" value="none" />
            <el-option label="每天" value="daily" />
            <el-option label="每周" value="weekly" />
            <el-option label="每月" value="monthly" />
            <el-option label="每年" value="yearly" />
          </el-select>
        </el-form-item>
        <el-form-item label="结束时间" v-if="form.repeat_type !== 'none'">
          <el-date-picker
            v-model="form.repeat_end_date"
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
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useMemoStore } from '../stores/memos'
import MemoCard from '../components/MemoCard.vue'

const memoStore = useMemoStore()
const showAddDialog = ref(false)
const submitting = ref(false)
const searchQuery = ref('')
const categoryFilter = ref('')
const formRef = ref()

const form = reactive({
  title: '',
  content: '',
  category: 'life',
  priority: 'normal',
  remind_at: '',
  repeat_type: 'none',
  repeat_end_date: '',
  notify_channels: ['feishu']
})

const disabledDate = (time) => {
  return time.getTime() < Date.now() - 24 * 60 * 60 * 1000
}

const rules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 2, max: 200, message: '长度在 2 到 200 个字符', trigger: 'blur' }
  ]
}

onMounted(() => {
  memoStore.fetchMemos()
})

const handleSearch = () => {
  const params = {}
  if (searchQuery.value) params.search = searchQuery.value
  if (categoryFilter.value) params.category = categoryFilter.value
  memoStore.fetchMemos(params)
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await memoStore.createMemo(form)
    ElMessage.success('创建成功')
    showAddDialog.value = false
    // 重置表单
    form.title = ''
    form.content = ''
    form.category = 'life'
    form.priority = 'normal'
    form.remind_at = ''
    form.repeat_type = 'none'
    form.repeat_end_date = ''
  } catch (error) {
    ElMessage.error(error.message || '创建失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await memoStore.deleteMemo(id)
    ElMessage.success('删除成功')
  } catch (error) {
    ElMessage.error(error.message || '删除失败')
  }
}
</script>

<style scoped>
.memos-page {
  padding: 20px 0;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

.page-title {
  margin: 0;
  font-size: 1.5rem;
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.loading {
  padding: 40px;
}

.memos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

@media (max-width: 768px) {
  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .actions {
    justify-content: flex-start;
  }
}
</style>
