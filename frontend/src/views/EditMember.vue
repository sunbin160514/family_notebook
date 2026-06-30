<template>
  <div class="edit-member-page">
    <el-page-header :title="'编辑 - ' + (memberStore.currentMember?.name || '')" @back="$router.back()" />

    <el-skeleton :rows="5" animated v-if="memberStore.loading" />

    <el-card v-else-if="memberStore.currentMember" class="form-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="member-form"
      >
        <el-row :gutter="20">
          <el-col :span="12" :xs="24">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12" :xs="24">
            <el-form-item label="昵称">
              <el-input v-model="form.nickname" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12" :xs="24">
            <el-form-item label="阳历生日">
              <el-date-picker
                v-model="form.solar_birthday"
                type="date"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12" :xs="24">
            <el-form-item label="阴历生日">
              <el-input v-model="form.lunar_birthday" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="喜欢的食物">
          <el-input v-model="form.favorite_foods" type="textarea" :rows="2" />
        </el-form-item>

        <el-form-item label="喜欢的运动">
          <el-input v-model="form.favorite_sports" type="textarea" :rows="2" />
        </el-form-item>

        <el-form-item label="讨厌的食物">
          <el-input v-model="form.disliked_foods" type="textarea" :rows="2" />
        </el-form-item>

        <el-form-item label="日常注意事项">
          <el-input v-model="form.daily_notes" type="textarea" :rows="3" />
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="form.remarks" type="textarea" :rows="2" />
        </el-form-item>

        <el-form-item>
          <el-button @click="$router.back()">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-empty v-else description="家人不存在" />
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useMemberStore } from '../stores/members'

const route = useRoute()
const router = useRouter()
const memberStore = useMemberStore()
const formRef = ref()
const submitting = ref(false)

const form = reactive({
  name: '',
  nickname: '',
  solar_birthday: '',
  lunar_birthday: '',
  favorite_foods: '',
  favorite_sports: '',
  disliked_foods: '',
  daily_notes: '',
  remarks: ''
})

const rules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ]
}

onMounted(async () => {
  const id = route.params.id
  if (id) {
    await memberStore.fetchMemberById(id)
    if (memberStore.currentMember) {
      Object.assign(form, memberStore.currentMember)
    }
  }
})

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await memberStore.updateMember(route.params.id, form)
    ElMessage.success('更新成功')
    router.push(`/members/${route.params.id}`)
  } catch (error) {
    ElMessage.error(error.message || '更新失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.edit-member-page {
  padding: 20px 0;
}

.form-card {
  max-width: 800px;
  margin: 30px auto;
}

.member-form {
  padding: 20px;
}
</style>
