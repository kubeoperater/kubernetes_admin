<template>
  <div class="app-container">
    <div class="filter-container">
      namespace:
      <el-input v-model="listQuery.pod_nspace" style="width: 200px;" class="filter-item" :disabled="true" />
      podname:
      <el-input v-model="listQuery.pod_name" style="width: 200px;" class="filter-item" :disabled="true" />
      pod_container:
      <el-select
        v-model="listQuery.pod_container"
        :placeholder="this.listQuery.pod_container"
        clearable
        style="width: 130px"
        class="filter-item"
        @change="handlegetpodlog()"
      >
        <el-option v-for="item in params.pod_containlist.split(',')" :key="item" :label="item" :value="item" />
      </el-select>
      <el-button class="filter-item" type="primary" @click="handlegetpodlog()">
        >
      </el-button>

    </div>
    <span style="position: relative; top: 0px;background: #fff;padding: 0 10px; " />
    <div><pre style="white-space: pre-wrap;border:2px solid #bfcbd9">{{ this.container_logs }}</pre></div>
  </div>

</template>
<script>
import { getpodlog } from '@/api/kubernetes/pod'
export default {
  name: 'ContainerLog',
  data() {
    return {
      container_logs: null,
      listQuery: {
        pod_nspace: undefined,
        pod_cluster: process.env.VUE_APP_K8S_TAG,
        pod_name: undefined,
        pod_container: undefined
      },
      params: ''
    }
  },
  created() {
    // 获取传入的参数
    const url_param = this.$route.query
    this.params = url_param
    // this.listQuery.tail_lines = 100
    this.listQuery.pod_nspace = this.params.pod_nsname
    this.listQuery.pod_cluster = this.params.pod_cluster
    this.listQuery.pod_name = this.params.pod_name
    this.listQuery.pod_container = this.params.pod_containlist.split(',')[0]
    this.handlegetpodlog(this.listQuery)
  },
  methods: {
    getpodlog() {
      getpodlog(this.listQuery).then(response => {
        this.container_logs = response.data.data
        setTimeout(() => {
        }, 1.5 * 100)
      })
    },
    handlegetpodlog() {
      this.getpodlog(this.listQuery)
    }
  }
}

</script>
