<template>
  <div class="container-fluid">
    <b-navbar type="dark" variant="dark">
      <b-navbar-brand href="#">
        <img src="../assets/logo.png" class="d-inline-block align-top logo" alt="Composer Explorer" height="40px" @click="$router.push('/')" />
      </b-navbar-brand>
      <div>
        <b-nav pills class="navbar-items">
          <b-nav-item id="home" :active='$route.path == "/"' @click="$router.push('/')"><b-icon-music-note-list></b-icon-music-note-list>&nbsp;&nbsp;Browse</b-nav-item>
          <b-nav-item id="performer" :active='$route.name == "performers"' @click="$router.push('/performers')"><b-icon-person-lines-fill></b-icon-person-lines-fill>&nbsp;&nbsp;Performers</b-nav-item>
          <b-nav-item id="radio" :active='$route.name == "radio"' @click="$router.push('/radio')"> <img src="@/assets/radio.svg" class="radio-img" height="22px" />&nbsp;&nbsp;Radio</b-nav-item>
        </b-nav>
      </div>
      <b-navbar-nav class="ml-auto" v-if="!$auth.clientToken">
        <b-nav-item disabled right class="log-in-with">Log in </b-nav-item>
        <b-button right variant="success" class="spotify-button" :href="spotifyURL">
          <img src="@/assets/Spotify_Logo_RGB_White.png" class="" alt="Spotify" height="28px" />
        </b-button>
      </b-navbar-nav>
      <b-navbar-nav class="ml-auto" v-if="$auth.clientToken">
        <b-nav-item href="/log_out" right>Log out</b-nav-item>
      </b-navbar-nav>
    </b-navbar>
  </div>
</template>

<script>
import {baseURL} from "../main.js";

export default {
  name: 'NavBar',
  data() {
    return {
      spotifyURL: baseURL + "connect_spotify",
    };
  },
}
</script>

<style scoped>
#home .active{
  background-color: var(--blue);
}
#performer .active{
  background-color: var(--purple);
}
#radio .active{
  background-color: var(--green);
}

.radio-img{
  padding-bottom: 0px;
}

.container-fluid {
  padding: 0px;
}
.log-in-with .disabled {
  color: lightgrey !important;
}
.spotify-button {
  background-color: #1db954;
  border: none;
}
img {
  margin-left: 0px;
}
.navbar.navbar-dark.bg-dark {
  background-color: #343a40 !important;
}
.navbar-items a {
  color: white !important;
}
</style>
