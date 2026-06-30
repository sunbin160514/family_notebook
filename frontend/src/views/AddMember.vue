<template>
  <div class="add-member-page">
    <el-page-header title="添加家人" @back="$router.back()" />

    <el-card class="form-card">
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
              <el-input v-model="form.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12" :xs="24">
            <el-form-item label="昵称">
              <el-input v-model="form.nickname" placeholder="请输入昵称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12" :xs="24">
            <el-form-item label="阳历生日">
              <el-date-picker
                v-model="form.solar_birthday"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12" :xs="24">
            <el-form-item label="阴历生日">
              <el-input v-model="form.lunar_birthday" placeholder="例如：正月初一" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="喜欢的食物">
          <el-input
            v-model="form.favorite_foods"
            type="textarea"
            :rows="2"
            placeholder="请输入喜欢的食物，多个用逗号分隔"
          />
        </el-form-item>

        <el-form-item label="喜欢的运动">
          <el-input
            v-model="form.favorite_sports"
            type="textarea"
            :rows="2"
            placeholder="请输入喜欢的运动，多个用逗号分隔"
          />
        </el-form-item>

        <el-form-item label="讨厌的食物">
          <el-input
            v-model="form.disliked_foods"
            type="textarea"
            :rows="2"
            placeholder="请输入讨厌的食物，多个用逗号分隔"
          />
        </el-form-item>

        <el-form-item label="日常注意事项">
          <el-input
            v-model="form.daily_notes"
            type="textarea"
            :rows="3"
            placeholder="请输入日常注意事项，如过敏、疾病等"
          />
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="form.remarks"
            type="textarea"
            :rows="2"
            placeholder="其他备注信息"
          />
        </el-form-item>

        <el-form-item>
          <el-button @click="$router.back()">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useMemberStore } from '../stores/members'

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
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await memberStore.createMember(form)
    ElMessage.success('添加成功')
    router.push('/')
  } catch (error) {
    ElMessage.error(error.message || '添加失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.add-member-page {
  padding: 20px 0;
}

.form-card {
  max-width: 800px;
  margin: 30px auto;
}

.member-form {
  padding: 20px;
}

@media (max-width: 768px) {
  .member-form {
    padding: 10px;
  }
}
</style>
