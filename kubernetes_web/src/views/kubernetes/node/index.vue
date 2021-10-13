/* eslint-disable */
<template>
  <div class="app-container">
    <div class="filter-container">
      <el-select
        v-model="listQuery.node_label"
        placeholder="组标签筛选"
        clearable
        filterable
        style="width: 200px"
        class="filter-item">
        <el-option v-for="item in labels_list" :key="item" :label="item" :value="item" /></el-select>
      <el-select
        v-model="listQuery.nodename"
        placeholder="node名称筛选"
        clearable
        filterable
        style="width: 200px"
        class="filter-item">
        <el-option v-for="item in node_list" :key="item" :label="item" :value="item" /></el-select>
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        筛选
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

      <el-table-column label="节点名称" prop="node_name" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.node_name }}</span>
        </template>
      </el-table-column>

      <el-table-column label="内核版本">
        <template slot-scope="scope">
          <span>{{ scope.row.node_info.kernel_version }}</span>
        </template>
      </el-table-column>

      <el-table-column label="系统版本">
        <template slot-scope="scope">
          <span>{{ scope.row.node_info.os_image }}</span>
        </template>
      </el-table-column>

      <el-table-column label="kubelet版本" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.node_info.kubelet_version }}</span>
        </template>
      </el-table-column>

      <el-table-column label="容器总数量" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.pod_num }}</span>
        </template>
      </el-table-column>

      <el-table-column label="容器正常数量" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.run_count }}</span>
        </template>
      </el-table-column>

      <el-table-column label="容器IP网段" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.pod_cidr }}</span>
        </template>
      </el-table-column>

      <el-table-column label="节点CPU使用" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.nodeusage_cpu }}</span>
        </template>
      </el-table-column>

      <el-table-column label="节点内存使用(U/T)" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.nodeusage_mem }}</span>
        </template>
      </el-table-column>

      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button type="primary" size="mini" @click="opendialog(scope.row)">
            详细信息
          </el-button>
        </template>
      </el-table-column>

    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getnode"
    />
    <el-dialog title="主机详细信息" :visible.sync="dialogFormVisible">
      <el-alert style="word-break: break-all">
        <pre>{{ JSON.stringify(temp, null, 4) }}</pre>
      </el-alert>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          关闭
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getnode } from '@/api/kubernetes/nodes'
import waves from '@/directive/waves' // waves directive
import { parseTime } from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import { mapGetters } from 'vuex'

export default {
  inject: ['reload'],
  name: 'NodeTable',
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
      node_list: null,
      query_dict: null,
      labels_list: null,
      total: 0,
      listLoading: true,
      dialogFormVisible: false,
      nodestatusOptions: ['Running', 'Not Running'],
      listQuery: {
        page: 1,
        limit: 10,
        sort: '+id',
        nodename: undefined,
        node_label: undefined,
        node_nspace: undefined,
        node_cluster: process.env.VUE_APP_K8S_TAG
      },
      dialogStatus: '',
      rules: {
        node_name: [{ required: true, message: 'node_name is required', trigger: 'change' }]
      },
      sortOptions: [{ label: 'ID Ascending', key: '+id' }, { label: 'ID Descending', key: '-id' }],
      temp: {
        'node_name': '',
        'node_namespace': '',
        'node_creatime': '',
        'node_labels': '',
        'node_selectlabels': '',
        'node_replicas': '',
        'node_available_replicas': '',
        'node_imglist': ''
      }
    }
  },
  created() {
    this.getnode()
  },
  methods: {
    rolesContains(n) {
      return this.roles.indexOf(n) > -1
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getnode()
    },
    getnode() {
      this.listLoading = true
      getnode(this.listQuery).then(response => {
        this.list = response.data.item
        this.total = response.data.total
        this.node_list = response.data.node_list
        this.labels_list = response.data.labels_list
        // this.query_dict = response.data.query_dict
        // this.listQuery.node_nspace = response.data.selected_ns
        // this.query_dict[this.listQuery.node_nspace].forEach((vues, index) => {
        //   this.labels_list.push(vues)
        // })
        // Just to simulate the time of the request
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 100)
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
    opendialog(row) {
      this.dialogFormVisible = true
      this.temp = Object.assign({}, row) // copy obj
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
