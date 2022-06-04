<template>
  <div v-if="$view.banner && !$auth.clientToken" class="container-fluid ">
    <div class="bg-text">
      <div id="welcome" class="jumbotron overlay">
        <div class="container">
          <h1 class="display-4">Welcome</h1>
          <p class="lead">Welcome to your Classical Music Portal. Explore composers from the Medieval to the present. <br> Listen to works on <b>Spotify, made navigable for Classical music.</b></p>

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
                    <p>Browse albums and connect with your Spotify account to play music and create playlists. Discover new artists.</p>
                  </div>
                </div>

                <div class="col-lg-4 col-md-4 d-flex align-items-stretch">
                  <div class="icon-box">
                    <div class="icon"><b-icon icon="chat-right" aria-hidden="true"></b-icon></div>
                    <h4>Engage</h4>
                    <p>Discuss works and performances, rate albums, track works you've explored, and add composers to your favorites.</p>
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
import {baseURL} from "../main.js";

export default {
  name: 'NavBar',
  data() {
    return {
      spotifyURL: baseURL + "connect_spotify"
    };
  },
  methods: {
    hideBanner(){
      this.$view.banner = false;
    }
  }
}
</script>

<style scoped>
.jumbotron{
  margin-bottom: 0px;
  padding-top: 32px;
  padding-bottom: 32px;
}
.overlay {
  border-radius: 20px;
  background-color: rgb(241, 242, 244, 0.8);
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
  z-index: 1;
}
@supports (-moz-appearance:none) {
  .overlay {
    border-radius: 20px;
    background-color: #f1f2f4;
    z-index: 1;
  }
}
.bg-text {
  color: black;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
  width: 80%;
  padding: 20px;
  text-align: center;
}
.icon-box {
  padding: 0px;
  text-align: center;
  transition: all ease-in-out 0.3s;
}
.icon {
  align-items: center;
/*  background: rgb(241, 242, 244, 0.7);*/
/*  border-radius: 50px;*/
  display: flex;
  height: 64px;
  justify-content: center;
  margin: 0 auto;
  margin-bottom: 0px;
  width: 64px;
  font-size: 24px;
}
.btn{
  margin-top: 20px;
}
</style>
