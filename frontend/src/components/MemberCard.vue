<template>
  <div class="member-card">
    <div class="card-header">
      <div class="avatar">{{ member.name?.charAt(0) }}</div>
      <div class="info">
        <h3 class="name">{{ member.name }}</h3>
        <span v-if="member.nickname" class="nickname">({{ member.nickname }})</span>
      </div>
      <div class="actions">
        <router-link :to="`/members/${member.id}`" class="action-btn view">
          <el-icon><View /></el-icon>
        </router-link>
        <router-link :to="`/members/${member.id}/edit`" class="action-btn edit">
          <el-icon><Edit /></el-icon>
        </router-link>
        <el-popconfirm
          title="确定要删除吗？"
          confirm-button-text="确定"
          cancel-button-text="取消"
          @confirm="handleDelete"
        >
          <template #reference>
            <button class="action-btn delete">
              <el-icon><Delete /></el-icon>
            </button>
          </template>
        </el-popconfirm>
      </div>
    </div>

    <div class="card-body">
      <div v-if="member.solar_birthday" class="info-row birthday">
        <span class="label">🎂 生日:</span>
        <span class="value">
          阳历 {{ member.solar_birthday }}
          <span v-if="member.lunar_birthday">| 阴历 {{ member.lunar_birthday }}</span>
        </span>
      </div>

      <div v-if="member.favorite_foods" class="info-row">
        <span class="label">😋 喜欢的食物:</span>
        <span class="value">{{ member.favorite_foods }}</span>
      </div>

      <div v-if="member.favorite_sports" class="info-row">
        <span class="label">🏃 喜欢的运动:</span>
        <span class="value">{{ member.favorite_sports }}</span>
      </div>

      <div v-if="member.disliked_foods" class="info-row warning">
        <span class="label">🚫 讨厌的食物:</span>
        <span class="value">{{ member.disliked_foods }}</span>
      </div>

      <div v-if="member.daily_notes" class="info-row important">
        <span class="label">⚠️ 日常注意:</span>
        <span class="value">{{ member.daily_notes }}</span>
      </div>

      <div v-if="member.remarks" class="info-row notes">
        <span class="label">📝 备注:</span>
        <span class="value">{{ member.remarks }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  member: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['delete'])

const handleDelete = () => {
  emit('delete', props.member.id)
}
</script>

<style scoped>
.member-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(212, 165, 116, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid rgba(232, 196, 160, 0.3);
}

.member-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(212, 165, 116, 0.18);
}

.card-header {
  background: linear-gradient(135deg, #FDF8F3 0%, white 100%);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  border-bottom: 1px solid rgba(232, 196, 160, 0.25);
}

.avatar {
  width: 52px;
  height: 52px;
  background: linear-gradient(135deg, #E8C4A0 0%, #F0D4B8 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 500;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(232, 196, 160, 0.4);
}

.info {
  flex: 1;
}

.name {
  margin: 0;
  font-size: 1.15rem;
  color: #5A5A5A;
  font-weight: 500;
}

.nickname {
  font-size: 0.9rem;
  color: #9A9A9A;
}

.actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  text-decoration: none;
  background: #FDF8F3;
}

.action-btn.view {
  color: #A8B8C8;
}

.action-btn.edit {
  color: #D4C4A8;
}

.action-btn.delete {
  color: #D4B8B0;
}

.action-btn:hover {
  background: #F5EBE0;
  transform: scale(1.1);
}

.card-body {
  padding: 18px 20px;
}

.info-row {
  margin-bottom: 10px;
  display: flex;
  gap: 10px;
  font-size: 0.92rem;
}

.info-row:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 400;
  color: #A8A8A8;
  flex-shrink: 0;
  min-width: 95px;
}

.value {
  color: #5A5A5A;
  flex: 1;
  word-break: break-word;
  line-height: 1.5;
}

.info-row.birthday .value {
  color: #D4A574;
  font-weight: 500;
}

.info-row.warning {
  background: #FDF2F0;
  padding: 10px 14px;
  border-radius: 12px;
  margin: 0 -4px 12px;
}

.info-row.warning .label {
  color: #C8A8A0;
}

.info-row.important {
  background: #FDF8F0;
  padding: 10px 14px;
  border-radius: 12px;
  margin: 0 -4px 12px;
  border-left: 3px solid #E8C4A0;
}

.info-row.important .label {
  color: #D4B090;
}

.info-row.notes {
  background: #F8F5F0;
  padding: 10px 14px;
  border-radius: 12px;
  margin: 0 -4px;
}

@media (max-width: 768px) {
  .card-header {
    flex-wrap: wrap;
  }

  .actions {
    width: 100%;
    justify-content: flex-end;
    margin-top: 10px;
  }

  .info-row {
    flex-direction: column;
    gap: 4px;
  }

  .label {
    min-width: auto;
  }
}
</style>
