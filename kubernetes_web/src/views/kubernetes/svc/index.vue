/* eslint-disable */
<template>
  <div class="app-container">
  <div class="filter-container">
    <el-select v-model="listQuery.svc_nspace" placeholder="命名空间" clearable filterable style="width: 130px"
               class="filter-item" @change="Nsspacechanges()">
      <el-option v-for="(item,index) in query_dict" :key="index" :label="index" :value="index"/>
    </el-select>

    <el-select v-model="listQuery.svc_label" placeholder="search" clearable filterable style="width: 200px"
               class="filter-item">
      <el-option v-for="item in labels_list" :key="item" :label="item" :value="item"/>
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

    <el-table-column label="服务名称" prop="id" align="center" width="auto">
      <template slot-scope="scope">
        <span>{{ scope.row.svc_name }}</span>
      </template>
    </el-table-column>

    <el-table-column label="服务ip" align="center"  width="auto">
      <template slot-scope="scope">
        <span>{{ scope.row.svc_ip }}</span>
      </template>
    </el-table-column>


    <el-table-column label="创建时间"  width="auto">
      <template slot-scope="scope">
        <span>{{ scope.row.create_time }}</span>
      </template>
    </el-table-column>

    <el-table-column label="后端服务标签" align="center"  width="auto">
      <template slot-scope="scope">
        <span>{{ scope.row.labels }}</span>
      </template>
    </el-table-column>


    <el-table-column label="服务类型" align="center"  width="auto">
      <template slot-scope="scope">
        <span>{{ scope.row.svc_type }}</span>
      </template>
    </el-table-column>

    <el-table-column label="服务端口" align="center"  width="auto">
      <template slot-scope="scope">
        <span>{{ scope.row.portlist }}</span>
      </template>
    </el-table-column>

    <el-table-column label="所在命名空间" align="center"  width="auto">
      <template slot-scope="scope">
        <span>{{ scope.row.svc_namespace }}</span>
      </template>
    </el-table-column>

    <!--<el-table-column label="操作" align="center" class-name="small-padding ">-->
      <!--<template slot-scope="scope">-->
        <!--<el-button type="primary" size="mini" @click="handleconn(scope.row)">-->
          <!--编辑-->
        <!--</el-button>-->
        <!--<el-button type="danger" size="mini" @click="handleconn(scope.row)">-->
          <!--删除-->
        <!--</el-button>-->
      <!--</template>-->
    <!--</el-table-column>-->

  </el-table>

  <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit"
              @pagination="getsvc"/>

  </div>
</template>

<script>
import {getsvc} from '@/api/kubernetes/svc'
import waves from '@/directive/waves' // waves directive
import {parseTime} from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination

export default {
name: 'PodTable',
components: {Pagination},
directives: {waves},
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
      listQuery: {
        page: 1,
        limit: 10,
        sort: '+id',
        svc_label: undefined,
        svc_nspace: undefined,
        svc_cluster: process.env.VUE_APP_K8S_TAG,
      },
      sortOptions: [{label: 'ID Ascending', key: '+id'}, {label: 'ID Descending', key: '-id'}],
      temp: {
        'svc_name': '',
        'svc_ip': '',
        'svc_namespace': '',
        'create_time': '',
        'labels': '',
        'svc_type': ''
      }
    }
  },
created() {
  this.getsvc()
},
methods: {
  Nsspacechanges() {
    this.labels_list = [];
    this.listQuery.svc_label = undefined
    this.query_dict[this.listQuery.svc_nspace].forEach((vues, index) => {
        this.labels_list.push(vues)
      }
    )
  },
  getsvc() {
    this.listLoading = true
    getsvc(this.listQuery).then(response => {
      this.list = response.data.items
      this.total = response.data.total
      this.query_dict = response.data.query_dict
      this.listQuery.svc_nspace = response.data.selected_ns
      this.labels_list = [];
      this.query_dict[this.listQuery.svc_nspace].forEach((vues, index) => {
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
    this.getsvc()
  },
  handleconn() {
    this.getsvc()
  },
  sortChange(data) {
    const {prop, order} = data
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
  getSortClass: function (key) {
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
