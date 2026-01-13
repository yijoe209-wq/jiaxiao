const app = getApp()

Page({
  data: {
    currentTab: 'pending',
    pendingTasks: [],
    confirmedTasks: []
  },

  onLoad() {
    this.loadData()
  },

  onShow() {
    this.loadData()
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    this.setData({ currentTab: tab })
  },

  async loadData() {
    await this.loadPendingTasks()
    await this.loadConfirmedTasks()
  },

  async loadPendingTasks() {
    try {
      const response = await wx.request({
        url: `${app.globalData.apiBase}/api/pending`,
        method: 'GET'
      })

      const tasks = response.data.tasks || []
      this.setData({
        pendingTasks: tasks
      })
    } catch (error) {
      console.error('加载待确认任务失败:', error)
    }
  },

  async loadConfirmedTasks() {
    try {
      // 获取所有学生的任务
      const students = ['bde646c6-6bef-4f8b-88b0-705925f201f8', 'a8d6658c-0596-4725-bad0-87b9d77d40e8']
      const allTasks = []

      for (const studentId of students) {
        const response = await wx.request({
          url: `${app.globalData.apiBase}/api/tasks/${studentId}`,
          method: 'GET'
        })

        const tasks = response.data.tasks || []
        allTasks.push(...tasks)
      }

      this.setData({
        confirmedTasks: allTasks
      })
    } catch (error) {
      console.error('加载已确认任务失败:', error)
    }
  },

  goToConfirm(e) {
    const pendingId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/confirm/confirm?pending_id=${pendingId}`
    })
  },

  async completeTask(e) {
    const taskId = e.currentTarget.dataset.id

    try {
      const response = await wx.request({
        url: `${app.globalData.apiBase}/api/tasks/${taskId}/complete`,
        method: 'POST'
      })

      if (response.data.success) {
        wx.showToast({
          title: '✅ 已标记完成',
          icon: 'success'
        })
        this.loadConfirmedTasks()
      } else {
        wx.showToast({
          title: '操作失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('标记完成失败:', error)
      wx.showToast({
        title: '操作失败',
        icon: 'none'
      })
    }
  }
})
