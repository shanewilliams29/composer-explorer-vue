const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true
})

module.exports = {
  outputDir: '../server/dist',
  devServer: {
    host: '127.0.0.1',
    port: 8080,
  }
}
