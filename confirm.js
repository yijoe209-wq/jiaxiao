const app = getApp()

Page({
  data: {
    pendingId: '',
    taskData: null,
    students: [
      { id: 'bde646c6-6bef-4f8b-88b0-705925f201f8', name: '小明', grade: '三年级' },
      { id: 'a8d6658c-0596-4725-bad0-87b9d77d40e8', name: '小红', grade: '一年级' }
    ],
    selectedStudent: '',
    loading: true,
    confirming: false
  },

  onLoad(options) {
    this.setData({
      pendingId: options.pending_id || ''
    })
    this.loadTaskData()
  },

  async loadTaskData() {
    try {
      const response = await wx.request({
        url: `${app.globalData.apiBase}/api/pending`,
        method: 'GET'
      })

      const tasks = response.data.tasks || []
      const currentTask = tasks.find(t => t.pending_id === this.data.pendingId)

      if (currentTask) {
        this.setData({
          taskData: currentTask.task_data,
          loading: false
        })
      } else {
        wx.showToast({
          title: '任务不存在',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('加载失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  selectStudent(e) {
    const studentId = e.currentTarget.dataset.id
    this.setData({
      selectedStudent: studentId
    })
  },

  async confirm() {
    if (!this.data.selectedStudent) {
      wx.showToast({
        title: '请选择学生',
        icon: 'none'
      })
      return
    }

    this.setData({ confirming: true })

    try {
      const response = await wx.request({
        url: `${app.globalData.apiBase}/api/confirm`,
        method: 'POST',
        data: {
          pending_id: this.data.pendingId,
          student_id: this.data.selectedStudent
        }
      })

      if (response.data.success) {
        wx.showToast({
          title: '✅ 任务创建成功',
          icon: 'success',
          duration: 2000
        })

        setTimeout(() => {
          wx.switchTab({
            url: '/pages/tasks/tasks'
          })
        }, 2000)
      } else {
        wx.showToast({
          title: response.data.error || '确认失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('确认失败:', error)
      wx.showToast({
        title: '确认失败',
        icon: 'none'
      })
    } finally {
      this.setData({ confirming: false })
    }
  }
})
