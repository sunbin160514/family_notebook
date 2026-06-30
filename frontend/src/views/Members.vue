<template>
  <div class="members-page">
    <h2 class="page-title">👨‍👩‍👧‍👦 家人列表</h2>

    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索家人姓名或昵称"
        clearable
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch">
            <el-icon><Search /></el-icon>
          </el-button>
        </template>
      </el-input>
      <router-link to="/members/add">
        <el-button type="primary">添加家人</el-button>
      </router-link>
    </div>

    <el-row v-if="memberStore.loading" :gutter="20">
      <el-col v-for="i in 4" :key="i" :xs="24" :sm="12" :md="8" :lg="6">
        <el-skeleton animated />
      </el-col>
    </el-row>

    <el-row v-else-if="memberStore.members.length" :gutter="20">
      <el-col
        v-for="member in memberStore.members"
        :key="member.id"
        :xs="24"
        :sm="12"
        :md="8"
        :lg="6"
        class="member-col"
      >
        <MemberCard :member="member" />
      </el-col>
    </el-row>

    <el-empty v-else description="暂无家人信息" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { useMemberStore } from '../stores/members'
import MemberCard from '../components/MemberCard.vue'

const memberStore = useMemberStore()
const searchKeyword = ref('')

onMounted(() => {
  memberStore.fetchMembers()
})

const handleSearch = () => {
  memberStore.fetchMembers(searchKeyword.value)
}
</script>

<style scoped>
.members-page {
  padding: 20px 0;
}

.page-title {
  margin-bottom: 20px;
  font-size: 1.5rem;
  color: #4A4A4A;
}

.search-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.search-bar .el-input {
  flex: 1;
}

.member-col {
  margin-bottom: 20px;
}
</style>
