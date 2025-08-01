<template>
  <div>
    <div>
      <div class="container-fluid">
        <b-navbar type="dark" variant="dark">
          <b-navbar-nav class="search-nav">
            <div class="search-icon">
              <b-icon-search></b-icon-search>
            </div>
            <b-form-input ref="searchBox" id="search-form" class="omnisearch" v-model="omniSearchInput" v-debounce:1000ms="omniSearch" type="search" placeholder="Composers, works, performers, albums" autocomplete="off"></b-form-input>
          </b-navbar-nav>
        </b-navbar>
      </div>
      <div id="dummy-div">
        <div id="search-results" v-show="viewSearchResults && !firstLoad" @scroll="hideKeyboard">
          <b-card class="album-info-card">
            <div class="spinner" v-show="loading" role="status">
              <b-spinner class="m-5"></b-spinner>
            </div>
            <div v-show="!loading && !firstLoad">
              <h6 v-if="composers.length + works.length + artists.length + albums.length == 0">No search results.</h6>
            </div>
            <b-card-body v-show="!loading" id="composers" class="card-body">
              <h5 v-if="composers.length > 0">Composers</h5>
              <b-card-text class="info-card-text">
                <div v-for="composer in composers" :key="composer['id']" @click="getComposer(composer)">
                  <table>
                    <tr>
                      <td>
                        <b-avatar size="52px" :src="composer['img']"></b-avatar>
                      </td>
                      <td class="info-td">
                        <a class="artist-name">{{ composer['name_full'] }}</a><br />
                        <span class="born-died">{{ composer['nationality'] }} • {{ composer['born']}} - {{ composer['died']}}</span>
                      </td>
                    </tr>
                  </table>
                </div>
              </b-card-text>
              <hr v-if="composers.length > 0">
            </b-card-body>
            <b-card-body v-show="!loading" id="works" class="card-body">
              <h5 v-if="works.length > 0">Works</h5>
              <b-card-text class="info-card-text">
                <div v-for="work in works" :key="work['id']" @click="getSearchWork(work)">
                  <table>
                    <tr>
                      <td>
                        <b-avatar size="52px" :src="workImgUrl(work['genre'], work['title'])"></b-avatar>
                      </td>
                      <td class="info-td">
                        <a v-if="work['nickname']" class="artist-name">{{ work['title'] }} • {{ work['nickname']}}</a>
                        <a v-else class="artist-name">{{ work['title'] }}</a><br />
                        <span v-if="work['cat']" class="born-died">{{ work['composer']}} • {{ work['cat']}}</span>
                        <span v-else class="born-died">{{ work['composer']}}</span>
                      </td>
                    </tr>
                  </table>
                </div>
              </b-card-text>
              <hr v-if="works.length > 0">
            </b-card-body>
            <b-card-body v-show="!loading" id="performers" class="card-body">
              <h5 v-if="artists.length > 0">Performers</h5>
              <b-card-text class="info-card-text">
                <div v-for="artist in artists" :key="artist.id" @click="getArtistComposers(artist)">
                  <table>
                    <tr>
                      <td>
                        <b-avatar size="52px" :src="artist.img"></b-avatar>
                      </td>
                      <td class="info-td">
                        <a class="artist-name">{{ artist.name }}</a><br />
                        <span v-if="artist.description !== 'NA'" class="born-died">{{ artist.description }}</span>
                      </td>
                    </tr>
                  </table>
                </div>
              </b-card-text>
              <hr v-if="artists.length > 0">
            </b-card-body>
  <b-card-body v-show="!loading" id="albums" class="card-body">
    <h5 v-if="albums.length > 0">Albums</h5>
    <b-card-text class="info-card-text">
      <div v-for="album in albums" :key="album.id" @click="goToAlbum(album.album_id)">
        <table>
          <tr>
            <td>
              <b-avatar square size="52px" :src="album.img"></b-avatar>
            </td>
            <td class="info-td">
              <div class="wrap-text align-middle">
                <a class="artist-name" @click="goToAlbum(album.album_id)">{{ album.title }}</a><br />
                <span class="born-died">{{ album.artists }}</span>
              </div>
            </td>
          </tr>
        </table>
      </div>
    </b-card-text>
  </b-card-body>
          </b-card>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { baseURL, staticURL } from "@/main.js";
import axios from "axios";
import { eventBus } from "@/main.js";

export default {
  name: 'NavBar',
  data() {
    return {
      radioImgURL: staticURL + '/assets/radio.svg',
      spotifyLogoURL: staticURL + '/assets/Spotify_Logo_RGB_White.png',
      logoURL: staticURL + '/assets/logo.png',
      spotifyURL: baseURL + "/assets/connect_spotify",
      unreadPosts: null,
      omniSearchInput: null,
      viewSearchResults: false,
      composers: [],
      works: [],
      artists: [],
      albums: [],
      loading: false,
      firstLoad: true,
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
      if (searchInput == "") {
        this.viewSearchResults = false;
        this.firstLoad = true;
      }
    },
  },
  methods: {
    hideKeyboard() {
      document.activeElement.blur();
    },
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
        ||
        (navigator.userAgent.includes("Mac") && "ontouchend" in document)
    },
    // makeToast() {
    //   this.$bvToast.toast(`Get the App on Play Store`, {
    //     href: 'https://play.google.com/store/apps/details?id=com.app.composerexplorer',
    //     title: 'App available for Android',
    //     toaster: 'b-toaster-bottom-full',
    //     solid: true,
    //     variant: 'warning',
    //     autoHideDelay: 3600000
    //   })
    // },
    workImgUrl(genre, title) {
      let url = "";
      if (genre == 'Opera' || genre == 'Stage Work' || genre == 'Ballet') {
        url = 'https://usc1.contabostorage.com/a36ba68caf9842799883275ab3ad3a88:composer-explorer.bucket/static/headers/' + title + '.jpg';
      } else {
        url = 'https://usc1.contabostorage.com/a36ba68caf9842799883275ab3ad3a88:composer-explorer.bucket/static/headers/' + genre + '.jpg';
      }
      return url;
    },
    getUnreadPosts() {
      if (this.$auth.clientToken) {
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
      if (this.omniSearchInput !== "") {
        this.getOmniSearch(this.omniSearchInput);
      } else {
        //this.viewSearchResults = false;
      }
    },
    getOmniSearch(item) {
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
      if (wordsArray.length > 1) {
        worksFirst = false;
      }

      axios
        .get(path)
        .then((res) => {
          this.composers = res.data.composers;
          this.works = res.data.works.slice(0, 5);
          this.artists = res.data.artists.slice(0, 3);
          this.albums = res.data.albums;
          this.loading = false;

          var content = "";
          var parent = "";

          if (worksFirst) {
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
        this.$router.push("/mobile?search=" + composer.name_short);
      }
      setTimeout(function() {
        eventBus.$emit("fireComposerOmniSearch", composer);
        eventBus.$emit("requestWorksList", composer.name_short);
      }, delay);
    },
    getSearchWork(work) {
      this.viewSearchResults = false;

      let delay = 0;
      if (this.$route.name != "home") {
        delay = 200;
        this.$router.push("/mobile?search=" + work.id);
      }
      setTimeout(function() {
        eventBus.$emit("fireWorkOmniSearch", work);
        eventBus.$emit("requestWorksList", work.composer);
        eventBus.$emit("requestAlbums");
      }, delay);
    },
    getArtistComposers(artist) {
      this.viewSearchResults = false;
      this.$config.artist = artist;
      this.$router.push("/mobileperformers?artist=" + artist.id);
    },
    detectKeyboard() {
      let vh = window.innerHeight * 0.01;
      // for mobile keyboard
      if (window.innerHeight < this.$view.initialWindowHeight) {
        this.$view.mobileKeyboard = true;
        vh = vh + 145 * 0.01;
      } else {
        this.$view.mobileKeyboard = false;
      }
      document.documentElement.style.setProperty("--vh", `${vh}px`);
    },
    goToAlbum(album_id) {
      this.$router.push("/mobilealbums?id=" + album_id);
    },
  },
  beforeCreate(){
    document.documentElement.style.setProperty("--workingheight", `191.6px`);
  },
  created() {
    this.initialWindowHeight = window.innerHeight;
    window.addEventListener('resize', this.detectKeyboard);
  },
  mounted() {
    this.$refs.searchBox.focus();
    const inputForm = document.getElementById("search-form");
    const overlay = document.getElementById("overlay");

    inputForm.addEventListener('click', () => {
      this.viewSearchResults = true;
    });

    overlay.addEventListener('click', () => {
      this.viewSearchResults = false;
    });
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.detectKeyboard);
  }
}
</script>

<style scoped>
h5 {
  padding-bottom: 3px;
  color: var(--my-white);
}

hr {
  border-top: 1px solid var(--medium-gray);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter,
.fade-leave-to {
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

#home .active {
  background-color: var(--blue);
}

#performer .active {
  background-color: var(--purple);
}

#albums .active {
  background-color: var(--orange);
}

#radio .active {
  background-color: var(--green);
}

#favorites .active {
  background-color: var(--red);
}

.radio-img {
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

.buttons-nav {
  min-width: 620px !important;
}

.navbar-items a {
  color: var(--my-white) !important;
}

.menu-button a {
  padding-right: 0px !important;
}

.sidebar-text {
  font-size: 14px;
}

.avatar-button>>>.btn {
  border: none !important;
  padding: 0px !important;
  background: transparent !important;
  margin-left: 5px;
}

.search-icon {
  position: absolute;
  top: 15px;
  left: 24px;
  color: white;
}

.search-nav {
  width: 100% !important;
}

.omnisearch {
  background-color: var(--medium-gray) !important;
  width: 100% !important;
  margin-right: 0px;
  margin-left: 0px;
}

.wrap-text {
  color: gray;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
}

.align-middle {
vertical-align: middle;
}

.form-control:focus {
  box-shadow: none;
  -webkit-box-shadow: none;
}

input[type="search"] {
  padding-left: 31px !important;
}

input[type="search"]::-webkit-search-cancel-button {
  -webkit-appearance: none;
  height: 13px;
  width: 13px;
  background: url("data:image/svg+xml;charset=UTF-8,%3csvg viewPort='0 0 12 12' version='1.1' xmlns='http://www.w3.org/2000/svg'%3e%3cline x1='1' y1='11' x2='11' y2='1' stroke='white' stroke-width='2'/%3e%3cline x1='1' y1='1' x2='11' y2='11' stroke='white' stroke-width='2'/%3e%3c/svg%3e");
}

#dummy-div {
  background-color: var(--dark-gray);
  width: 100%;
  height: calc(var(--vh, 1vh) * 100 - 54px - var(--workingheight));
}

#search-results {
  width: 100%;
  z-index: 9999;
  max-height: calc(var(--vh, 1vh) * 100 - 54px - var(--workingheight));
  overflow-y: scroll;
  background: none;
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
  background: none;
  border: none !important;
}

.card-body {
  background: none;
  --scroll-bar-bg-color: var(--light-gray);
}

.info-card-text {
  font-size: 13px;
  line-height: 130%;
  padding-left: 2px;
}

.info-td {
  padding-left: 10px;
}

.born-died {
  font-size: 14px !important;
  color: var(--medium-dark-gray) !important;
}

.artist-name {
  color: var(--my-white) !important;
  font-weight: 500;
  font-size: 16px;
}

.artist-name:hover {
  text-decoration: none;
}

/*scrollbars*/
#search-results {
  --scroll-bar-color: var(--medium-dark-gray);
  --scroll-bar-bg-color: var(--dark-gray);
}

#search-results {
  scrollbar-width: thin;
  scrollbar-color: var(--scroll-bar-color) var(--scroll-bar-bg-color) !important;
}

/* Works on Chrome, Edge, and Safari */
#search-results::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}

#search-results::-webkit-scrollbar-track {
  background: var(--scroll-bar-bg-color) !important;
}

#search-results::-webkit-scrollbar-thumb {
  background-color: var(--scroll-bar-color);
  border-radius: 20px;
  border: 3px solid var(--scroll-bar-bg-color) !important;
}

table {
  margin-bottom: 6px;
}

h6 {
  color: white;
  padding-top: 5px;
}
</style>
