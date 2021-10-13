/* eslint-disable */
<template>
  <div class="app-container">
    <div class="filter-container">
      <el-select
        v-model="listQuery.pod_nspace"
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
        v-model="listQuery.pod_label"
        placeholder="pod名称筛选"
        clearable
        filterable
        style="width: 200px"
        class="filter-item"
      >
        <el-option v-for="item in labels_list" :key="item" :label="item" :value="item" />
      </el-select>
      <el-select v-model="listQuery.pod_stats" placeholder="pod状态筛选" clearable style="width: 130px" class="filter-item">
        <el-option v-for="item in podstatusOptions" :key="item" :label="item" :value="item" />
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

      <el-table-column label="容器名称" prop="id" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.pod_name }}</span>
        </template>
      </el-table-column>

      <el-table-column label="容器ip" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.pod_ip }}</span>
        </template>
      </el-table-column>

      <el-table-column label="容器状态" align="center">
        <template slot-scope="scope">
          <span :style="{'color':( scope.row.pod_status === 'Running' ? '' : 'red')}">{{ scope.row.pod_status }}</span>
        </template>
      </el-table-column>

      <el-table-column label="创建时间">
        <template slot-scope="scope">
          <span>{{ scope.row.pod_creatime }}</span>
        </template>
      </el-table-column>

      <el-table-column label="镜像地址" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.img_rel }}</span>
        </template>
      </el-table-column>

      <el-table-column label="container列表" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.container_name_list }}</span>
        </template>
      </el-table-column>

      <el-table-column label="宿主机IP" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.host_ip }}</span>
        </template>
      </el-table-column>

      <el-table-column label="容器命名空间" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.pod_namespace }}</span>
        </template>
      </el-table-column>

      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button type="primary" size="mini" @click="handlessh(scope.row)">
            SSH
          </el-button>
          <el-button type="danger" size="mini" @click="handlelog(scope.row)">
            LOG
          </el-button>
        </template>
      </el-table-column>

    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getpod"
    />
    <el-dialog :visible.sync="dialogsshVisible" title="Reading statistics" />
  </div>
</template>

<script>
import { getpod } from '@/api/kubernetes/pod'
import waves from '@/directive/waves' // waves directive
import { parseTime } from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination

export default {
  name: 'PodTable',
  components: { Pagination },
  directives: { waves },
  filters: {
  },
  data() {
    return {
      tableKey: 0,
      list: null,
      query_dict: null,
      labels_list: null,
      total: 0,
      listLoading: true,
      dialogsshVisible: false,
      dialoglogVisible: false,
      podstatusOptions: ['Running', 'Not Running'],
      listQuery: {
        page: 1,
        limit: 10,
        sort: '+id',
        pod_label: undefined,
        pod_nspace: undefined,
        pod_appname: undefined,
        pod_cluster: process.env.VUE_APP_K8S_TAG,
        pod_stats: undefined
      },
      sortOptions: [{ label: 'ID Ascending', key: '+id' }, { label: 'ID Descending', key: '-id' }],
      temp: {
        'pod_name': '',
        'pod_ip': '',
        'pod_status': '',
        'pod_creatime': '',
        'img_rel': '',
        'container_name_list': '',
        'host_ip': '',
        'pod_namespace': ''
      }
    }
  },
  created() {
    this.getpod()
  },
  methods: {
    Nsspacechanges() {
      this.labels_list = []
      this.listQuery.pod_label = undefined
      this.query_dict[this.listQuery.pod_nspace].forEach((vues, index) => {
        this.labels_list.push(vues)
      }
      )
    },
    getpod() {
      this.listLoading = true
      getpod(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.query_dict = response.data.query_dict
        this.listQuery.pod_nspace = response.data.selected_ns
        this.labels_list = []
        this.query_dict[this.listQuery.pod_nspace].forEach((vues, index) => {
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
      this.getpod()
    },
    handlessh(item) {
      const routeData = this.$router.resolve(
        {
          path: 'webterminal',
          query: {
            pod_cluster: this.listQuery.pod_cluster,
            pod_nsname: item.pod_namespace,
            pod_appname: item.pod_appname,
            pod_name: item.pod_name,
            pod_containlist: item.container_name_list
          }
        }
      )
      window.open(routeData.href, '_blank')
    },
    handlelog(item) {
      const routeData = this.$router.resolve(
        {
          path: 'containerlog',
          query: {
            pod_cluster: this.listQuery.pod_cluster,
            pod_nsname: item.pod_namespace,
            pod_name: item.pod_name,
            pod_containlist: item.container_name_list
          }
        }
      )
      window.open(routeData.href, '_blank')
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
