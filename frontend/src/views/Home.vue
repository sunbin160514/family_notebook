<template>
  <div class="home">
    <!-- 搜索栏 -->
    <div class="search-section">
      <el-input
        v-model="searchQuery"
        placeholder="🔍 搜索姓名或昵称..."
        size="large"
        clearable
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
        </template>
      </el-input>
    </div>

    <!-- 加载状态 -->
    <div v-if="memberStore.loading" class="loading">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 错误提示 -->
    <el-alert
      v-if="memberStore.error"
      :title="memberStore.error"
      type="error"
      closable
      @close="memberStore.error = null"
    />

    <!-- 家人列表 -->
    <div v-else class="members-section">
      <div class="section-header">
        <h2 class="section-title">
          👨‍👩‍👧‍👦 家人列表
          <span class="count">({{ memberStore.memberCount }}人)</span>
        </h2>
        <router-link to="/members/add">
          <el-button type="primary" size="large">
            <el-icon><Plus /></el-icon> 添加家人
          </el-button>
        </router-link>
      </div>

      <div v-if="memberStore.members.length === 0" class="empty-state">
        <el-empty description="还没有添加家人">
          <router-link to="/members/add">
            <el-button type="primary">添加第一个家人</el-button>
          </router-link>
        </el-empty>
      </div>

      <div v-else class="members-grid">
        <MemberCard
          v-for="member in memberStore.members"
          :key="member.id"
          :member="member"
          @delete="handleDelete"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useMemberStore } from '../stores/members'
import MemberCard from '../components/MemberCard.vue'

const memberStore = useMemberStore()
const searchQuery = ref('')

onMounted(() => {
  memberStore.fetchMembers()
})

const handleSearch = () => {
  memberStore.fetchMembers(searchQuery.value)
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这位家人吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await memberStore.deleteMember(id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}
</script>

<style scoped>
.home {
  padding: 20px 0;
}

.search-section {
  max-width: 600px;
  margin: 0 auto 30px;
}

.loading {
  padding: 40px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.section-title {
  margin: 0;
  font-size: 1.4rem;
  color: #5A5A5A;
  font-weight: 400;
}

.count {
  font-size: 1rem;
  color: #AAA;
  font-weight: normal;
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

@media (max-width: 768px) {
  .members-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    text-align: center;
  }
}
</style>
