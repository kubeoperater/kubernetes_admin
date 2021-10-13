/* eslint-disable */
<template>
  <div class="app-container">
    <div class="filter-container">
      <el-select
        v-model="listQuery.dep_nspace"
        placeholder="命名空间"
        clearable
        filterable
        style="width: 130px"
        class="filter-item"
        @change="Nsspacechanges()"
      >
        <el-option v-for="(item,index) in query_dict" :key="index" :label="index" :value="index" />
      </el-select>

      <el-select
        v-model="listQuery.dep_label"
        placeholder="dep名称筛选"
        clearable
        filterable
        style="width: 200px"
        class="filter-item"
      >
        <el-option v-for="item in labels_list" :key="item" :label="item" :value="item" />
      </el-select>
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
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

      <el-table-column label="deploy名称" prop="dep_name" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.dep_name }}</span>
        </template>
      </el-table-column>

      <el-table-column label="deploy空间" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.dep_namespace }}</span>
        </template>
      </el-table-column>

      <el-table-column label="创建时间">
        <template slot-scope="scope">
          <span>{{ scope.row.dep_creatime }}</span>
        </template>
      </el-table-column>

      <el-table-column label="deploy标签" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.dep_labels }}</span>
        </template>
      </el-table-column>

      <el-table-column label="deploy后端服务标签" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.dep_selectlabels }}</span>
        </template>
      </el-table-column>

      <el-table-column label="deploy副本数" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.dep_replicas }}</span>
        </template>
      </el-table-column>

      <el-table-column label="deploy可用副本数" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.dep_available_replicas }}</span>
        </template>
      </el-table-column>

      <el-table-column label="镜像地址" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.img_list }}</span>
        </template>
      </el-table-column>

      <el-table-column label="容器列表" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.container_list }}</span>
        </template>
      </el-table-column>

      <el-table-column v-if="rolesContains(listQuery.dep_nspace + 'manage') || rolesContains('superuser') " label="操作" align="center" class-name="small-padding fixed-width">
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

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getdep"
    />
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="left"
        label-width="auto"
        style="width: auto; margin-left:20px; margin-right:20px;"
      >
        <el-form-item label="部署名" prop="dep_name">
          <el-input v-model="temp.dep_name" />
        </el-form-item>
        <el-form-item v-if="dialogStatus !== 'delete'" label="副本数" prop="dep_replicas">
          <el-input v-model="temp.dep_replicas" />
        </el-form-item>
        <el-form-item  label="节点选择:" prop="label_list">
          <el-select v-model="temp.dep_nodename" placeholder="nodeSelect选项" clearable filterable>
            <el-option v-for="item in temp.label_list.split(',')" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item  label="容器名:" prop="dep_containame">
          <el-select v-model="temp.dep_containame" placeholder="容器名" clearable filterable>
            <el-option v-for="item in temp.container_list.split(',')" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="镜像:" prop="contain_image">
          <el-input
            v-model="temp.contain_image"
            type="text"
            style="-webkit-text-fill-color:black; opacity: 1"
          />
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
  </div>
</template>

<script>
import { getdep, changedep } from '@/api/kubernetes/dep'
import waves from '@/directive/waves' // waves directive
import { parseTime } from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import { mapGetters } from 'vuex'

export default {
  inject: ['reload'],
  name: 'DepTable',
  components: { Pagination },
  directives: { waves },
  computed: {
    ...mapGetters([
      'name',
      'roles'
    ])
  },
  filters: {},
  data() {
    return {
      tableKey: 0,
      list: null,
      query_dict: null,
      labels_list: null,
      total: 0,
      listLoading: true,
      dialogFormVisible: false,
      depstatusOptions: ['Running', 'Not Running'],
      listQuery: {
        page: 1,
        limit: 10,
        sort: '+id',
        dep_label: undefined,
        dep_nspace: undefined,
        dep_cluster: process.env.VUE_APP_K8S_TAG
      },
      dialogStatus: '',
      textMap: {
        update: '更新',
        create: '创建',
        delete: '删除,请注意该操作会删除部署的docker程序，请谨慎操作！！！'
      },
      rules: {
        dep_name: [{ required: true, message: 'dep_name is required', trigger: 'change' }],
        dep_replicas: [{ required: true, message: 'dep_replicas is required', trigger: 'blur' }]
      },
      sortOptions: [{ label: 'ID Ascending', key: '+id' }, { label: 'ID Descending', key: '-id' }],
      temp: {
        'dep_name': '',
        'dep_namespace': '',
        'dep_creatime': '',
        'dep_labels': '',
        'dep_selectlabels': '',
        'dep_replicas': '',
        'dep_available_replicas': '',
        'img_list': '',
        'container_list': '',
        'dep_nodename': '',
        'dep_containame': '',
        'label_list': '',
        'contain_image': ''
      }
    }
  },
  created() {
    this.getdep()
  },
  methods: {
    rolesContains(n) {
      return this.roles.indexOf(n) > -1
    },
    Nsspacechanges() {
      this.labels_list = []
      this.listQuery.dep_label = undefined
      this.query_dict[this.listQuery.dep_nspace].forEach((vues, index) => {
        this.labels_list.push(vues)
      }
      )
    },
    getdep() {
      this.listLoading = true
      getdep(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.query_dict = response.data.query_dict
        this.listQuery.dep_nspace = response.data.selected_ns
        this.labels_list = []
        this.query_dict[this.listQuery.dep_nspace].forEach((vues, index) => {
          this.labels_list.push(vues)
        })
        // Just to simulate the time of the request
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 100)
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getdep()
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
          tempData['cluster'] = process.env.VUE_APP_K8S_TAG
          changedep(tempData).then(response => {
            this.dialogFormVisible = false
            this.listQuery.dep_nspace = tempData['dep_nspace']
            this.$notify({
              title: 'Success',
              message: response.data.message,
              type: 'success',
              duration: 2000
            })
          })
        }
      })
      this.reload()
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
