/* eslint-disable */
<template>
  <div class="app-container">
    <div class="filter-container">
      <el-select
        v-model="listQuery.pro_nspace"
        placeholder="命名空间"
        clearable
        filterable
        style="width: 130px"
        class="filter-item"
      >
        <el-option v-for="namespace in namespace_dict" :key="namespace" :label="namespace" :value="namespace" />
      </el-select>

      <el-select
        v-model="listQuery.project_name"
        placeholder="项目名称筛选"
        clearable
        filterable
        style="width: 200px"
        class="filter-item"
      >
        <el-option v-for="item in alllist" :key="item.project_name" :label="item.project_name" :value="item.project_name" />
      </el-select>
      <el-select
        v-model="listQuery.deploy_type"
        placeholder="项目部署类型筛选"
        clearable
        filterable
        style="width: 200px"
        class="filter-item"
      >
        <el-option v-for="(item,index) in deploy_typelist" :key="index" :label="item" :value="index" />
      </el-select>
      <el-select
        v-model="listQuery.project_status"
        placeholder="工单状态筛选"
        clearable
        filterable
        style="width: 200px"
        class="filter-item"
      >
        <el-option v-for="(item,index) in statuslist" :key="index" :label="item" :value="index" />
      </el-select>
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-edit" @click="handleCreate">
        新增立项
      </el-button>
    </div>

    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >

      <el-table-column label="项目名称" prop="pro_name" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.project_name }}</span>
        </template>
      </el-table-column>

      <el-table-column label="项目组" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.project_namespace }}</span>
        </template>
      </el-table-column>

      <el-table-column label="项目创建时间">
        <template slot-scope="scope">
          <span>{{ scope.row.project_createtime }}</span>
        </template>
      </el-table-column>

      <el-table-column label="项目端口">
        <template slot-scope="scope">
          <span>{{ scope.row.project_port }}</span>
        </template>
      </el-table-column>

      <el-table-column label="项目初始镜像" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.project_image }}</span>
        </template>
      </el-table-column>

      <el-table-column label="项目部署类型" align="center">
        <template slot-scope="scope">
          <span> {{ formatdeptype(scope.row.deploy_type) }}</span> <!--知识点-->
        </template>
      </el-table-column>

      <el-table-column label="创建人" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.project_user }}</span>
        </template>
      </el-table-column>

      <el-table-column label="部署POD数" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.project_replicas }}</span>
        </template>
      </el-table-column>

      <el-table-column label="项目状态" align="center">
        <template slot-scope="scope">
          <span v-if="scope.row.project_status === 'approved' ">已批准</span> <!--知识点-->
          <span v-else-if="scope.row.project_status === 'create' ">已申请</span>
          <span v-else-if="scope.row.project_status === 'failed' ">立项失败</span>
          <span v-else-if="scope.row.project_status === 'deny' ">驳回</span>
          <span v-else-if="scope.row.project_status === 'success' ">立项成功</span>
          <span v-else-if="scope.row.project_status === 'PEDDING' ">执行中</span>
          <span v-else>scope.row.project_status</span>
        </template>
      </el-table-column>

      <el-table-column v-if="rolesContains(listQuery.pro_nspace + 'manage') || rolesContains('superuser') " label="操作" align="center" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button v-if="statusContainsaproved(scope.row.project_status)" type="primary" size="mini" @click="handleExecute(scope.row)">执行</el-button>
          <el-button v-else-if="statusContainscreate(scope.row.project_status)" type="danger" size="mini" @click="handleChange(scope.row)">批准</el-button>
          <el-button v-else type="info" size="mini" @click="handledisplaylog(scope.row)">执行日志</el-button>
        </template>
      </el-table-column>

    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getprojectlist"
    />
    <el-dialog title="创建应用立项工单" :visible.sync="dialogFormVisible">
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="left"
        label-width="90px"
        style="width: auto; margin-left:20px; margin-right:20px;"
      >
        <el-form-item label="应用组:" prop="project_namespace">
          <el-select v-model="temp.project_namespace" placeholder="应用组" clearable filterable>
            <el-option v-for="item in this.namespace_dict" :key="item" :label="item" :value="item" />
            <el-option key="---" label="如果不在列表，请联系管理员创建" value="none" />
          </el-select>
        </el-form-item>
        <el-form-item label="应用名称:" prop="project_name">
          <el-input v-model="temp.project_name" />
        </el-form-item>
        <el-form-item label="部署类型:" prop="deploy_type">
          <el-select v-model="temp.deploy_type" placeholder="部署类型" clearable filterable>
            <el-option v-for="(item,index) in deploy_typelist" :key="index" :label="item" :value="index" />
          </el-select>
        </el-form-item>

        <el-form-item label="节点数:" prop="project_replicas">
          <el-input v-model="temp.project_replicas" type="number" min="1" max="10" />
        </el-form-item>
        <el-form-item label="初始镜像:" prop="project_image">
          {{ temp.harborurl }}/{{ temp.project_namespace }}/{{ temp.project_name }}: <el-input v-model="temp.project_image" style="width: 180px" type="number" min="20191210151128" />
        </el-form-item>
        <el-form-item label="监听端口:" prop="project_port">
          <el-input v-model="temp.project_port" type="number" min="1025" max="65534" />
        </el-form-item>
      <!--<el-form-item label="CPU限制:" prop="project_cpu">-->
        <!--<el-input v-model="temp.project_cpu"  type="number" min="100" max="16000"/> m (1000 millicpu = 1core)-->
      <!--</el-form-item>-->
        <!--<el-form-item label="内存限制:" prop="project_mem">-->
        <!--<el-input v-model="temp.project_mem"  type="number" min="1" max="10"/> Mi(1024Mi = 1Gi)-->
      <!--</el-form-item>-->
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          Cancel
        </el-button>
        <el-button type="primary" @click="createData()">
          Confirm
        </el-button>
      </div>
    </el-dialog>
    <el-dialog title="更新工单状态" :visible.sync="dialogForm2Visible">
      <el-form
        ref="dataForm2"
        :rules="rules"
        :model="temp"
        label-position="left"
        label-width="auto"
        style="width: auto; margin-left:20px; margin-right:20px;"
      >
        <el-form-item label="项目名称" prop="project_name">
          <el-input v-model="temp.project_name" :disabled="true" />
        </el-form-item>
        <el-form-item label="应用组" prop="project_namespace">
          <el-input v-model="temp.project_namespace" :disabled="true" />
        </el-form-item>
        <el-form-item label="应用端口" prop="project_port">
          <el-input v-model="temp.project_port" type="number" min="1025" max="65534" />
        </el-form-item>
        <el-form-item label="部署类型:" prop="deploy_type">
          <el-select v-model="temp.deploy_type" placeholder="部署类型" clearable filterable>
            <el-option v-for="(item,index) in deploy_typelist" :key="index" :label="item" :value="index" />
          </el-select>
        </el-form-item>
        <el-form-item label="工单状态" prop="project_status">
          <el-select
            v-model="temp.project_status"
            placeholder="search"
            clearable
            filterable
            style="width: 200px"
            class="filter-item"
          >
            <el-option v-for="(value,index) in statuslist" :key="value" :label="value" :value="index" />
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogForm2Visible = false">
          Cancel
        </el-button>
        <el-button type="primary" @click="changeData()">
          Confirm
        </el-button>
      </div>
    </el-dialog>
    <el-dialog title="执行创建过程" :visible.sync="dialogForm3Visible">
      <el-form
        ref="dataForm3"
        :model="temp"
        label-position="left"
        label-width="90px"
        style="width: auto; margin-left:20px; margin-right:20px;"
      >
        <el-form-item label="项目名称" prop="project_name">
          <el-input v-model="temp.project_name" type="textarea" style="-webkit-text-fill-color:black; opacity: 1" :disabled="true" />
        </el-form-item>
        <el-form-item label="应用组" prop="project_namespace">
          <el-input v-model="temp.project_namespace" type="textarea" style="-webkit-text-fill-color:black; opacity: 1" :disabled="true" />
        </el-form-item>
        <el-form-item label="应用端口" prop="project_port">
          <el-input v-model="temp.project_port" type="textarea" style="-webkit-text-fill-color:black; opacity: 1" :disabled="true" />
        </el-form-item>
        <el-form-item label="部署类型:" prop="deploy_type">
          <el-input v-model="temp.deploy_type" type="textarea" style="-webkit-text-fill-color:black; opacity: 1" placeholder="部署类型" :disabled="true" />
        </el-form-item>
        <el-form-item label="应用镜像:" prop="project_image">
          <el-input v-model="temp.project_image" type="textarea" style="-webkit-text-fill-color:black; opacity: 1" placeholder="应用镜像" :disabled="true" />
        </el-form-item>
        <el-form-item label="工单申请人:" prop="project_user">
          <el-input v-model="temp.project_user" type="textarea" style="-webkit-text-fill-color:black; opacity: 1" placeholder="工单申请人" :disabled="true" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="executeCreate()">
          确认执行工单部署
        </el-button>
        <el-button @click="dialogForm3Visible = false">
          取消
        </el-button>
      </div>
    </el-dialog>
    <el-dialog title="执行日志" :visible.sync="dialogForm4Visible" style="width:auto;height: auto">
      <el-steps class="el-steps-sn reset-steps" :active="this.steplenth">
        <el-step key="1" title="01" description="创建共享存储" />
        <el-step key="2" title="02" description="部署应用" />
        <el-step key="3" title="03" description="创建服务网关" />
      </el-steps>
      <el-button @click="nextstep()">下一步</el-button>
      <el-alert style="word-break: break-all">
        <p v-if="this.steplenth === 1" v-html="this.project_volume_message" />
        <p v-if="this.steplenth === 2" v-html="this.project_task_message" />
        <p v-if="this.steplenth === 3" v-html="this.project_svc_message" />
      </el-alert>
    </el-dialog>

  </div>
</template>

<script>
import { projectlist, projectchange, checkharborimg, projectdeploy, projectaskinfo } from '@/api/items/project'
import { getnamespace } from '@/api/kubernetes/namespace'
import waves from '@/directive/waves' // waves directive
import { parseTime } from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import { mapGetters } from 'vuex'

export default {
  inject: ['reload'],
  name: 'ProjectTable',
  components: { Pagination },
  directives: { waves },
  computed: {
    ...mapGetters([
      'name',
      'roles'
    ])
  },
  filters: {},
  data: function() {
    const validatePass = (rule, value, callback) => {
      if (this.temp.project_image.match(new Date().toISOString().replace('-', '').split('T')[0].replace('-', ''))) {
        callback()
      } else {
        callback(new Error('只允许当天打出来的镜像' + new Date().toISOString().replace('-', '').split('T')[0].replace('-', '')) + 'xxxx')
      }
    }
    return {
      tableKey: 0,
      list: null,
      alllist: null,
      namespace_dict: null,
      total: 0,
      listLoading: true,
      dialogFormVisible: false,
      dialogForm2Visible: false,
      dialogForm3Visible: false,
      dialogForm4Visible: false,
      steplenth: 1,
      project_task_message: '',
      project_volume_message: '',
      project_svc_message: '',
      imgstatus: undefined,
      imgmessage: undefined,
      statuslist: { 'create': '已申请', 'approved': '已批准', 'deny': '驳回', 'PEDDING': '执行中', 'failed': '立项失败', 'success': '立项成功' },
      depstatusOptions: ['Running', 'Not Running'],
      deploy_typelist: { 'deployment': '部署集', 'statefulset': '有状态副本集' },
      listQuery: {
        page: 1,
        limit: 10,
        project_cluster: process.env.VUE_APP_K8S_TAG,
        project_name: undefined,
        pro_nspace: undefined,
        deploy_type: undefined
      },
      rules: {
        project_name: [{ required: true, message: '应用名称不能为空', trigger: 'blur' }],
        project_status: [{ required: true, message: '应用状态不能为空', trigger: 'blur' }],
        project_namespace: [{ required: true, message: '应用组不能为空,如果不在列表请联系管理员先创建再进行申请', trigger: 'blur' }],
        project_replicas: [{ required: true, message: '节点数不能为空', trigger: 'blur' }],
        project_image: [{ required: true, message: '初始镜像不能为空', trigger: 'blur' },
          { required: true, trigger: 'blur', validator: validatePass }],
        project_port: [{ required: true, message: '监听端口不能为空', trigger: 'blur' }],
        deploy_type: [{ required: true, message: '应用名称不能为空', trigger: 'blur' }],
        imagepullsecrets: [{ required: true, message: '应用名称不能为空', trigger: 'blur' }]
      },
      temp: {
        'project_cluster': process.env.VUE_APP_K8S_TAG,
        'harborurl': process.env.VUE_APP_HAR_SER,
        'project_name': undefined,
        'project_namespace': undefined,
        'project_replicas': '',
        'project_image': '',
        'project_port': '',
        'deploy_type': '',
        'imagepullsecrets': ''
      }
    }
  },
  created() {
    this.getprojectlist()
  },
  methods: {
    resetTemp() {
      this.temp = {
        'project_cluster': process.env.VUE_APP_K8S_TAG,
        'harborurl': process.env.VUE_APP_HAR_SER,
        'project_name': undefined,
        'project_namespace': undefined,
        'project_replicas': '',
        'project_image': '',
        'project_port': '',
        'deploy_type': '',
        'imagepullsecrets': '',
        'project_status': ''
      }
    },
    formatdeptype(data) {
      return data === 'deployment' ? '部署集' : data === 'statefulset' ? '有状态副本集' : data
    },
    rolesContains(n) {
      return this.roles.indexOf(n) > -1
    },
    statusContainsaproved(status) {
      return status === 'approved'
    },
    statusContainscreate(status) {
      return status === 'create'
    },
    nextstep() {
      if (this.steplenth === 3) {
        this.steplenth = 1
      } else {
        this.steplenth += 1
      }
    },
    getprojectlist() {
      this.listLoading = true
      projectlist(this.listQuery).then(response => {
        this.list = response.data.items
        this.alllist = response.data.all_project
        this.total = response.data.total
        this.namespace_dict = response.data.namespace_dict
        this.listQuery.pro_nspace = response.data.selected_ns
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 100)
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getprojectlist()
    },

    handleChange(row) {
      this.temp = Object.assign({}, row) // copy obj
      this.dialogForm2Visible = true
      this.$nextTick(() => {
        this.$refs['dataForm2'].clearValidate()
      })
    },
    changeData() {
      this.$refs['dataForm2'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          tempData['action'] = 'update'
          const postData = {}
          postData['action'] = tempData['action']
          postData['project_name'] = tempData['project_name']
          postData['project_namespace'] = tempData['project_namespace']
          postData['project_port'] = tempData['project_port']
          postData['project_status'] = tempData['project_status']
          postData['deploy_type'] = tempData['deploy_type']
          projectchange(postData).then(response => {
            this.dialogForm2Visible = false
            this.$notify({
              title: 'Success',
              message: 'Update Successfully',
              type: 'success',
              duration: 2000
            })
            this.reload()
          })
        }
      })
    },
    decodeUnicode(str) {
      str = str.replace(/\\/g, '%')
      return unescape(str)
    },
    handledisplaylog(row) {
      const tempData = Object.assign({}, row)
      this.dialogForm4Visible = true
      const params = {}
      params['project_name'] = tempData['project_name']
      params['project_namespace'] = tempData['project_namespace']
      projectaskinfo(params).then(response => {
        this.project_task_message = response.data.project_message.replace(/\\r\\n/g, '<br>').replace(/\\r/g, ' ').replace(/\\n/g, '<br>').replace(/ /g, '&nbsp;')
        this.project_volume_message = this.decodeUnicode(response.data.project_volume_message.replace(/\\r\\n/g, '<br>').replace(/\\r/g, '').replace(/\\n/g, '<br>'))
        this.project_svc_message = this.decodeUnicode(response.data.project_svc_message.replace(/\\r\\n/g, '<br>').replace(/\\r/g, '').replace(/\\n/g, '<br>').replace(/ /g, '&nbsp;'))
      })
    },
    handleExecute(row) {
      this.temp = Object.assign({}, row) // copy obj
      this.dialogForm3Visible = true
      this.$nextTick(() => {
        this.$refs['dataForm3'].clearValidate()
      })
    },
    executeCreate() {
      this.$refs['dataForm3'].validate((valid) => {
        if (valid) {
          this.temp['cluster_alias'] = process.env.VUE_APP_K8S_TAG
          projectdeploy(this.temp).then(response => {
            this.dialogForm3Visible = false
            this.$notify({
              title: 'Success',
              message: 'Created Successfully' + response.data.task_id,
              type: 'success',
              duration: 2000
            })
            this.reload()
          })
        }
      })
    },
    handleCreate() {
      this.resetTemp()
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.temp['action'] = 'create'
          projectchange(this.temp).then(response => {
            this.dialogFormVisible = false
            this.$notify({
              title: 'Success',
              message: 'Created Successfully',
              type: 'success',
              duration: 2000
            })
            this.reload()
          })
        }
      })
    },
    formatJson(filterVal, jsonData) {
      return jsonData.map(v => filterVal.map(j => {
        if (j === 'timestamp') {
          return parseTime(v[j])
        } else {
          return v[j]
        }
      }))
    }
  }
}
</script>
