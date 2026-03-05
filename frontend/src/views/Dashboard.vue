<template>
  <div class="dashboard">
    <div class="stats-cards">
      <el-card class="stat-card" v-loading="loading">
        <div class="stat-content">
          <div class="stat-icon total">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">BUG总数</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" v-loading="loading">
        <div class="stat-content">
          <div class="stat-icon pending">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.status?.pending || 0 }}</div>
            <div class="stat-label">待处理</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" v-loading="loading">
        <div class="stat-content">
          <div class="stat-icon processing">
            <el-icon><Loading /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.status?.processing || 0 }}</div>
            <div class="stat-label">处理中</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" v-loading="loading">
        <div class="stat-content">
          <div class="stat-icon resolved">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.status?.resolved || 0 }}</div>
            <div class="stat-label">已解决</div>
          </div>
        </div>
      </el-card>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <span>BUG趋势（近30天）</span>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <span>状态分布</span>
          </template>
          <div ref="statusChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>模块分布 TOP10</span>
          </template>
          <div ref="moduleChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>开发人员积压 TOP10</span>
          </template>
          <div ref="developerChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Document, Clock, Loading, CircleCheck } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getBugStatistics } from '../api/bug'

const loading = ref(false)
const stats = ref({})

const trendChartRef = ref(null)
const statusChartRef = ref(null)
const moduleChartRef = ref(null)
const developerChartRef = ref(null)

let trendChart = null
let statusChart = null
let moduleChart = null
let developerChart = null

const fetchStatistics = async () => {
  loading.value = true
  try {
    stats.value = await getBugStatistics()
    await nextTick()
    renderCharts()
  } finally {
    loading.value = false
  }
}

const renderCharts = () => {
  renderTrendChart()
  renderStatusChart()
  renderModuleChart()
  renderDeveloperChart()
}

const renderTrendChart = () => {
  if (!trendChartRef.value) return
  
  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value)
  }
  
  const dates = stats.value.trend?.map(item => item.date) || []
  const created = stats.value.trend?.map(item => item.created) || []
  const resolved = stats.value.trend?.map(item => item.resolved) || []
  
  trendChart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['新增', '解决']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '新增',
        type: 'line',
        data: created,
        itemStyle: { color: '#f56c6c' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0.1)' }
          ])
        }
      },
      {
        name: '解决',
        type: 'line',
        data: resolved,
        itemStyle: { color: '#67c23a' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.1)' }
          ])
        }
      }
    ]
  })
}

const renderStatusChart = () => {
  if (!statusChartRef.value) return
  
  if (!statusChart) {
    statusChart = echarts.init(statusChartRef.value)
  }
  
  const statusMap = {
    pending: '待处理',
    processing: '处理中',
    resolved: '已解决',
    rejected: '已驳回',
    closed: '已关闭'
  }
  
  const colors = {
    pending: '#e6a23c',
    processing: '#409eff',
    resolved: '#67c23a',
    rejected: '#f56c6c',
    closed: '#909399'
  }
  
  const data = Object.entries(stats.value.status || {}).map(([key, value]) => ({
    name: statusMap[key] || key,
    value: value,
    itemStyle: { color: colors[key] }
  }))
  
  statusChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{c}'
        },
        data: data
      }
    ]
  })
}

const renderModuleChart = () => {
  if (!moduleChartRef.value) return
  
  if (!moduleChart) {
    moduleChart = echarts.init(moduleChartRef.value)
  }
  
  const modules = stats.value.module || []
  
  moduleChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'category',
      data: modules.map(item => item.name).reverse(),
      axisLabel: {
        width: 150,
        overflow: 'truncate'
      }
    },
    series: [
      {
        type: 'bar',
        data: modules.map(item => item.count).reverse(),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#409eff' },
            { offset: 1, color: '#67c23a' }
          ])
        }
      }
    ]
  })
}

const renderDeveloperChart = () => {
  if (!developerChartRef.value) return
  
  if (!developerChart) {
    developerChart = echarts.init(developerChartRef.value)
  }
  
  const developers = stats.value.developer || []
  
  developerChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'category',
      data: developers.map(item => item.name).reverse()
    },
    series: [
      {
        type: 'bar',
        data: developers.map(item => item.count).reverse(),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#f56c6c' },
            { offset: 1, color: '#e6a23c' }
          ])
        }
      }
    ]
  })
}

const handleResize = () => {
  trendChart?.resize()
  statusChart?.resize()
  moduleChart?.resize()
  developerChart?.resize()
}

onMounted(() => {
  fetchStatistics()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  statusChart?.dispose()
  moduleChart?.dispose()
  developerChart?.dispose()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stats-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.pending {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.processing {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.resolved {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.chart-card {
  margin-bottom: 0;
}

.chart-container {
  height: 300px;
}
</style>
