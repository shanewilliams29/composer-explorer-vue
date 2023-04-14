<template>
<div>
  <div class="container-fluid">
    <b-row class="flex-nowrap">
      <b-col class="text-center">
        <div class="vertical-centered">
          <div class="no-results" v-if="!results[0]">
            <table class="dummy-table">
              Search for a performer to view composers and works they perform
            </table>
          </div>
          <table  class="headings-table" v-if="results">
            <tr class="tr-performer" v-for="result in results" :key="result[0]">
              <td>
                <b-avatar class="avatar" size="64px" :src="img"></b-avatar>
              </td>
              <td class="td-text">
                <span class="artist-name">{{ result[0] }}&nbsp;</span><br />
                <span class="artist-job">{{ result[1] }}</span>

                <span v-if="result[4]" class="wiki-link">
                  &nbsp;&nbsp;<a :href="result[4]" target="_blank">
                    <b-icon icon="info-circle-fill" aria-hidden="true"></b-icon> Wikipedia</a>
                </span>

                <span 
                  @mouseover="hover = true" 
                  @mouseleave="hover = false" 
                  @click="goToAristRadio(result[0])" 
                  class="radio-link"><a>&nbsp;&nbsp;
                  <img v-if="hover" :src="radioWhiteUrl" class="radio-link-img" height="14px" />
                  <img v-else :src="radioGrayURL" class="radio-link-img" height="14px" />
                  &nbsp;Radio</a>
                </span>

                <span class="radio-link"
                  @mouseover="hover2 = true" 
                  @mouseleave="hover2 = false" >&nbsp;&nbsp;
                  <a :href="spotifyUrl" target="_blank">
                  <img v-if="hover2" :src="spotifyWhiteUrl" class="spotify-link-img" height="14px" />
                  <img v-else :src="spotifyGrayURL" class="spotify-link-img" height="14px" />
                  Spotify</a>
                </span>
              </td>
            </tr>
          </table>
        </div>
      </b-col>
      <b-col class="last-col">
        <b-card class="heading-card albums-card">
          <b-form-group>
              <b-form-input id="performer-search-form" class="omnisearch" size="sm" v-model="omniSearchInput" v-debounce:0ms="omniSearch" @focus="onInputFocus()" type="search" placeholder="Search for a performer" autocomplete="off"></b-form-input>
            <b-row class="flex-nowrap">
              <b-col style="padding-right: 0px;" cols="8">
                <v-select 
                  v-model="albumSortField" 
                  label="text" 
                  :options="albumSortOptions" 
                  @input="albumFilter()" 
                  :clearable="false" 
                  class="mt-3 select-box" 
                  :searchable="false">
                  </v-select>
              </b-col>
              <b-col style="padding-left: 5px;" cols="4">
                <v-select 
                  v-model="albumSizeField" 
                  label="text" 
                  :options="albumSizeOptions" 
                  @input="albumSize()" 
                  :clearable="false" 
                  class="mt-3 select-box" 
                  :searchable="false">
                </v-select>
              </b-col>
            </b-row>
          </b-form-group>
        </b-card>
      </b-col>
    </b-row>
  </div>
  <div>
 <Transition name="fade">
      <div v-show="viewSearchResults && !firstLoad" class="overlay" id="performer-overlay"></div>
    </Transition>

    <Transition name="fade">
    <div id="performer-search-results" v-show="viewSearchResults && !firstLoad">
      <b-card class="search-card shadow-sm">

        <div class="spinner" v-show="loading" role="status">
        <b-spinner class="m-5"></b-spinner>
        </div>

          <div v-show="!loading && !firstLoad">
            <h6 v-if="searchresults.length == 0">No search results.</h6>
          </div>

        <b-card-body v-show="!loading" id="performers" class="card-body">
          <b-card-text class="info-card-text">
            <div v-for="result in searchresults" :key="result[0]">
              <table class="search-table">
                <tr>
                  <td>
                    <b-avatar size="40px" :src="result[2]"></b-avatar>
                  </td>
                  <td class="info-td">
                    <a class="artist-link" @click="artistSearch(result[0])">{{ result[0] }}</a><br />
                    <span class="born-died">{{ result[1] }}</span>
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
import { getArtistDetails } from "@/HelperFunctions.js" 

export default {
  data() {
    return {
      radioGrayURL: staticURL + "radio_gray.svg",
      radioWhiteUrl: staticURL + "radio.svg",
      spotifyGrayURL: staticURL + "Spotify_Icon_RGB_Black.png",
      spotifyWhiteUrl: staticURL + "Spotify_Icon_RGB_White.png",
      hover: false,
      hover2: false,
      wikiLink: null,
      query: "",
      loading: false,
      results: [],
      img: "",
      spotifyUrl: "",
      omniSearchInput: null,
      viewSearchResults: false,
      searchresults: [],
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
  computed: {
    apiKeyGot() {
      return this.$auth.knowledgeKey;
    },
  artistDictGot() {
      return this.$lists.artistDict;
    },
  },
  searchInput() {
    return this.omniSearchInput;
  },
  watch: {
    apiKeyGot() {
      if (this.$route.query.artist) {
        this.getArtistPicAndJob(this.$route.query.artist);
      }
    },
    artistDictGot() {
      if (this.$route.query.artist) { 
        this.getArtistPicAndJob(this.$route.query.artist);
      }
    },
    searchInput(searchInput) {
      if (searchInput == ""){
        this.viewSearchResults = false;
      }
    },
    searchresults: {
      handler: function () {
        // turn off loading when people results array is fully populated
        if (this.searchresults.length == this.artists.length && this.artists.length > 0){
          this.loading = false;
        }
      },
      deep: true
    }
  },
  methods: {
    omniSearch() {
      if (this.omniSearchInput !== ""){
        this.getOmniSearch(this.omniSearchInput);
      } else {
        //this.viewSearchResults = false;
      }
    },
    getOmniSearch(item) {
      this.loading = true;
      this.viewSearchResults = true;
      this.firstLoad = false;
      this.searchresults = [];
      this.artists = [];

      function removeAccents(text) {
        return text.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      }

      let i = 0;
      let pattern = new RegExp("\\b" + item.toLowerCase() + "\\w*");

      for (let artist of this.$lists.artistDict) {
        let match = pattern.exec(removeAccents(artist.name.toLowerCase()));
        if (match) {
            this.artists.push(artist);
          i++;
        }
        if (i > 10) {
          break;
        }
      }

      if (this.artists.length < 1){
        this.loading = false;
      }

      this.artists.forEach((element) => getArtistDetails(element, this.searchresults, this.$auth.knowledgeKey));
    },
    onInputFocus() {
      this.omniSearchInput = "";
    },
    getArtistPicAndJob(artistName){ // improve,use dictonary instead of list?
        this.results = []
         for (let i = 0; i < this.$lists.artistDict.length; i++) {
            let artist = this.$lists.artistDict[i];
            if (artist.name == artistName){
              this.spotifyUrl = 'https://open.spotify.com/artist/' + artist.id;
              this.img = artist.img
              getArtistDetails(artist, this.results, this.$auth.knowledgeKey);
              break;
            }
          }
      },
    capitalize(string) {
      let capitalized = string[0].toUpperCase() + string.substring(1);
      return capitalized;
    },
    artistSearch(artist) {
      this.viewSearchResults = false;
      this.getArtistPicAndJob(artist);
      eventBus.$emit("requestComposersForArtist", artist);
    },
    resetField(input) {
      if (!input) {
        this.$router.push("/performers");
        eventBus.$emit("clearPerformers");
        this.results = [];
      }
    },
    albumFilter() {
      eventBus.$emit("requestAlbums", this.$config.work, this.omniSearchInput, this.albumSortField.value);
    },
    resetAlbumSort() {
      this.albumSortField = { value: "recommended", text: "Recommended sorting" };
    },
    setArtistField(artist) {
      this.getArtistPicAndJob(artist);
      this.$router.push("/performers?artist=" + artist);
      this.omniSearchInput = artist;
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
      this.artistSearch(this.$route.query.artist);
      this.omniSearchInput = this.$route.query.artist;
      this.$config.artist = this.$route.query.artist;
    }
    eventBus.$on("fireArtistAlbums", this.resetAlbumSort);
    eventBus.$on("requestComposersForArtist", this.setArtistField);
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
    eventBus.$off("requestComposersForArtist", this.setArtistField);
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
  background: rgba(52, 58, 64, 0.5);
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
  margin-bottom: 3px;
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
  padding-top: 3.5px !important;
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
  padding-bottom: 2px;
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



#performer-search-results{
  position: absolute;
  top: calc(60px + 50px);
  right: 5px;
  z-index: 9999;
  width: calc(450px - 5px);
  box-shadow: rgba(0, 0, 0, 0.07) 0px 1px 2px, rgba(0, 0, 0, 0.07) 0px 2px 4px, rgba(0, 0, 0, 0.07) 0px 4px 8px, rgba(0, 0, 0, 0.07) 0px 8px 16px, rgba(0, 0, 0, 0.07) 0px 16px 32px, rgba(0, 0, 0, 0.07) 0px 32px 64px;
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
  padding-top: 8px;
  padding-bottom: 10px;
  background-color: var(--my-white) !important;
  border: none !important;
}
.search-card >>> .card-body {
  background-color: var(--my-white) !important;
  --scroll-bar-bg-color: var(--light-gray);
}
.info-card-text {
  font-size: 13px;
  line-height: 130%;
  overflow-y: scroll;
  max-height: 380px;
  padding-left: 2px;
}
.info-td {
  padding-left: 10px;
}
.born-died {
  font-size: 13px !important;
  color: grey !important;
}
.artist-link {
  color: black !important;
  font-weight: 600;
  font-size: 14px;
}
.artist-link:hover {
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

.search-table {
  margin-bottom: 6px;
}
h6{
  padding-top: 5px;
}
</style>
