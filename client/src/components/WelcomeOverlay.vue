<template>
  <div v-if="$view.banner && !$auth.clientToken" class="container-fluid ">
    <div class="bg-text">
      <div id="welcome" class="jumbotron jumbotron-fluid text-center overlay">
        <div class="container">
          <h1 class="display-4">Welcome</h1>
          <p class="lead">Welcome to your Classical Music Portal. Explore composers from the Medieval to the present. <br> Listen to works on <b>Spotify, made navigable for Classical music.</b></p>

            <div class="container">

              <div class="row">
                <div class="col-lg-4 col-md-4 d-flex align-items-stretch">
                  <div class="icon-box">
                    <div class="icon"><i class="bx bx-search"></i></div>
                    <h4>Explore</h4>
                    <p>Discover new composers and new works by the composers you love. For the newcomer and the completionist.</p>
                  </div>
                </div>

                <div class="col-lg-4 col-md-4 d-flex align-items-stretch mt-4 mt-md-0">
                  <div class="icon-box">
                    <div class="icon"><i class="bx bx-music"></i></div>
                    <h4>Play Music</h4>
                    <p>Browse albums and connect with your Spotify account to play music and create playlists. Discover new artists.</p>
                  </div>
                </div>

                <div class="col-lg-4 col-md-4 d-flex align-items-stretch mt-4 mt-lg-0">
                  <div class="icon-box">
                    <div class="icon"><i class="bx bx-message"></i></div>
                    <h4>Engage</h4>
                    <p>Discuss works and performances, rate albums, track works you've explored, and add composers to your favorites.</p>
                  </div>
                </div>

              </div>

            </div>
  
          <a :href="spotifyURL" class="btn btn-success">Get Started</a> <button @click="hideBanner()" class="btn btn-secondary">Hide</button>
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
.overlay {
  border-radius: 20px;
  background-color: rgb(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  z-index: 1;

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
</style>
