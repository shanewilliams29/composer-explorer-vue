<template>
  <div v-if="$view.banner && !$auth.clientToken && $view.mobile" class="container-fluid">
    <div class="bg-text">
      <div id="welcome" class="jumbotron overlay">
        <div class="container content disable-scrollbars">
          <h1>
            <img :src="logoURL" class="d-inline-block align-top logo" alt="Composer Explorer" height="60px" />
          </h1>
          <h4>Welcome to your Classical Music Portal.</h4>
          <p class="lead">
            Explore composers from the Medieval to the present. <br />
            Listen to works on <b>Spotify, made navigable for Classical music.</b>
          </p>

          <div class="container">
            <div class="row">
              <div class="col-lg-4 col-md-4 d-flex align-items-stretch">
                <div class="icon-box">
                  <div class="icon"><b-icon icon="search" aria-hidden="true"></b-icon></div>
                  <h4>Explore</h4>
                  <p>Discover new composers and new works by the composers you love. For the newcomer and the completionist.</p>
                </div>
              </div>

              <div class="col-lg-4 col-md-4 d-flex align-items-stretch">
                <div class="icon-box">
                  <div class="icon"><b-icon icon="music-note-beamed" aria-hidden="true"></b-icon></div>
                  <h4>Play Music</h4>
                  <p>Browse albums and connect with your Spotify account to play music and create radios.</p>
                </div>
              </div>

              <div class="col-lg-4 col-md-4 d-flex align-items-stretch">
                <div class="icon-box">
                  <div class="icon"><b-icon icon="heart" aria-hidden="true"></b-icon></div>
                  <h4>Engage</h4>
                  <p>Discover new performers, and add works and performances to your favorites.</p>
                </div>
              </div>
            </div>
          </div>
          </div>
          <div class="buttons-container">
          <a :href="spotifyURL" class="btn btn-success">Log in with Spotify</a> <button @click="hideBanner()" class="btn btn-secondary">Browse</button>
          </div>
      </div>
    </div>
  </div>
</template>

<script>
import {baseURL, staticURL} from "@/main.js";

export default {
  name: 'NavBar',
  data() {
    return {
      spotifyURL: baseURL + "connect_spotify",
      logoURL: staticURL + '/assets/logo.png'
    };
  },
  methods: {
    hideBanner(){
      this.$view.banner = false;
    }
  },
}
</script>

<style scoped>
.jumbotron{
  margin-bottom: 0px;
  padding-top: 0px;
  padding-bottom: 0px;
  height: 100%;
}
.overlay {
box-shadow: rgba(0, 0, 0, 0.07) 0px 1px 2px, rgba(0, 0, 0, 0.07) 0px 2px 4px, rgba(0, 0, 0, 0.07) 0px 4px 8px, rgba(0, 0, 0, 0.07) 0px 8px 16px, rgba(0, 0, 0, 0.07) 0px 16px 32px, rgba(0, 0, 0, 0.07) 0px 32px 64px;
  border-radius: 0px;
  background-color: rgb(52, 58, 64, 0.95);
  z-index: 1;
}
@supports (-moz-appearance:none) {
  .overlay {
    background-color: rgb(52, 58, 64, 0.95);
  }
}
img{
  margin: 5px;
}
.bg-text {
  color: var(--my-white);
  z-index: 99999999 !important;
  width: 100%;
  height: 100%;
  padding: 0px;
  text-align: center;
  position: absolute;
  top: 0px;
  left: 0px;
}
.content{
  padding-top: 32px;
  height: calc(100% - 100px);
  overflow-y: scroll;
}
.buttons-container{
  height: 100px;
  border-top: solid 1px var(--medium-gray);
}
.disable-scrollbars::-webkit-scrollbar {
  background: transparent; /* Chrome/Safari/Webkit */
  width: 0px;
}
    
.disable-scrollbars {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none;  /* IE 10+ */
}
p{
  font-weight: 300;
}
h1{
  margin-bottom: 16px;
}
h4{
  color: var(--yellow);
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
  margin-top: 32px;
  border: none;
}
.green{
  color: var(--green);
}
</style>
