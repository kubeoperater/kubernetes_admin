<template>
  <div class="app-container">
    <div class="filter-container">
      <el-select
        v-model="pod_nspace"
        placeholder="Namespace"
        filterable
        style="width: 130px"
        class="filter-item"
        @change="nschange"
      >
        <el-option v-for="namespace in nslist" :key="namespace" :label="namespace" :value="namespace"/>
      </el-select>
      <el-select
        v-model="pod_name"
        placeholder="pod名称"
        filterable
        style="width: 200px"
        class="filter-item"
        @change="podchange"
      >
        <el-option v-for="podname in podlist" :key="podname" :label="podname" :value="podname" />
      </el-select>
      <el-select
        v-model="pod_container"
        placeholder="container名称"
        filterable
        style="width: 200px"
        class="filter-item"
      >
        <el-option v-for="container in containerlist " :key="container" :label="container" :value="container" />
      </el-select>
      <el-button class="filter-item" type="primary" icon="Connect" @click="connectPodTerminal()">
        连接
      </el-button>
    </div>
    <span style="position: relative; top: 0px;background: #fff;padding: 0 10px; " />
    <div id="terminal" class="console" /></div>

</template>

<script>

import Terminal from './Xterm'
import { getnsset, getcontainerbypod, getpodbyns } from '@/api/kubernetes/pod'

export default {
  name: 'Console',
  data() {
    return {
      term: null,
      terminalSocket: null,
      nsparams: {
        nameonly: true,
        cluster: process.env.VUE_APP_K8S_TAG
      },
      podparams: {
        pod_nspace: undefined,
        cluster: process.env.VUE_APP_K8S_TAG
      },
      containerparams: {
        cluster: process.env.VUE_APP_K8S_TAG,
        pod_nspace: undefined,
        pod_name: undefined
      },
      pod_container: undefined,
      pod_label: undefined,
      pod_nspace: undefined,
      nslist: [],
      podlist: [],
      containerlist: [],
      params: ''
    }
  },
  created() {
  // 获取传入的参数
    const url_param = this.$route.query
    // var param = this.$route.params;
    this.params = url_param
    this.pod_nspace = this.params.pod_nsname
    this.pod_cluster = this.params.pod_cluster
    this.pod_name = this.params.pod_name
    this.containerlist = this.params.pod_containlist.split(',')
    this.pod_container = this.containerlist[0]
    this.getnsset()
    this.nschange()
  },
  mounted() {
    const height = document.documentElement.clientHeight
    const rows = height / 18 - 6
    const terminalContainer = document.getElementById('terminal')
    this.term = new Terminal({ cursorBlink: true, focus: true, rows: parseInt(rows) })
    this.term.open(terminalContainer)
    // open websocket
    const ws_url = `${process.env.VUE_APP_WS_API}` + '/kube/pod/ssh/' + `${this.pod_cluster}` + '/' +
    `${this.pod_nspace}` + '/' +
    `${this.pod_name}` + '/' +
    `${this.pod_container}` + '/' +
    `${this.$store.getters.token}` + '/'
    this.terminalSocket = new WebSocket(ws_url)
    this.terminalSocket.onopen = this.runRealTerminal
    this.terminalSocket.onclose = this.closeRealTerminal
    this.terminalSocket.onerror = this.errorRealTerminal
    this.term.attach(this.terminalSocket)
    this.term.fit()
    this.term.resize(this.term.cols, parseInt(rows))// 终端窗口重新设置大小 并触发term.on("resize"
    this.term._initialized = true

    window.addEventListener('resize', this.windowChange)
  },
  beforeDestroy() {
    this.terminalSocket.close()
    this.term.destroy()
  },
  methods: {
    nschange() {
      this.podparams.pod_nspace = this.pod_nspace
      this.getpodbynshandle(this.podparams)
    },
    podchange() {
      this.containerparams.pod_name = this.pod_name
      this.containerparams.pod_nspace = this.pod_nspace
      this.getcontainerbypodhandle(this.containerparams)
    },
    getnsset() {
      getnsset(this.nsparams).then(response => {
        this.nslist = []
        response.data.data.forEach((vues, index) => {
          this.nslist.push(vues)
        })
        setTimeout(() => {}, 1.5 * 100)
      })
    },
    getpodbynshandle(params) {
      getpodbyns(params).then(response => {
        this.podlist = []
        response.data.list.forEach((vues, index) => {
          this.podlist.push(vues)
        })
        setTimeout(() => {}, 1.5 * 100)
      })
    },
    getcontainerbypodhandle(params) {
      getcontainerbypod(params).then(response => {
        this.containerlist = []
        response.data.list.forEach((vues, index) => {
          this.containerlist.push(vues)
        })
        setTimeout(() => {}, 1.5 * 100)
      })
    },
    runRealTerminal() {
      console.log('webSocket is finished')
    },
    errorRealTerminal() {
      this.terminalSocket.close()
      console.log('error')
    },
    closeRealTerminal() {
      this.terminalSocket.close()
      this.term.writeln('当前连接已关闭，请刷新重连')
      console.log('closed. Thank you for use!')
    },
    windowChange() {
      const height = document.documentElement.clientHeight
      const rows = height / 18 - 6
      this.term.fit()
      this.term.resize(this.term.cols, parseInt(rows))// 终端窗口重新设置大小 并触发term.on("resize"
      this.term.scrollToBottom()
    },
    connectPodTerminal() {
      const height = document.documentElement.clientHeight
      const rows = height / 18 - 6
      const terminalContainer = document.getElementById('terminal')
      if (terminalContainer.isConnected) {
        console.log('is connnect')
        terminalContainer.innerHTML = ''
      }
      this.term = new Terminal({ cursorBlink: true, focus: true, rows: parseInt(rows) })
      this.term.open(terminalContainer)
      // open websocket
      const ws_url = `${process.env.VUE_APP_WS_API}` + '/kube/pod/ssh/' + `${this.pod_cluster}` + '/' +
    `${this.pod_nspace}` + '/' +
    `${this.pod_name}` + '/' +
    `${this.pod_container}` + '/' +
    `${this.$store.getters.token}` + '/'
      this.terminalSocket = new WebSocket(ws_url)
      this.terminalSocket.onopen = this.runRealTerminal
      this.terminalSocket.onclose = this.closeRealTerminal
      this.terminalSocket.onerror = this.errorRealTerminal

      this.term.attach(this.terminalSocket)
      this.term.fit()
      this.term.resize(this.term.cols, parseInt(rows))// 终端窗口重新设置大小 并触发term.on("resize"
      window.addEventListener('resize', this.windowChange)
    }
  }
}

</script>
