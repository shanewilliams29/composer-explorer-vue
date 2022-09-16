<template>
  <div v-show="!$view.mobileKeyboard">
    <div class="container-fluid">
      <b-navbar type="dark" variant="dark">
        <b-navbar-brand v-if="!$view.mobile">
          <img :src="logoURL" class="d-inline-block align-top logo" alt="Composer Explorer" height="40px"/>
        </b-navbar-brand>
          <b-navbar-brand @click="$router.push('/mobile')" v-if="$view.mobile">
          <img :src="logoURL" class="d-inline-block align-top logo" alt="Composer Explorer" height="40px"/>
        </b-navbar-brand>

        <div v-if="!$view.mobile">
          <b-nav pills class="navbar-items">
            <b-nav-item id="home" :active='$route.path == "/"' @click="$router.push('/')"><b-icon-music-note-list></b-icon-music-note-list>&nbsp;&nbsp;Browse</b-nav-item>
            <b-nav-item id="performer" :active='$route.name == "performers"' @click="$router.push('/performers')"><b-icon-person-lines-fill></b-icon-person-lines-fill>&nbsp;&nbsp;Performers</b-nav-item>
            <b-nav-item v-if="$auth.clientToken" id="favorites" :active='$route.name == "favorites"' @click="$router.push('/favorites')"> <b-icon-heart></b-icon-heart>&nbsp;&nbsp;Favorites</b-nav-item>
            <b-nav-item id="radio" :active='$route.name == "radio"' @click="$router.push('/radio')"> <img :src="radioImgURL" class="radio-img" height="22px" />&nbsp;&nbsp;Radio</b-nav-item>
          </b-nav>
        </div>
        <b-navbar-nav class="ml-auto" v-if="!$auth.clientToken">
          <b-button v-if="$view.avatar" right variant="success" class="spotify-button" :href="spotifyURL">
            <img :src="spotifyLogoURL" class="" alt="Spotify" height="28px" />
          </b-button>
          <b-nav-item class="menu-button" right v-b-toggle.sidebar-right><b-icon-three-dots-vertical></b-icon-three-dots-vertical></b-nav-item>
        </b-navbar-nav>
        <b-navbar-nav class="ml-auto" v-if="$auth.clientToken">
          <b-nav pills class="navbar-items">
            <b-nav-item v-if="$view.mobile && ($route.name != 'mobileradio')" id="radio" :active='$route.name == "mobileradio"' @click="$router.push('/mobileradio')"> <img :src="radioImgURL" class="radio-img" height="22px" />&nbsp;&nbsp;Radio</b-nav-item>
            <b-nav-item v-if="$view.mobile && ($route.name == 'mobileradio')" id="radio" :active='$route.name == "mobileradio"' @click="$router.push('/mobile')"> <img :src="radioImgURL" class="radio-img" height="22px" />&nbsp;&nbsp;Radio</b-nav-item>
          </b-nav>
          <b-dropdown v-if="$view.avatar" class="avatar-button" right no-caret>
            <template #button-content>
              <b-avatar href="#" :src="$auth.avatar"></b-avatar>
            </template>
            <!-- <b-dropdown-item @click="$router.push('/users')">User List</b-dropdown-item> -->
            <b-dropdown-item v-if="!$view.mobile" href="/change_avatar">Change Avatar</b-dropdown-item>
            <b-dropdown-item href="/log_out">Log out</b-dropdown-item>
          </b-dropdown>

          <b-nav-item class="menu-button" right v-b-toggle.sidebar-right><b-icon-three-dots-vertical></b-icon-three-dots-vertical></b-nav-item>
        </b-navbar-nav>
      </b-navbar>
    </div>
    <div>
      <b-sidebar id="sidebar-right" title="" backdrop-variant="dark" width="350px" backdrop right shadow>
        <div class="px-3 py-0 sidebar-text">
          <h6>Composer Explorer</h6>
          <p>Welcome to your Classical Music Portal. Explore composers from the Medieval to the present. Listen to works on Spotify, made navigable for Classical music.</p>
          <h6>Usage</h6>
          <p>Log in with your <b>Spotify Premium</b> account to play music. Add performances to your favorites and create your own customized radios.</p>
          <h6>Acknowledgements</h6>
          <p v-if="!$view.mobile">
            Composer and work information is used under licence from <a href="https://en.wikipedia.org/" target="_blank">Wikipedia</a>, <a href="https://imslp.org/" target="_blank">IMSLP</a>, and
            <a href="https://openopus.org/" target="_blank">Open Opus</a>. Album data and cover art provided by <a href="https://www.spotify.com/" target="_blank">Spotify</a>.
          </p>
            <p v-if="$view.mobile">
            Composer and work information is used under licence from Wikipedia, IMSLP, and Open Opus. Album data and cover art provided by Spotify.
          </p>
          <h6>Disclaimer</h6>
          <p>
            ComposerExplorer.com is not associated with Spotify Technology SA. Artist, album and track records are retrieved through the Spotify search API and do not necessarily represent the full extent of the Spotify catalogue for a
            given work. No guarantee is made as to the accuracy of catalogued composer and work information, and use is recommended for recreational purposes only.
          </p>
          <h6>Contact</h6>
          <p v-if="!$view.mobile">For all inquiries, please contact: <a href="mailto:admin@composerexplorer.com">admin@composerexplorer.com</a></p>
          <p v-if="$view.mobile">For all inquiries, please contact: admin@composerexplorer.com</p>
          <h6>Copyright</h6>
          <p>
            © 2022 ComposerExplorer.com. All rights reserved.
          </p>
        </div>
      </b-sidebar>
    </div>
  </div>
</template>

<script>
import {baseURL, staticURL} from "../main.js";

export default {
  name: 'NavBar',
  data() {
    return {
      radioImgURL: staticURL + 'radio.svg',
      spotifyLogoURL: staticURL + 'Spotify_Logo_RGB_White.png',
      logoURL: staticURL + 'logo.png',
      spotifyURL: baseURL + "connect_spotify"
    };
  },
  created(){
  var userAgent = window.navigator.userAgent.toLowerCase();
    if (userAgent.includes('wv')) {
      this.$view.avatar = false;
    } else {
      this.$view.avatar = true;
    }
  }
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
#favorites .active{
  background-color: var(--red);
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
.menu-button a {
  padding-right: 0px !important;
}
.sidebar-text{
  font-size: 14px;
}
.avatar-button >>> .btn{
  border: none !important;
  padding: 0px !important;
  background: transparent !important;
  margin-left: 5px;
}
</style>
