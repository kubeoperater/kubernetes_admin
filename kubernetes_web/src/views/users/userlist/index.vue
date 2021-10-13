<template>
  <div class="app-container">
    <div class="filter-container">
      <el-select v-model="listQuery.user_name" placeholder="search"  clearable filterable style="width: 200px;"
                 class="filter-item">
        <el-option v-for="item in all_userlist" :key="item.username" :label="item.username" :value="item.username"/>
      </el-select>
      <el-select v-model="listQuery.userlevel" placeholder="用户类别筛选" clearable style="width: 130px" class="filter-item">
        <el-option v-for="item in userlevel_list " :key="item" :label="item" :value="item"/>
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
          <span>{{ scope.row.username }}</span>
        </template>
      </el-table-column>

      <el-table-column label="性别">
        <template slot-scope="scope">
          <span>{{ scope.row.gender }}</span>
        </template>
      </el-table-column>

      <el-table-column label="邮箱地址">
        <template slot-scope="scope">
          <span>{{ scope.row.email }}</span>
        </template>
      </el-table-column>

      <el-table-column label="超级用户">
        <template slot-scope="scope">
          <span>{{ scope.row.is_superuser}}</span>
        </template>
      </el-table-column>

      <el-table-column label="创建时间">
        <template slot-scope="scope">
          <span>{{ scope.row.date_joined }}</span>
        </template>
      </el-table-column>

      <el-table-column label="最后登录">
        <template slot-scope="scope">
          <span>{{ scope.row.last_login }}</span>
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

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getusersinfo" />

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="70px" style="width: 400px; margin-left:50px;">
        <el-form-item label="用户名称" prop="user_name">
          <el-input v-model="temp.username" />
        </el-form-item>
        <el-form-item label="email" prop="user_email">
          <el-input v-model="temp.email" />
        </el-form-item>
        <el-form-item label="超级用户" prop="is_superuser">
           <el-select v-model="temp.is_superuser" placeholder="search" clearable filterable style="width: 200px"
               class="filter-item">
            <el-option v-for="item in labels_list" :key="item" :label="item" :value="item"/>
          </el-select>
        </el-form-item>
        <el-form-item label="性别" prop="gender">
           <el-select v-model="temp.gender" placeholder="search" clearable filterable style="width: 200px"
               class="filter-item">
            <el-option v-for="item in gender_list" :key="item" :label="item" :value="item"/>
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
import { getuserlist, updateuserinfo } from '@/api/users/user'
import waves from '@/directive/waves' // waves directive
import { parseTime } from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination

export default {
  inject:['reload'],
  name: 'UserTable',
  components: { Pagination },
  directives: { waves },
  filters: {},
  data() {
    return {
      tableKey: 0,
      list: null,
      all_userlist: null,
      total: 0,
      listLoading: true,
      labels_list:['True','False'],
      gender_list:['male','female'],
      userlevel_list: ['superuser', 'user'],
      listQuery: {
        page: 1,
        limit: 20,
        sort: '+id',
        user_name: undefined,
        user_email: undefined,
        userlevel: undefined
      },
      sortOptions: [{ label: 'ID Ascending', key: '+id' }, { label: 'ID Descending', key: '-id' }],
      temp: {
        'username': '',
        'user_email': '',
        'is_superuser':''
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
    this.getusersinfo()
  },
  methods: {
    getusersinfo() {
      this.listLoading = true
      getuserlist(this.listQuery).then(response => {
        this.list = response.data.items
        this.all_userlist = response.data.all_userlist
        this.total = response.data.total
        // Just to simulate the time of the request
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 100)
      })
    },
    handleFilter() {
      this.getusersinfo()
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
          updateuserinfo(this.temp).then(response => {
            console.log(response)
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
      this.temp.is_superuser = this.temp.is_superuser.toString()
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
          const postData =  {}
          postData['action'] = this.dialogStatus
          postData['is_superuser'] = tempData['is_superuser']
          postData['username'] = tempData['username']
          postData['email'] = tempData['email']
          postData['gender'] = tempData['gender']
          postData['id'] = tempData['id']
          updateuserinfo(postData).then(response => {
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
