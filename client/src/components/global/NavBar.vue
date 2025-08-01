<template>
  <div v-if="!$view.mobile">
    <div v-show="!$view.mobileKeyboard">
      <div class="container-fluid">
        <b-navbar type="dark" variant="dark">
          <b-navbar-brand v-if="!$view.mobile">
            <img :src="logoURL" class="d-inline-block align-top logo" alt="Composer Explorer" height="40px" />
          </b-navbar-brand>
          <b-navbar-brand @click="$router.push('/mobile')" v-if="$view.mobile">
            <img :src="logoURL" class="d-inline-block align-top logo" alt="Composer Explorer" height="40px" />
          </b-navbar-brand>
          <div v-if="!$view.mobile">
            <b-nav pills class="navbar-items buttons-nav">
              <b-nav-item id="home" :active='$route.path == "/"' @click="$router.push('/')">
                <b-icon-music-note-list></b-icon-music-note-list>&nbsp;&nbsp;Browse
              </b-nav-item>
              <b-nav-item id="performer" :active='$route.name == "performers"' @click="$router.push('/performers')">
                <b-icon-person-lines-fill></b-icon-person-lines-fill>&nbsp;&nbsp;Performers
              </b-nav-item>
              <b-nav-item id="albums" :active='$route.name == "albums"' @click="$router.push('/albums')">
                <b-icon-record-circle-fill></b-icon-record-circle-fill>&nbsp;&nbsp;Albums
              </b-nav-item>
              <b-nav-item v-if="$auth.clientToken" id="favorites" :active='$route.name == "favorites"' @click="$router.push('/favorites')">
                <b-icon-heart></b-icon-heart>&nbsp;&nbsp;Favorites
              </b-nav-item>
              <b-nav-item id="radio" :active='$route.name == "radio"' @click="$router.push('/radio')"> <img :src="radioImgURL" class="radio-img" height="22px" />&nbsp;&nbsp;Radio</b-nav-item>
              <!-- <b-nav-item id="forum" href="/forum" target="_blank"> <b-icon-chat-right-text></b-icon-chat-right-text>&nbsp;&nbsp;Forum&nbsp;<b-badge>{{ unreadPosts }}</b-badge></b-nav-item> -->
            </b-nav>
          </div>
          <b-navbar-nav v-if="!$view.mobile" class="search-nav">
            <div class="search-icon">
              <b-icon-search></b-icon-search>
            </div>
            <b-form-input id="search-form" class="omnisearch" size="sm" v-model="omniSearchInput" v-debounce:500ms="omniSearch" type="search" placeholder="Search composers, works, performers, albums" autocomplete="off"></b-form-input>
          </b-navbar-nav>
          <b-navbar-nav class="ml-auto" v-if="!$auth.clientToken">
            <b-button v-if="$view.avatar" right variant="success" class="spotify-button" :href="spotifyURL">
              <img :src="spotifyLogoURL" class="" alt="Spotify" height="28px" />
            </b-button>
            <b-nav-item class="menu-button" right v-b-toggle.sidebar-right>
              <b-icon-three-dots-vertical></b-icon-three-dots-vertical>
            </b-nav-item>
          </b-navbar-nav>
          <b-navbar-nav class="ml-auto" v-if="$auth.clientToken">
            <b-nav pills class="navbar-items">
              <b-nav-item v-if="$view.mobile && ($route.name != 'mobileradio')" id="radio" :active='$route.name == "mobileradio"' @click="$router.push('/mobileradio')">
                <img :src="radioImgURL" class="radio-img" height="22px" />&nbsp;&nbsp;Radio
              </b-nav-item>
              <b-nav-item v-if="$view.mobile && ($route.name == 'mobileradio')" id="radio" :active='$route.name == "mobileradio"' @click="$router.push('/mobile')">
                <img :src="radioImgURL" class="radio-img" height="22px" />&nbsp;&nbsp;Radio
              </b-nav-item>
            </b-nav>
            <b-dropdown v-if="$view.avatar" class="avatar-button" right no-caret>
              <template #button-content>
                <b-avatar href="#" :src="$auth.avatar"></b-avatar>
              </template>
              <b-dropdown-item v-if="!$view.mobile" href="/change_display_name">Change Display Name</b-dropdown-item>
              <b-dropdown-item v-if="!$view.mobile" href="/change_avatar">Change Avatar</b-dropdown-item>
              <b-dropdown-item href="/log_out">Log out</b-dropdown-item>
            </b-dropdown>
            <b-nav-item class="menu-button" right v-b-toggle.sidebar-right>
              <b-icon-three-dots-vertical></b-icon-three-dots-vertical>
            </b-nav-item>
          </b-navbar-nav>
        </b-navbar>
      </div>
      <Transition name="fade">
        <div v-show="viewSearchResults && !firstLoad" class="overlay" id="overlay"></div>
      </Transition>
      <Transition name="fade">
        <div id="search-results" v-show="viewSearchResults && !firstLoad">
          <b-card class="album-info-card shadow-sm">
            <div class="spinner" v-show="loading" role="status">
              <b-spinner class="m-5"></b-spinner>
            </div>
            <div v-show="!loading && !firstLoad">
              <h6 v-if="composers.length + works.length + artists.length + albums.length == 0">No search results.</h6>
            </div>
            <b-card-body v-show="!loading" id="composers" class="card-body">
              <h6 v-if="composers.length > 0">Composers</h6>
              <b-card-text ref="composersPanel" class="info-card-text">
                <div v-for="composer in composers" :key="composer['id']">
                  <table>
                    <tr>
                      <td>
                        <b-avatar size="40px" :src="composer['img']"></b-avatar>
                      </td>
                      <td class="info-td">
                        <a class="artist-name" @click="getComposer(composer)">{{ composer['name_full'] }}</a><br />
                        <span class="born-died">{{ composer['born']}} - {{ composer['died']}}</span>
                      </td>
                    </tr>
                  </table>
                </div>
              </b-card-text>
            </b-card-body>
            <b-card-body v-show="!loading" id="works" class="card-body">
              <h6 v-if="works.length > 0">Works</h6>
              <b-card-text ref="worksPanel" class="info-card-text">
                <div v-for="work in works" :key="work['id']">
                  <table>
                    <tr>
                      <td>
                        <b-avatar size="40px" :src="workImgUrl(work['genre'], work['title'])"></b-avatar>
                      </td>
                      <td class="info-td">
                        <a v-if="work['nickname']" @click="getSearchWork(work)" class="artist-name">{{ work['title'] }} • {{ work['nickname']}}</a>
                        <a v-else @click="getSearchWork(work)" class="artist-name">{{ work['title'] }}</a><br />
                        <span v-if="work['cat']" class="born-died">{{ work['composer']}} • {{ work['cat']}}</span>
                        <span v-else class="born-died">{{ work['composer']}}</span>
                      </td>
                    </tr>
                  </table>
                </div>
              </b-card-text>
            </b-card-body>
            <b-card-body v-show="!loading" id="performers" class="card-body">
              <h6 v-if="artists.length > 0">Performers</h6>
              <b-card-text ref="artistsPanel" class="info-card-text">
                <div v-for="artist in artists" :key="artist.id">
                  <table>
                    <tr>
                      <td>
                        <b-avatar size="40px" :src="artist.img"></b-avatar>
                      </td>
                      <td class="info-td">
                        <a class="artist-name" @click="getArtistComposers(artist)">{{ artist.name }}</a><br />
                        <span class="born-died">{{ artist.description }}</span>
                      </td>
                    </tr>
                  </table>
                </div>
              </b-card-text>
            </b-card-body>
            <b-card-body v-show="!loading" id="albums" class="card-body">
              <h6 v-if="albums.length > 0">Albums</h6>
              <b-card-text ref="albumsPanel" class="info-card-text">
                <div v-for="album in albums" :key="album.id">
                  <table>
                    <tr>
                      <td>
                        <b-avatar square size="40px" :src="album.img"></b-avatar>
                      </td>
                      <td class="info-td wrap-text">
                        <a class="artist-name" @click="goToAlbum(album.album_id)">{{ album.title }}</a><br />
                        <span class="born-died">{{ album.artists }}</span>
                      </td>
                    </tr>
                  </table>
                </div>
              </b-card-text>
            </b-card-body>
          </b-card>
        </div>
      </Transition>
      <div>
        <b-sidebar id="sidebar-right" title="" backdrop-variant="dark" width="350px" backdrop right shadow>
          <div class="px-3 py-0 sidebar-text">
            <h6>Composer Explorer</h6>
            <p>Welcome to your Classical Music Portal. Explore composers from the Medieval to the present. Listen to works on Spotify, made navigable for Classical music.</p>
            <h6>Usage</h6>
            <p>Log in with your <b>Spotify Premium</b> account to play music. Add performances to your favorites and create your own customized radios.</p>
            <p v-if="false">
              <span style="color: red;"><b>Android App:</b></span> Battery optimizations may stop playback (such as when phone is locked). Enable unrestricted battery access to the app in your phone's settings:
              <span style="color: darkblue;">Settings > Apps > Composer Explorer > Battery > Unrestricted</span>.
            </p>
            <h6>Acknowledgements</h6>
            <p v-if="!$view.mobile">
              Composer and work information is used under licence from <a href="https://en.wikipedia.org/" target="_blank">Wikipedia</a>, <a href="https://imslp.org/" target="_blank">IMSLP</a>, and
              <a href="https://openopus.org/" target="_blank">Open Opus</a>. Album data and cover art provided by <a href="https://www.spotify.com/" target="_blank">Spotify</a>.
            </p>
            <h6 v-if="!$view.mobile">Donations</h6>
            <p v-if="!$view.mobile">
              Composer Explorer is offered as a free and ad-free experience. If you would like to support the costs of hosting and development, please sponsor us on <a href="https://www.patreon.com/composerexplorer" target="_blank">Patreon</a>.
            </p>
            <p v-if="$view.mobile">
              Composer and work information is used under licence from Wikipedia, IMSLP, and Open Opus. Album data and cover art provided by Spotify.
            </p>
            <h6>Disclaimer</h6>
            <p>
              ComposerExplorer.com is not associated with Spotify Technology SA. Artist, album and track records are retrieved through the Spotify search API and do not necessarily represent the full extent of the Spotify catalogue for a
              given work. No guarantee is made as to the accuracy of catalogued composer and work information, and use is recommended for recreational purposes only.
            </p>
            <h6 v-if="!$view.mobile">GitHub</h6>
            <p v-if="!$view.mobile">For feature requests and bug reports: <a href="https://github.com/shanewilliams29/composer-explorer-vue/issues" target="_blank">GitHub</a>.</p>
            <h6>Contact</h6>
            <p v-if="!$view.mobile">For all inquiries, please contact: <a href="mailto:composerexplorer@gmail.com">composerexplorer@gmail.com</a></p>
            <p v-if="$view.mobile">For all inquiries, please contact: composerexplorer@gmail.com</p>
            <h6>Copyright</h6>
            <p>
              © 2022 ComposerExplorer.com. All rights reserved.
            </p>
          </div>
        </b-sidebar>
      </div>
      <div>
      </div>
    </div>
  </div>
</template>


<script>
import {baseURL, staticURL} from "@/main.js";
import axios from "axios";
import { eventBus } from "@/main.js";

export default {
  name: 'NavBar',
  data() {
    return {
      radioImgURL: staticURL + '/assets/radio.svg',
      spotifyLogoURL: staticURL + '/assets/Spotify_Logo_RGB_White.png',
      logoURL: staticURL + '/assets/logo.png',
      spotifyURL: baseURL + "connect_spotify",
      unreadPosts: null,
      omniSearchInput: null,
      viewSearchResults: false,
      composers: [],
      works: [],
      artists: [],
      albums: [],
      loading: false,
      firstLoad: true
    };
  },
  computed: {
    clientToken() {
      return this.$auth.clientToken;
    },
    searchInput() {
      return this.omniSearchInput;
    },
  },
  watch: {
    searchInput(searchInput) {
      if (searchInput == ""){
        this.resetScroll();
        this.viewSearchResults = false;
        this.firstLoad = true;
      }
    },
  },
  methods: {
    workImgUrl(genre, title) {
      let url = "";
      if(genre == 'Opera' || genre == 'Stage Work' || genre == 'Ballet'){
        url = 'https://usc1.contabostorage.com/a36ba68caf9842799883275ab3ad3a88:composer-explorer.bucket/static/headers/' + title + '.jpg';
      } else {
        url = 'https://usc1.contabostorage.com/a36ba68caf9842799883275ab3ad3a88:composer-explorer.bucket/static/headers/' + genre + '.jpg';
      }
      return url;
    },
    getUnreadPosts() {
      if(this.$auth.clientToken){
        const path = "api/userdata";
        axios
          .get(path)
          .then((res) => {
            this.unreadPosts = res.data.new_posts;
          })
          .catch((error) => {
            console.error(error);
          });
        }
    },
    omniSearch() {
      if (this.omniSearchInput !== ""){
        this.getOmniSearch(this.omniSearchInput);
      } else {
        //this.viewSearchResults = false;
      }
    },
    resetScroll() {
      this.$refs.composersPanel.scrollTop = 0;
      this.$refs.worksPanel.scrollTop = 0;
      this.$refs.artistsPanel.scrollTop = 0;
      this.$refs.albumsPanel.scrollTop = 0;
    },    
    getOmniSearch(item) {
      this.resetScroll();
      this.loading = true;
      this.viewSearchResults = true;
      this.firstLoad = false;
      this.composers = [];
      this.works = [];
      this.artists = [];
      this.albums = [];

      const path = "api/elasticsearch?search=" + item;
      
      let wordsArray = item.split(" ");
      let worksFirst = false;
      if(wordsArray.length > 1){
        worksFirst = false;
      }

      axios
        .get(path)
        .then((res) => {
          this.composers = res.data.composers;
          this.works = res.data.works;
          this.artists = res.data.artists;
          this.albums = res.data.albums;
          this.loading = false;

          var content = "";
          var parent = "";

          if (worksFirst){
            content = document.getElementById('works');
            parent = content.parentNode;
            parent.insertBefore(content, parent.firstChild);
          } else {
            content = document.getElementById('composers');
            parent = content.parentNode;
            parent.insertBefore(content, parent.firstChild);
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading = false;
          this.viewSearchResults = true;
          this.ajax_waiting = false;
        });
    },
    getComposer(composer) {
        this.viewSearchResults = false;
        let delay = 0;
        if (this.$route.name != "home") {
          delay = 200;
          this.$router.push("/?search=" + composer.name_short);
        }
        setTimeout(function(){
          eventBus.$emit("fireComposerOmniSearch", composer);
          eventBus.$emit("requestWorksList", composer.name_short);
          eventBus.$emit("clearAlbumsList", composer.name_short);
          eventBus.$emit("sendArtistList", []);
        }, delay);
    },
    getSearchWork(work) {
        this.viewSearchResults = false;

        let delay = 0;
        if (this.$route.name != "home") {
          delay = 200;
          this.$router.push("/?search=" + work.id);
        }
        setTimeout(function(){
          eventBus.$emit("fireWorkOmniSearch", work);
        }, delay);
    },
    getArtistComposers(artist) {
      this.viewSearchResults = false;
      if (!this.$view.mobile) {
        this.$config.artist = artist;
        if (this.$route.name != "performers") {
          this.$router.push("/performers?artist=" + artist.id);
        } else {
          eventBus.$emit("requestPerformer", artist);
        }
      }
    },
    goToAlbum(album_id) {
      this.viewSearchResults = false;
      if (!this.$view.mobile) {
          this.$router.push("/albums?id=" + album_id);
      }
    },
  },
  created(){
    var userAgent = window.navigator.userAgent.toLowerCase();

    if (userAgent.includes('wv')) { // Webview (App)
      this.$view.avatar = false;
    } else {
      this.$view.avatar = true;
    }
  },
  mounted() {
    const inputForm = document.getElementById("search-form");
    const overlay = document.getElementById('overlay');

    inputForm.addEventListener('click', () => {
      this.viewSearchResults = true;
    });

    overlay.addEventListener('click', () => {
      this.viewSearchResults = false;
    });

  },
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
     .overlay {
            display: block;
            position: absolute;
            top: 66;
            left: 0;
            width: 100%;
            height: calc(100% - 66px);
            background: rgba(52, 58, 64, 0.5);
            z-index: 10;
        }
#home .active{
  background-color: var(--blue);
}
#performer .active{
  background-color: var(--purple);
}
#albums .active{
  background-color: var(--orange);
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
  background-color: var(--dark-gray) !important;
}
.buttons-nav{
  min-width: 620px !important;
}
.navbar-items a {
  color: var(--my-white) !important;
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
.search-icon{
  position: absolute;
  top: 21px;
  left: calc(165.3px + 600px + 38px);
  color: white;
}
.search-nav{
  width: 100% !important;
}
.omnisearch{
  background-color: var(--medium-gray) !important;
  width: 100% !important;
  margin-right: 30px;
  margin-left: 10px;
}
.form-control:focus{
  box-shadow: none; 
  -webkit-box-shadow: none;
}
input[type="search"]{
  padding-left: 31px !important;
}
input[type="search"]::-webkit-search-cancel-button {
  -webkit-appearance: none;
   height: 13px;
   width: 13px;
   background: url("data:image/svg+xml;charset=UTF-8,%3csvg viewPort='0 0 12 12' version='1.1' xmlns='http://www.w3.org/2000/svg'%3e%3cline x1='1' y1='11' x2='11' y2='1' stroke='white' stroke-width='2'/%3e%3cline x1='1' y1='1' x2='11' y2='11' stroke='white' stroke-width='2'/%3e%3c/svg%3e");
}
#search-results{
  position: absolute;
  top: 60px;
  left: calc(165.3px + 600px + 30px);
  z-index: 9999;
  width: calc(100% - 165.3px - 600px - 35px);
  box-shadow: rgba(0, 0, 0, 0.07) 0px 1px 2px, rgba(0, 0, 0, 0.07) 0px 2px 4px, rgba(0, 0, 0, 0.07) 0px 4px 8px, rgba(0, 0, 0, 0.07) 0px 8px 16px, rgba(0, 0, 0, 0.07) 0px 16px 32px, rgba(0, 0, 0, 0.07) 0px 32px 64px;
}
.spinner {
  text-align: center;
}
.m-5 {
    color: #9da6af;
}
.album-info-card {
  padding-left: 15px;
  padding-right: 15px;
  padding-top: 8px;
  padding-bottom: 10px;
  background-color: var(--my-white) !important;
  border: none !important;
}
.card-body {
  background-color: var(--my-white) !important;
  --scroll-bar-bg-color: var(--light-gray);
}
.info-card-text {
  font-size: 13px;
  line-height: 130%;
  overflow-y: scroll;
  max-height: 143px;
  padding-left: 2px;
}
.info-td {
  padding-left: 10px;
}
.wrap-text {
  color: gray;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
}
.born-died {
  font-size: 13px !important;
  color: grey !important;
}
.artist-name {
  color: black !important;
  font-weight: 600;
  font-size: 14px;
}
.artist-name:hover {
  color: black !important;
  text-decoration: underline !important;
  cursor: pointer;
}

/*scrollbars*/
.info-card-text {
  --scroll-bar-color: var(--scroll-color-light);
  --scroll-bar-bg-color: var(--my-white);
}
.info-card-text {
  scrollbar-width: thin;
  scrollbar-color: var(--scroll-bar-color) var(--scroll-bar-bg-color) !important;
}

/* Works on Chrome, Edge, and Safari */
.info-card-text::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}
.info-card-text::-webkit-scrollbar-track {
  background: var(--scroll-bar-bg-color) !important;
}
.info-card-text::-webkit-scrollbar-thumb {
  background-color: var(--scroll-bar-color);
  border-radius: 20px;
  border: 3px solid var(--scroll-bar-bg-color) !important;
}

table {
  margin-bottom: 6px;
}
h6{
  padding-top: 5px;
}
</style>
