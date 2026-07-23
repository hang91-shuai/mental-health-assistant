Page({
  data: {
    msg: ""
  },
  testApi() {
    wx.request({
      url: "http://10.15.161.200:5000/api/ping",
      success: res => {
        this.setData({ msg: res.data })
      },
      fail: () => {
        this.setData({ msg: "请求失败，后端未启动" })
      }
    })
  }
})