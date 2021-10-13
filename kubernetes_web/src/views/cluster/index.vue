<template>
  <div class="app-container">
     <div class="filter-container">
      <el-input v-model="listQuery.k8s_name" placeholder="search" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-edit" @click="handleCreate">
        增加
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
      @sort-change="sortChange"
    >

      <el-table-column label="ID" prop="id" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.id }}</span>
        </template>
      </el-table-column>

      <el-table-column label="集群名称" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.k8s_name }}</span>
        </template>
      </el-table-column>

      <el-table-column label="API地址">
        <template slot-scope="scope">
          <span>{{ scope.row.k8sapi }}</span>
        </template>
      </el-table-column>

      <el-table-column label="Token" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.k8sapi_token.slice(1,20) }}</span>
        </template>
      </el-table-column>

      <el-table-column label="集群别称">
        <template slot-scope="scope">
          <span>{{ scope.row.k8s_ident }}</span>
        </template>
      </el-table-column>

      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button type="primary" size="mini" @click="handleUpdate(scope.row)">
            Edit
          </el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.row)">
            Delete
          </el-button>
        </template>
      </el-table-column>

    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getcluster" />

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="70px" style="width: 400px; margin-left:50px;">
        <el-form-item label="集群名称" prop="k8s_name">
          <el-input v-model="temp.k8s_name" />
        </el-form-item>
        <el-form-item label="API地址" prop="k8sapi">
          <el-input v-model="temp.k8sapi" />
        </el-form-item>
        <el-form-item label="Token" prop="k8sapi_token">
          <el-input v-model="temp.k8sapi_token" />
        </el-form-item>
        <el-form-item label="集群别称" prop="k8s_ident">
          <el-input  v-model="temp.k8s_ident"/>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          Cancel
        </el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">
          Confirm
        </el-button>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="dialogPvVisible" title="Reading statistics">
      <el-table :data="pvData" border fit highlight-current-row style="width: 100%">
        <el-table-column prop="key" label="Channel" />
        <el-table-column prop="pv" label="Pv" />
      </el-table>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="dialogPvVisible = false">Confirm</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getcluster, changecluster } from '@/api/kubernetes/cluster'
import waves from '@/directive/waves' // waves directive
import { parseTime } from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination

export default {
  inject: ['reload'],
  name: 'CluserTable',
  components: { Pagination },
  directives: { waves },
  filters: {},
  data() {
    return {
      tableKey: 0,
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        sort: '+id',
        k8s_name: undefined,
        k8sapi: undefined
      },
      sortOptions: [{ label: 'ID Ascending', key: '+id' }, { label: 'ID Descending', key: '-id' }],
      temp: {
        'k8sapi': '',
        'k8sapi_token': '',
        'k8s_name': '',
        'k8s_ident':''
      },
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: '更新',
        create: '创建',
        delete: '请注意,该操作非常危险，请核对后删除。'
      },
      dialogPvVisible: false,
      pvData: [],
      rules: {
        k8sapi: [{ required: true, message: 'k8sapi is required', trigger: 'change' }],
        k8s_name: [{ required: true, message: 'k8s_name is required', trigger: 'blur' }]
      },
      downloadLoading: false
    }
  },
  created() {
    this.getcluster()
  },
  methods: {
    getcluster() {
      this.listLoading = true
      getcluster(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
        // Just to simulate the time of the request
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 100)
      })
    },
    handleFilter() {
      this.getcluster()
    },
    handleDelete(row) {
      this.temp = Object.assign({}, row) // copy obj
      this.dialogStatus = 'delete'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    sortChange(data) {
      const { prop, order } = data
      if (prop === 'id') {
        this.sortByID(order)
      }
    },
    sortByID(order) {
      if (order === 'ascending') {
        this.listQuery.sort = '+id'
      } else {
        this.listQuery.sort = '-id'
      }
      this.handleFilter()
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        importance: 1,
        remark: '',
        title: ''
      }
    },
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.temp['action'] = 'create'
          changecluster(this.temp).then(response => {
            this.temp['id'] = response.data.id
            this.list.unshift(this.temp)
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
    handleUpdate(row) {
      this.temp = Object.assign({}, row) // copy obj
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          tempData['action'] = this.dialogStatus
          changecluster(tempData).then(response => {
            this.dialogFormVisible = false
            this.$notify({
              title: 'Success',
              message: this.dialogStatus + 'Successfully',
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
    },
    getSortClass: function(key) {
      const sort = this.listQuery.sort
      return sort === `+${key}`
        ? 'ascending'
        : sort === `-${key}`
          ? 'descending'
          : ''
    }
  }
}
</script>
