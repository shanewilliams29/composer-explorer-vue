<template>
  <div v-if="$view.banner && !$auth.clientToken && !$view.mobile" class="container-fluid">
    <div class="bg-text">
      <div id="welcome" class="jumbotron overlay">
        <div class="container">
          <h1>
            <img :src="logoURL" class="d-inline-block align-top logo" alt="Composer Explorer" height="60px" />
          </h1>
          <p class="lead">
            Welcome to your Classical Music Portal. Explore composers from the Medieval to the present. <br />
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

          <a :href="spotifyURL" class="btn btn-success">Log in with Spotify</a> <button @click="hideBanner()" class="btn btn-secondary">Hide</button>
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
  padding-top: 32px;
  padding-bottom: 32px;
}
.overlay {
box-shadow: rgba(0, 0, 0, 0.07) 0px 1px 2px, rgba(0, 0, 0, 0.07) 0px 2px 4px, rgba(0, 0, 0, 0.07) 0px 4px 8px, rgba(0, 0, 0, 0.07) 0px 8px 16px, rgba(0, 0, 0, 0.07) 0px 16px 32px, rgba(0, 0, 0, 0.07) 0px 32px 64px;
  border-radius: 20px;
  background-color: rgb(52, 58, 64, 0.97);
/*  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);*/
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
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
  width: 80%;
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
