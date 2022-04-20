<template>
  <div>
    <!-- Image and text -->
    <b-navbar type="dark" variant="dark">
      <b-navbar-brand href="#">
        <img
          src="../assets/logo.png"
          class="d-inline-block align-top"
          alt="Composer Explorer"
          height="40px"
        />
      </b-navbar-brand>

<div>
  <b-nav pills class="navbar-items">
    <b-nav-item :active='$route.path == "/"' href="/"><b-icon-music-note-list></b-icon-music-note-list>&nbsp;Browse</b-nav-item>
    <b-nav-item :active='$route.name == "performers"' href="/performers"><b-icon-person-lines-fill></b-icon-person-lines-fill>&nbsp;Performers</b-nav-item>
    <b-nav-item :active='$route.name == "radio"' href="/radio"><b-icon-volume-up-fill></b-icon-volume-up-fill>&nbsp;Radio</b-nav-item>
  </b-nav>
</div>


      <b-navbar-nav class="ml-auto" v-if="!loggedIn">
        <b-nav-item disabled right class="log-in-with">Log in </b-nav-item>
        <b-button right
          variant="success"
          class="spotify-button"
          :href="spotifyURL"
          >
            <img
              src="@/assets/Spotify_Logo_RGB_White.png"
              class=""
              alt="Spotify"
              height="28px"
            />
        </b-button>
      </b-navbar-nav>



      <b-navbar-nav class="ml-auto" v-if="loggedIn">
        <b-nav-item href="/log_out" right>Log out</b-nav-item>
      </b-navbar-nav>
    </b-navbar>
  </div>
</template>

<script>
import {baseURL} from "../main.js";
import {eventBus} from "../main.js";

export default {
  name: 'NavBar',
  data() {
    return {
      spotifyURL: baseURL + "connect_spotify",
      loggedIn: false
    };
  },
  methods: {
    },
  created() {
    eventBus.$on('fireLogIn', (state) => {
      this.loggedIn = state;
    })
  },
}
</script>

<style scoped>
.log-in-with .disabled{
  color: lightgrey !important;
}
.spotify-button{
  background-color: #1db954;
  border: none;
}
img {
  margin-left: 0px;
}
.navbar.navbar-dark.bg-dark {
  background-color: #343a40 !important;
}
.navbar-items a{
  color: white !important;
}
</style>
