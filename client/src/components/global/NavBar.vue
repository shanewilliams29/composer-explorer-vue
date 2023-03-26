<template>
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
            <b-nav-item id="home" :active='$route.path == "/"' @click="$router.push('/')"><b-icon-music-note-list></b-icon-music-note-list>&nbsp;&nbsp;Browse</b-nav-item>
            <b-nav-item id="performer" :active='$route.name == "performers"' @click="$router.push('/performers')"><b-icon-person-lines-fill></b-icon-person-lines-fill>&nbsp;&nbsp;Performers</b-nav-item>
            <b-nav-item v-if="$auth.clientToken" id="favorites" :active='$route.name == "favorites"' @click="$router.push('/favorites')"> <b-icon-heart></b-icon-heart>&nbsp;&nbsp;Favorites</b-nav-item>
            <b-nav-item id="radio" :active='$route.name == "radio"' @click="$router.push('/radio')"> <img :src="radioImgURL" class="radio-img" height="22px" />&nbsp;&nbsp;Radio</b-nav-item>
            <b-nav-item id="forum" href="/forum" target="_blank"> <b-icon-chat-right-text></b-icon-chat-right-text>&nbsp;&nbsp;Forum&nbsp;<b-badge>{{ unreadPosts }}</b-badge></b-nav-item>
          </b-nav>
        </div>

          <b-navbar-nav class="search-nav">
            <b-form-input class="omnisearch" v-model="omniSearchInput" v-debounce="omniSearch" type="search" placeholder="Search composers, works, performers" autocomplete="off"></b-form-input>
          </b-navbar-nav>

        <b-navbar-nav class="ml-auto" v-if="!$auth.clientToken">
          <b-button v-if="$view.avatar" right variant="success" class="spotify-button" :href="spotifyURL">
            <img :src="spotifyLogoURL" class="" alt="Spotify" height="28px" />
          </b-button>
          <b-nav-item class="menu-button" right v-b-toggle.sidebar-right><b-icon-three-dots-vertical></b-icon-three-dots-vertical></b-nav-item>
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

          <b-nav-item class="menu-button" right v-b-toggle.sidebar-right><b-icon-three-dots-vertical></b-icon-three-dots-vertical></b-nav-item>
        </b-navbar-nav>
      </b-navbar>
    </div>

    <div id="search-results" v-if="viewSearchResults">
      <b-card class="album-info-card shadow-sm">
        <!-- <h6 v-if="composers.length == 0">No search results.</h6> -->
        <h6 v-if="composers.length > 0">Composers</h6>
        <b-card-body class="card-body">
          <b-card-text class="info-card-text">
            <div v-for="composer in composers" :key="composer['id']">
              <table>
                <tr>
                  <td>
                    <b-avatar size="40px" :src="composer['img']"></b-avatar>
                  </td>
                  <td class="info-td">
                    <a class="artist-name">{{ composer['name_full'] }}</a><br />
                    <span class="born-died">{{ composer['born']}} - {{ composer['died']}}</span>
                  </td>
                </tr>
              </table>
            </div>
          </b-card-text>
        </b-card-body>
        <h6 v-if="works.length > 0">Works</h6>
        <b-card-body class="card-body">
          <b-card-text class="info-card-text">
            <div v-for="work in works" :key="work['id']">
              <table>
                <tr>
                  <td>
                    <b-avatar size="40px" :src="workImgUrl(work['genre'])"></b-avatar>
                  </td>
                  <td class="info-td">
                    <a class="artist-name">{{ work['title'] }}</a><br />
                    <span v-if="work['cat']" class="born-died">{{ work['composer']}} • {{ work['cat']}}</span>
                    <span v-else class="born-died">{{ work['composer']}}</span>
                  </td>
                </tr>
              </table>
            </div>
          </b-card-text>
        </b-card-body>
        <h6 v-if="results.length > 0">Performers</h6>
        <b-card-body class="card-body">
          <b-card-text class="info-card-text">
            <div v-for="result in results" :key="result[0]">
              <table>
                <tr>
                  <td>
                    <b-avatar size="40px" :src="result[2]"></b-avatar>
                  </td>
                  <td class="info-td">
                    <a class="artist-name">{{ result[0] }}</a><br />
                    <span class="born-died">{{ result[1] }}</span>
                  </td>
                </tr>
              </table>
            </div>
          </b-card-text>
        </b-card-body>
      </b-card>
    </div>
    
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
          <p v-if="!$view.mobile">For feature requests and bug reports:  <a href="https://github.com/shanewilliams29/composer-explorer-vue/issues" target="_blank">GitHub</a>.</p>
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
    <div>
    </div>
  </div>
</template>


<script>
import {baseURL, staticURL} from "@/main.js";
import axios from "axios";
import {getPeopleInfoFromGoogle} from "@/HelperFunctions.js" 

export default {
  name: 'NavBar',
  data() {
    return {
      radioImgURL: staticURL + 'radio.svg',
      spotifyLogoURL: staticURL + 'Spotify_Logo_RGB_White.png',
      logoURL: staticURL + 'logo.png',
      spotifyURL: baseURL + "connect_spotify",
      unreadPosts: null,
      omniSearchInput: null,
      viewSearchResults: false,
      composers: [],
      works: [],
      artists: [],
      results: []
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
    clientToken() {
      this.getUnreadPosts()
    },
    searchInput(searchInput) {
      if (searchInput == ""){
        this.viewSearchResults = false;
      }
    },
  },
  methods: {
    iOS() {
      return [
        'iPad Simulator',
        'iPhone Simulator',
        'iPod Simulator',
        'iPad',
        'iPhone',
        'iPod'
      ].includes(navigator.platform)
      // iPad on iOS 13 detection
      || (navigator.userAgent.includes("Mac") && "ontouchend" in document)
    },
    makeToast() {
      this.$bvToast.toast(`Get the App on Play Store`, {
        href: 'https://play.google.com/store/apps/details?id=com.app.composerexplorer',
        title: 'App available for Android',
        toaster: 'b-toaster-bottom-full',
        solid: true,
        variant: 'warning',
        autoHideDelay: 3600000
      })
    },
    workImgUrl(genre) {
      const url = 'https://storage.googleapis.com/composer-explorer.appspot.com/headers/' + genre + '.jpg';
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
        this.viewSearchResults = false;
      }
    },
    getOmniSearch(item) {
      const path = "api/omnisearch?search=" + item;
      axios
        .get(path)
        .then((res) => {
          this.composers = res.data.composers;
          this.works = res.data.works;
          this.artists = res.data.artists;
          this.results = [];
          this.artists.forEach((element) => getPeopleInfoFromGoogle(element, this.results, this.$auth.knowledgeKey));
          // Object.keys(this.artists).forEach((key) => getPeopleInfoFromGoogle(this.artists[key]['name'], this.results, this.$auth.knowledgeKey));
          this.viewSearchResults = true;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.viewSearchResults = true;
        });
    },
  },
  created(){
    var apple = this.iOS();
    var userAgent = window.navigator.userAgent.toLowerCase();
    //this.getUnreadPosts();

    if (userAgent.includes('wv')) { // Webview (App)
      this.$view.avatar = false;
    } else {
      this.$view.avatar = true;
      if (this.$view.mobile && !apple) {
        this.makeToast();
      }
    }
  },
  mounted() {
    // Periodically checks for new forum posts
    setInterval(this.getUnreadPosts, 60000);
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
  min-width: 600px !important;
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
.search-nav{
  width: 100% !important;
}
.omnisearch{
  background-color: var(--medium-gray) !important;
  width: 100% !important;
  margin-right: 10px;
}
.form-control:focus{
  box-shadow: none; 
  -webkit-box-shadow: none;
}
input[type="search"]::-webkit-search-cancel-button {
  -webkit-appearance: none;
   height: 13px;
   width: 13px;
   background: url("data:image/svg+xml;charset=UTF-8,%3csvg viewPort='0 0 12 12' version='1.1' xmlns='http://www.w3.org/2000/svg'%3e%3cline x1='1' y1='11' x2='11' y2='1' stroke='white' stroke-width='2'/%3e%3cline x1='1' y1='1' x2='11' y2='11' stroke='white' stroke-width='2'/%3e%3c/svg%3e");
}
#search-results{
  position: absolute;
  top: 66px;
  left: calc(165.3px + 600px);
  z-index: 9999;
  width: calc(100% - 165.3px - 600px - 5px);
}
.album-info-card {
  padding: 15px;
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
  max-height: 190px;
  padding-left: 2px;
}
.info-td {
  padding-left: 10px;
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
table {
  margin-bottom: 6px;
}
h6{
  padding-top: 5px;
}
</style>
