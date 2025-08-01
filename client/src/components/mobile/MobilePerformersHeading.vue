<template>
  <div>
    <div class="container-fluid">
      <b-row class="flex-nowrap">
        <b-col class="text-center">
          <div class="vertical-centered">
            <div class="no-results" v-if="!$config.artist">
              <table class="dummy-table">
                Search for a performer to view composers and works they perform
              </table>
            </div>
            <table class="headings-table" v-if="$config.artist">
              <tr class="tr-performer">
                <td>
                  <b-avatar class="avatar" size="64px" :src="$config.artist.img"></b-avatar>
                </td>
                <td class="td-text">
                  <span class="artist-name">{{ $config.artist.name }}&nbsp;</span><br />
                  <span v-if="$config.artist.wiki_link != 'NA'" class="artist-job">{{ $config.artist.description }}</span>
                </td>
              </tr>
            </table>
          </div>
        </b-col>
      </b-row>
      <b-row>
        <div class="container-fluid">
          <b-form-input id="performer-search-form" class="omnisearch" v-model="omniSearchInput" v-debounce:1000ms="omniSearch" @focus="onInputFocus()" type="search" placeholder="Search for a performer" autocomplete="off">
          </b-form-input>
        </div>
      </b-row>
    </div>
    <div>
      <Transition name="fade">
        <div v-show="viewSearchResults && !firstLoad" class="overlay" id="performer-overlay"></div>
      </Transition>
      <Transition name="fade">
        <div id="performer-search-results" v-show="viewSearchResults && !firstLoad">
          <b-card class="search-card">
            <div class="spinner" v-show="loading" role="status">
              <b-spinner class="m-5"></b-spinner>
            </div>
            <div v-show="!loading && !firstLoad">
              <h6 v-if="artists.length == 0">No search results.</h6>
            </div>
            <b-card-body v-show="!loading" id="performers" class="card-body">
              <b-card-text class="info-card-text" @scroll="hideKeyboard">
                <div v-for="artist in artists" :key="artist.id" @click="artistSearch(artist)">
                  <table class="search-table">
                    <tr>
                      <td>
                        <b-avatar size="52px" :src="artist.img"></b-avatar>
                      </td>
                      <td class="info-td">
                        <a class="artist-link">{{ artist.name }}</a><br />
                        <span v-if="artist.description !== 'NA'" class="born-died">{{ artist.description }}</span>
                      </td>
                    </tr>
                  </table>
                </div>
              </b-card-text>
            </b-card-body>
          </b-card>
        </div>
      </Transition>
    </div>
  </div>
</template>


<script>
import { eventBus, staticURL } from "@/main.js";
import axios from "axios";

export default {
  data() {
    return {
      radioGrayURL: staticURL + "/assets/radio_gray.svg",
      radioWhiteUrl: staticURL + "/assets/radio.svg",
      spotifyGrayURL: staticURL + "/assets/Spotify_Icon_RGB_Gray.png",
      spotifyWhiteUrl: staticURL + "/assets/Spotify_Icon_RGB_White.png",
      hover: false,
      hover2: false,
      loading: false,
      img: "",
      spotifyUrl: "",
      omniSearchInput: null,
      viewSearchResults: false,
      artists: [],
      firstLoad: true,

      albumSortField: { value: "recommended", text: "Recommended sorting" },
      albumSortOptions: [
        { value: "recommended", text: "Recommended sorting" },
        { value: "dateascending", text: "Sort by date, earliest to latest" },
        { value: "datedescending", text: "Sort by date, latest to earliest" },
      ],
      albumSizeField: { value: this.$config.albumSize, text: this.capitalize(this.$config.albumSize) },
      albumSizeOptions: [
        { value: "large", text: "Large" },
        { value: "small", text: "Small" },
      ],

    };
  },
  methods: {
    hideKeyboard() {
      document.activeElement.blur();
    },
    omniSearch() {
      if (this.omniSearchInput !== "") {
        this.getOmniSearch(this.omniSearchInput);
      } else {
        this.resetField()
      }
    },
    getOmniSearch(item) {
      this.loading = true;
      this.viewSearchResults = true;
      this.firstLoad = false;
      this.artists = [];

      const path = "api/searchperformers?search=" + item;

      axios
        .get(path)
        .then((res) => {
          this.artists = res.data.artists;
          this.loading = false;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading = false;
          this.viewSearchResults = true;
          this.ajax_waiting = false;
        });
    },
    getArtist(artistId) {
      const path = "api/getperformer?id=" + artistId;

      axios
        .get(path)
        .then((res) => {
          this.$config.artist = res.data.artist;
          this.spotifyUrl = 'https://open.spotify.com/artist/' + res.data.artist.id;
          this.omniSearchInput = res.data.artist.name;
          eventBus.$emit("requestComposersForArtist", res.data.artist.id);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    onInputFocus() {
      this.omniSearchInput = "";
      this.resetField()
    },
    capitalize(string) {
      let capitalized = string[0].toUpperCase() + string.substring(1);
      return capitalized;
    },
    artistSearch(artist) {
      this.viewSearchResults = false;
      this.setArtist(artist);
    },
    resetField(input) {
      if (!input) {
        this.$router.push("/mobileperformers");
        eventBus.$emit("clearPerformers");
        this.$config.artist = null;
        this.firstLoad = true;
      }
    },
    albumFilter() {
      eventBus.$emit("requestAlbums", this.$config.work, this.$config.artist.name, this.albumSortField.value);
    },
    resetAlbumSort() {
      this.albumSortField = { value: "recommended", text: "Recommended sorting" };
    },
    setArtist(artist) {
      this.$config.composer = null;
      this.$config.artist = artist;
      this.omniSearchInput = artist.name;
      this.$router.push("/mobileperformers?artist=" + artist.id);
      eventBus.$emit("requestComposersForArtist", artist.id);
    },
    albumSize() {
      this.$config.albumSize = this.albumSizeField.value === "large" ? "large" : "small";
    },
    goToAristRadio(artist) {
      this.$config.artist = artist;
      this.$router.push("/radio?artist=" + artist);
    },
  },
  created() {
    this.$config.artist = null;
    if (this.$route.query.artist) {
      this.getArtist(this.$route.query.artist);
    }
    eventBus.$on("fireArtistAlbums", this.resetAlbumSort);
    eventBus.$on("requestPerformer", this.setArtist);
  },
  mounted() {
    const inputForm = document.getElementById("performer-search-form");

    const overlay = document.getElementById('performer-overlay');

    inputForm.addEventListener('click', () => {
      this.viewSearchResults = true;
      // overlay.style.display = 'block';
    });

    overlay.addEventListener('click', () => {
      this.viewSearchResults = false;
      //overlay.style.display = 'none';
    });

  },
  beforeDestroy() {
    eventBus.$off("fireArtistAlbums", this.resetAlbumSort);
    eventBus.$off("requestPerformer", this.setArtist);
  },
};
</script>

<style>
.form-control {
  background-color: var(--search-gray) !important;
  border: none !important;
  color: var(--my-white) !important;
}
::-webkit-input-placeholder {
  /* Chrome/Opera/Safari */
  color: #9ea4ae !important;
}
::-moz-placeholder {
  /* Firefox 19+ */
  color: #9ea4ae !important;
}
:-ms-input-placeholder {
  /* IE 10+ */
  color: #9ea4ae !important;
}
:-moz-placeholder {
  /* Firefox 18- */
  color: #9ea4ae !important;
}
</style>
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
  background: rgba(52, 58, 64, 1);
  z-index: 10;
}
.spinner {
  text-align: center;
  color: grey;
}
  .container-fluid {
  background-color: var(--medium-gray);
  color: var(--search-gray);
}
.vertical-centered{
  height: 78px;
  line-height: 78px;
  text-align: center;
}
.headings-table {
  display: inline-block;
  text-align: left;
  vertical-align: middle;
  line-height: normal;
  margin-bottom: 3px;
}
.dummy-table{
  padding: 20px;
  text-align: center !important;
  display: inline-block;
  vertical-align: middle;
  line-height: normal;
}
.artist-name{
  font-size: 20px;
  color: var(--my-white);
}
.artist-job{
  color: var(--medium-light-gray);
  font-size: 16px;
}
.wiki-link a{
  color: var(--medium-dark-gray);
  font-size: 12px;
  text-decoration: none;
}
.radio-link a{
  color: var(--medium-dark-gray) !important;
  font-size: 12px;
  text-decoration: none;
}
.radio-link >>> img, a:hover{
  color: var(--my-white) !important;
  cursor: pointer;
}
.wiki-link a:hover{
  color: var(--my-white);
  cursor: pointer;
}
.spotify-link-img{
  margin-bottom: 3px;
}
.no-results{
  font-size: 16px;
  color: var(--medium-light-gray);
}
.avatar{
  margin-right: 10px;
}
.last-col {
  margin-right: 5px;
}
.albums-card {
  padding-top: 5px !important;
}
.albums-card .card-body {
  background: none !important;
  height: 73px;
}
.card {
  background: none;
  border: none;
}
.heading-card {
  padding-top: 5px;
  padding-bottom: 0px;
  padding-left: 5px;
}
.form-row {
  margin-bottom: 0px;
}
.lead {
  font-weight: 500;
  font-size: 14px;
  margin: 0px;
  padding-left: 10px;
  padding-bottom: 1px;
}
.col {
  padding: 0px;
}
.select-box {
  margin-top: 5px !important;
  font-size: 14px;
  fill: white;
}
>>> .vs__selected-options{
  flex-wrap: nowrap;
}
>>> .vs__selected{
  white-space:nowrap;
  overflow: hidden;
}
>>> {
  --vs-search-input-bg: none;
  --vs-controls-color: var(--my-white);
  --vs-border-color: var(--search-gray);
  --vs-border-width: 1px;
  --vs-selected-bg: var(--search-gray);
  --vs-selected-color: var(--my-white);
  --vs-line-height: 1;
  --vs-search-input-color: var(--my-white);
}

#performer-search-form{
  margin-bottom: 5px;
}

#performer-search-results{
  position: absolute;
  top: calc(54.67px + 121px);
  z-index: 9999;
  width: 100%;
  background: none;
}
.spinner {
  text-align: center;
}
.m-5 {
    color: #9da6af;
}
.search-card {
  padding-left: 15px;
  padding-right: 15px;
  padding-top: 12px;
  padding-bottom: 10px;
  background-color: none !important;
  border: none !important;
}
.search-card >>> .card-body {
  background-color: none !important;
  --scroll-bar-bg-color: var(--light-gray);
}
.info-card-text {
  font-size: 13px;
  line-height: 130%;
  overflow-y: scroll;
  height: calc(var(--vh, 1vh) * 100 - 121px + 20px - var(--workingheight));
  padding-left: 2px;
}
.info-td {
  padding-left: 10px;
}
.born-died {
  font-size: 14px !important;
  color: var(--medium-dark-gray) !important;
}
.artist-link {
  color: white !important;
  font-weight: 600;
  font-size: 16px;
}
.artist-link:hover {
   text-decoration: none !important;
}

/*scrollbars*/
.info-card-text {
  --scroll-bar-color: var(--medium-dark-gray);
  --scroll-bar-bg-color: none;
}

.search-table {
  margin-bottom: 6px;
}
h6{
  color: white;
  padding-top: 5px;
}
/* clears the ‘X’ from Internet Explorer */
input[type=search]::-ms-clear { display: none; width : 0; height: 0; }
input[type=search]::-ms-reveal { display: none; width : 0; height: 0; }
/* clears the ‘X’ from Chrome */
input[type="search"]::-webkit-search-decoration,
input[type="search"]::-webkit-search-cancel-button,
input[type="search"]::-webkit-search-results-button,
input[type="search"]::-webkit-search-results-decoration { display: none; }
</style>
