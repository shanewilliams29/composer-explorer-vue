<template>
  <div v-if="$auth.clientToken && $view.showConnecting && $auth.clientToken != 'INVALID'">
    <div class="bg-text">
      <div id="connecting" class="jumbotron overlay">
        <div class="spinner" v-show="true" role="status">
          <b-spinner class="m-5"></b-spinner>
        </div>
        <p class="lead">Lost internet connection...</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.jumbotron{
  margin-bottom: 0px;
  padding-top: 32px;
  padding-bottom: 32px;
}
.overlay {
box-shadow: rgba(0, 0, 0, 0.07) 0px 1px 2px, rgba(0, 0, 0, 0.07) 0px 2px 4px, rgba(0, 0, 0, 0.07) 0px 4px 8px, rgba(0, 0, 0, 0.07) 0px 8px 16px, rgba(0, 0, 0, 0.07) 0px 16px 32px, rgba(0, 0, 0, 0.07) 0px 32px 64px;
  border-radius: 20px;
  background-color: rgb(52, 58, 64, 0.90);
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
  z-index: 1;
}
@supports (-moz-appearance:none) {
  .overlay {
    background-color: rgb(52, 58, 64, 0.90);
  }
}
img{
  margin: 5px;
}
.bg-text {
  color: var(--my-white);
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
  width: 300px;
  padding: 20px;
  text-align: center;
}
p{
  font-weight: 300;
}
.icon-box {
  padding: 0px;
  text-align: center;
}
.icon {
  align-items: center;
  background: rgb(241, 242, 244, 0.1);
  border-radius: 50px;
  display: flex;
  height: 64px;
  justify-content: center;
  margin: 0 auto;
  margin-bottom: 15px;
  width: 64px;
  font-size: 24px;
}
.btn{
  margin-top: 15px;
  border: none;
}
</style>
