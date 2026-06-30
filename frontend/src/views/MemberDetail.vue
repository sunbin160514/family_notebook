<template>
  <div class="member-detail-page">
    <el-page-header :title="memberStore.currentMember?.name" @back="$router.push('/')" />

    <el-skeleton :rows="5" animated v-if="memberStore.loading" />

    <template v-else-if="memberStore.currentMember">
      <el-card class="detail-card">
        <div class="avatar-section">
          <div class="avatar">{{ memberStore.currentMember.name?.charAt(0) }}</div>
          <h2 class="name">{{ memberStore.currentMember.name }}</h2>
          <span v-if="memberStore.currentMember.nickname" class="nickname">
            {{ memberStore.currentMember.nickname }}
          </span>
        </div>

        <el-descriptions :column="1" border>
          <el-descriptions-item label="阳历生日">
            {{ memberStore.currentMember.solar_birthday || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="阴历生日">
            {{ memberStore.currentMember.lunar_birthday || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="喜欢的食物">
            {{ memberStore.currentMember.favorite_foods || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="喜欢的运动">
            {{ memberStore.currentMember.favorite_sports || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="讨厌的食物">
            {{ memberStore.currentMember.disliked_foods || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="日常注意事项">
            {{ memberStore.currentMember.daily_notes || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="备注">
            {{ memberStore.currentMember.remarks || '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="actions">
          <router-link :to="`/members/${memberStore.currentMember.id}/edit`">
            <el-button type="primary">编辑</el-button>
          </router-link>
          <el-button @click="$router.push('/')">返回</el-button>
        </div>
      </el-card>
    </template>

    <el-empty v-else description="家人不存在" />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMemberStore } from '../stores/members'

const route = useRoute()
const memberStore = useMemberStore()

onMounted(() => {
  const id = route.params.id
  if (id) {
    memberStore.fetchMemberById(id)
  }
})
</script>

<style scoped>
.member-detail-page {
  padding: 20px 0;
}

.detail-card {
  max-width: 600px;
  margin: 30px auto;
}

.avatar-section {
  text-align: center;
  padding: 30px;
  background: linear-gradient(135deg, #FF9A76 0%, #FFB4A2 100%);
  margin: -20px -20px 30px;
  border-radius: 8px 8px 0 0;
  color: white;
}

.avatar {
  width: 100px;
  height: 100px;
  background: rgba(255, 255, 255, 0.9);
  color: #FF9A76;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  font-weight: 600;
  margin: 0 auto 20px;
}

.name {
  margin: 0 0 10px;
  font-size: 1.8rem;
}

.nickname {
  font-size: 1.1rem;
  opacity: 0.9;
}

.actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

@media (max-width: 768px) {
  .actions {
    flex-direction: column;
  }
}
</style>
