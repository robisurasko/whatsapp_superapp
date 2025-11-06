<template>
  <div class="whatsapp-superapp">
    <header class="topbar">
      <div class="left-title">Whatsapp Superapp</div>
      <div class="actions">
        <select v-model="agentStatus" @change="updateStatus">
          <option>Online</option>
          <option>Busy</option>
          <option>Offline</option>
        </select>
        <button @click="openSettings">Settings</button>
        <button @click="openTemplates">Templates</button>
      </div>
    </header>

    <div class="app-grid">
      <aside class="left">
        <input v-model="search" placeholder="Search contacts..." />
        <ul class="conversations">
          <li v-for="c in conversations" :key="c.name" :class="{active: c.name===activeConversation}" @click="selectConversation(c)">
            <div class="name">{{ c.contact }}</div>
            <div class="preview">{{ c.last_message }}</div>
          </li>
        </ul>
      </aside>

      <main class="center">
        <div v-if="!activeConversation" class="empty">Pilih conversation di sebelah kiri</div>
        <div v-else class="message-panel">
          <div class="message-list">
            <div v-for="m in messages" :key="m.name" :class="['msg', m.direction.toLowerCase()]">
              <div class="content">{{ m.message }}</div>
              <div class="meta">{{ m.sent_at }}</div>
            </div>
          </div>
          <div class="composer">
            <textarea v-model="composerText" placeholder="Type a message"></textarea>
            <div class="composer-actions">
              <button @click="sendText">Send</button>
              <button @click="sendTemplatePrompt">Send Template</button>
            </div>
          </div>
        </div>
      </main>

      <aside class="right">
        <div v-if="contactDetail">
          <h3>{{ contactDetail.full_name }}</h3>
          <div>Phone: {{ contactDetail.phone }}</div>
          <div>Tags: <input v-model="contactDetail.tags" @blur="saveContact" /></div>
        </div>
        <div v-else>Contact details will appear here</div>
      </aside>
    </div>

    <!-- Modal placeholders -->
    <div v-if="showSettings" class="modal">Settings (placeholder)</div>
    <div v-if="showTemplates" class="modal">Templates (placeholder)</div>
  </div>
</template>

<script>
export default {
  name: 'WhatsAppSuperapp',
  data() {
    return {
      conversations: [],
      messages: [],
      activeConversation: null,
      contactDetail: null,
      composerText: '',
      agentStatus: 'Offline',
      search: '',
      showSettings: false,
      showTemplates: false
    }
  },
  mounted() {
    this.fetchConversations()
  },
  methods: {
    async fetchConversations(){
      const res = await fetch('/api/method/whatsapp_superapp.api.list_conversations')
      const data = await res.json()
      this.conversations = data.message || data
    },
    async selectConversation(c){
      this.activeConversation = c.name
      const res = await fetch('/api/method/whatsapp_superapp.api.list_messages?conversation=' + encodeURIComponent(c.name))
      const data = await res.json()
      this.messages = data.message || data
      // fetch contact
      const contactName = c.contact
      if(contactName){
        const res2 = await fetch('/api/resource/CSIS Contact/' + encodeURIComponent(contactName))
        const d2 = await res2.json()
        this.contactDetail = d2.data
      }
    },
    async sendText(){
      if(!this.activeConversation) return alert('Select conversation first')
      // create outgoing message record (local simulation)
      const payload = {
        doc: {
          doctype: 'CSIS Whatsapp Message',
          conversation: this.activeConversation,
          direction: 'Outgoing',
          content_type: 'text',
          message: this.composerText
        }
      }
      await fetch('/api/resource/CSIS Whatsapp Message', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(payload)
      })
      this.composerText = ''
      this.selectConversation({name:this.activeConversation, contact: this.contactDetail && this.contactDetail.name})
    },
    sendTemplatePrompt(){
      const t = prompt('Template name to send:')
      if(!t) return
      fetch('/api/method/whatsapp_superapp.api.send_template?contact=' + encodeURIComponent(this.contactDetail.name) + '&template_name=' + encodeURIComponent(t))
        .then(()=> this.selectConversation({name:this.activeConversation, contact: this.contactDetail && this.contactDetail.name}))
    },
    updateStatus(){
      // in a real app, call API to set agent status
      console.log('status', this.agentStatus)
    },
    openSettings(){ this.showSettings = true },
    openTemplates(){ this.showTemplates = true },
    saveContact(){
      // save contact via REST
      fetch('/api/resource/CSIS Contact/' + encodeURIComponent(this.contactDetail.name), {
        method: 'PUT',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({data: this.contactDetail})
      })
    }
  }
}
</script>

<style scoped>
.topbar{display:flex;justify-content:space-between;padding:12px;background:#f3f3f3}
.app-grid{display:grid;grid-template-columns:320px 1fr 320px;gap:12px;padding:12px}
.left,.center,.right{background:white;border-radius:8px;padding:12px;min-height:400px}
.conversations{list-style:none;padding:0;margin:0}
.conversations li{padding:8px;border-bottom:1px solid #eee;cursor:pointer}
.conversations li.active{background:#eef}
.msg{padding:8px;margin:6px 0;border-radius:6px;max-width:70%}
.msg.incoming{background:#f1f1f1;align-self:flex-start}
.msg.outgoing{background:#d1ffd1;align-self:flex-end}
.message-list{display:flex;flex-direction:column}
.composer{margin-top:12px}
.modal{position:fixed;left:20%;top:20%;background:white;padding:20px;border:1px solid #ccc}
</style>
