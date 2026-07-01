<template>
  <div class="settings-page">
    <h2 class="page-title">⚙️ 系统设置</h2>

    <el-card class="setting-card">
      <template #header>
        <div class="card-header">
          <span>🔔 通知设置</span>
        </div>
      </template>

      <el-form :model="form" label-width="150px">
        <el-form-item label="启用消息通知">
          <el-switch v-model="form.notification_enabled" />
        </el-form-item>

        <el-divider>飞书机器人</el-divider>

        <el-form-item label="Webhook 地址">
          <el-input
            v-model="form.feishu_webhook_url"
            placeholder="https://open.feishu.cn/open-apis/bot/v2/hook/..."
          />
        </el-form-item>

        <el-form-item label="Secret">
          <el-input
            v-model="form.feishu_secret"
            placeholder="签名校验密钥（可选）"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button @click="testFeishu" :disabled="!form.feishu_webhook_url">
            测试飞书推送
          </el-button>
        </el-form-item>

        <el-divider>微信机器人</el-divider>

        <el-form-item label="Webhook 地址">
          <el-input
            v-model="form.weixin_webhook_url"
            placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=..."
          />
        </el-form-item>

        <el-form-item>
          <el-button @click="testWeixin" :disabled="!form.weixin_webhook_url">
            测试微信推送
          </el-button>
        </el-form-item>

        <el-divider> PushPlus（个人微信）</el-divider>

        <el-form-item label="Token">
          <el-input
            v-model="form.pushplus_token"
            placeholder="PushPlus 用户 Token，绑定个人微信"
          />
        </el-form-item>

        <el-form-item>
          <el-button @click="testPushPlus" :disabled="!form.pushplus_token">
            测试微信推送
          </el-button>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSave" :loading="saving">
            保存设置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="setting-card mt-20">
      <template #header>
        <div class="card-header">
          <span>📖 使用说明</span>
        </div>
      </template>

      <div class="help-content">
        <h4>如何获取 PushPlus Token（个人微信）</h4>
        <ol>
          <li>关注公众号「PushPlus 推送加」</li>
          <li>点击菜单「功能」→「开发设置」</li>
          <li>复制页面上的「Token」</li>
          <li>粘贴到上方输入框并保存</li>
        </ol>

        <h4>如何获取飞书 Webhook</h4>
        <ol>
          <li>在飞书群聊中点击右上角「设置」</li>
          <li>选择「群机器人」→「添加机器人」</li>
          <li>选择「自定义机器人」</li>
          <li>复制 Webhook 地址</li>
        </ol>

        <h4>如何获取微信 Webhook</h4>
        <ol>
          <li>在企业微信群中右键点击群名称</li>
          <li>选择「群机器人」→「添加机器人」</li>
          <li>选择「新建机器人」，输入名称</li>
          <li>复制 Webhook 地址</li>
        </ol>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { settingApi } from '../api'

const form = reactive({
  feishu_webhook_url: '',
  feishu_secret: '',
  weixin_webhook_url: '',
  pushplus_token: '',
  notification_enabled: true
})

const saving = ref(false)

onMounted(async () => {
  try {
    const response = await settingApi.getNotifications()
    Object.assign(form, response.data)
  } catch (error) {
    console.error('获取设置失败:', error)
  }
})

const handleSave = async () => {
  saving.value = true
  try {
    await settingApi.saveNotifications(form)
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const testFeishu = async () => {
  try {
    const response = await axios.post(form.feishu_webhook_url, {
      msg_type: 'text',
      content: {
        text: '📢 家庭管理系统测试消息\n\n如果您收到这条消息，说明飞书机器人配置成功！'
      }
    })

    if (response.data.code === 0) {
      ElMessage.success('测试消息已发送，请查看飞书群')
    } else {
      ElMessage.error(response.data.msg)
    }
  } catch (error) {
    ElMessage.error('发送失败：' + error.message)
  }
}

const testWeixin = async () => {
  try {
    const response = await axios.post(form.weixin_webhook_url, {
      msgtype: 'text',
      text: {
        content: '📢 家庭管理系统测试消息\n\n如果您收到这条消息，说明微信机器人配置成功！'
      }
    })

    if (response.data.errcode === 0) {
      ElMessage.success('测试消息已发送，请查看微信群')
    } else {
      ElMessage.error(response.data.errmsg)
    }
  } catch (error) {
    ElMessage.error('发送失败：' + error.message)
  }
}

const testPushPlus = async () => {
  try {
    const response = await axios.post('http://www.pushplus.plus/send', {
      token: form.pushplus_token,
      title: '😊 温馨提醒：测试消息',
      content: '<p>📢 这是一条测试消息</p><p>如果您收到这条消息，说明 PushPlus 配置成功！</p>',
      template: 'html'
    })

    if (response.data.code === 200) {
      ElMessage.success('测试消息已发送，请查看个人微信')
    } else {
      ElMessage.error(response.data.msg)
    }
  } catch (error) {
    ElMessage.error('发送失败：' + error.message)
  }
}
</script>

<style scoped>
.settings-page {
  padding: 20px 0;
}

.page-title {
  margin-bottom: 20px;
  font-size: 1.5rem;
}

.setting-card {
  max-width: 700px;
}

.mt-20 {
  margin-top: 20px;
}

.card-header {
  font-weight: 600;
  font-size: 1.1rem;
}

.help-content h4 {
  margin: 15px 0 10px;
  color: #409EFF;
}

.help-content ol {
  padding-left: 20px;
  line-height: 2;
}

.help-content li {
  color: #666;
}
</style>
