<template>
  <div class="app-container">
    <div class="filter-container">
      <el-select
        v-model="listQuery.user_name"
        placeholder="用户筛选"
        clearable
        filterable
        style="width: 200px;"
        class="filter-item"
      >
        <el-option v-for="item in user_list" :key="item" :label="item" :value="item" />
      </el-select>
      <el-select
        v-model="listQuery.cluster_name"
        placeholder="集群筛选"
        clearable
        filterable
        style="width: 200px;"
        class="filter-item"
      >
        <el-option v-for="item in cluster_list" :key="item[1]" :label="item[1]" :value="item[0]" />
      </el-select>
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

      <el-table-column label="用户名称" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.user_name_id }}</span>
        </template>
      </el-table-column>

      <el-table-column label="集群名称">
        <template slot-scope="scope">
          <span>{{ scope.row.k8sapi_id }}</span>
        </template>
      </el-table-column>

      <el-table-column label="命名空间">
        <template slot-scope="scope">
          <span>{{ scope.row.kube_namespace }}</span>
        </template>
      </el-table-column>

      <el-table-column label="权限">
        <template slot-scope="scope">
          <span>{{ scope.row.kube_permis }}</span>
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

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getuserpermission" />

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="70px" style="width: 400px; margin-left:50px;">
        <el-form-item label="用户名称">
          <el-select
            v-model="temp.user_name_id"
            placeholder="search"
            clearable
            filterable
            style="width: 200px"
            class="filter-item"
          >
            <el-option v-for="item in user_list" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="集群别称">
          <el-select
            v-model="temp.k8sapi_id"
            placeholder="search"
            clearable
            filterable
            style="width: 200px"
            class="filter-item"
            @change="getclusternamelist(temp.k8sapi_id)"
          >
            <el-option v-for="option in cluster_list" :key="option[1]" :label="option[1]" :value="option[0]" />
          </el-select>
        </el-form-item>
        <el-form-item label="命名空间">
          <el-select
            v-model="temp.kube_namespace"
            placeholder="search"
            clearable
            filterable
            style="width: 200px"
            class="filter-item"
          >
            <el-option v-for="item in namspace_list" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="权限">
          <el-select
            v-model="temp.kube_permis"
            placeholder="search"
            clearable
            filterable
            style="width: 200px"
            class="filter-item"
          >
            <el-option v-for="item in permis_list" :key="item" :label="item" :value="item" />
          </el-select>
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
import { updateuserpermission, getuserpermission } from '@/api/users/user'
import { getnamespace } from '@/api/kubernetes/namespace'
import waves from '@/directive/waves' // waves directive
import { parseTime } from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination

export default {
  inject: ['reload'],
  name: 'PermisTable',
  components: { Pagination },
  directives: { waves },
  filters: {},
  data() {
    return {
      tableKey: 0,
      list: null,
      total: 0,
      listLoading: true,
      namspace_list: [],
      cluster_list: [],
      user_list: [],
      permis_list: ['read', 'manage'],
      listQuery: {
        page: 1,
        limit: 20,
        user_name: undefined,
        cluster_name: undefined
      },
      queryparmas: {
        cluster: undefined,
        nameonly: true
      },
      sortOptions: [{ label: 'ID Ascending', key: '+id' }, { label: 'ID Descending', key: '-id' }],
      temp: {
        'user_name_id': '',
        'kube_namespace': '',
        'k8sapi': '',
        'kube_permis': ''
      },
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: '更新',
        create: '创建',
        delete: '删除'
      },
      dialogPvVisible: false,
      pvData: [],
      rules: {
        username: [{ required: true, message: 'user_name is required', trigger: 'change' }]
      },
      downloadLoading: false
    }
  },
  created() {
    this.getuserpermission()
  },
  methods: {
    getuserpermission() {
      this.listLoading = true
      getuserpermission(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.cluster_list = response.data.cluster_list
        console.log(this.cluster_list)
        this.user_list = response.data.userlist
        // Just to simulate the time of the request
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 100)
      })
    },
    handleFilter() {
      this.getuserpermission()
    },
    getclusternamelist(clusterid) {
      this.queryparmas.cluster = clusterid
      getnamespace(this.queryparmas).then(response => {
        this.namspace_list = response.data.data
        // Just to simulate the time of the request
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 100)
      })
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
          updateuserpermission(this.temp).then(response => {
            this.dialogFormVisible = false
            this.$notify({
              title: 'Success',
              message: response.data.message,
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
          updateuserpermission(tempData).then(response => {
            this.dialogFormVisible = false
            this.$notify({
              title: 'Success',
              message: response.data.message,
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
