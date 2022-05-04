const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true
})

module.exports = {
  outputDir: '../server/dist',
   devServer: {
    hot: false,
    liveReload: false
  }
}
