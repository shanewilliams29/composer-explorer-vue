<template>
  <div class="container-fluid">
    <b-row class="flex-nowrap">
      <b-col class="text-center">
        <div class="vertical-centered">
          <div class="no-results" v-if="!results[0]">
            <table class="dummy-table">
              Search for a performer to view composers and works they perform
            </table>
          </div>
          <table v-if="results">
            <tr class="tr-performer" v-for="result in results" :key="result[0]">
              <td>
                <b-avatar class="avatar" size="64px" :src="img"></b-avatar>
              </td>
              <td class="td-text">
                <span class="artist-name">{{ result[0] }}&nbsp;</span><br />
                <span class="artist-job">{{result[1]}}</span>

                <span v-if="result[4]" class="wiki-link">
                  &nbsp;&nbsp;<a :href="result[4]" target="_blank">
                    <b-icon icon="info-circle-fill" aria-hidden="true"></b-icon> Wikipedia</a>&nbsp;&nbsp;
                </span>

                <span 
                  @mouseover="hover = true" 
                  @mouseleave="hover = false" 
                  @click="goToAristRadio(result[0])" 
                  class="radio-link">
                  <img v-if="hover" :src="radioWhiteUrl" class="radio-link-img" height="14px" />
                  <img v-else :src="radioGrayURL" class="radio-link-img" height="14px" />
                  <a>&nbsp;Radio</a>
                </span>
              </td>
            </tr>
          </table>
        </div>
      </b-col>
      <b-col class="last-col">
        <b-card class="heading-card albums-card">
          <b-form-group>
            <vue-typeahead-bootstrap 
              v-show="$lists.artistList.length < 1" 
              v-model="query" 
              placeholder="Loading..." 
              class="mt-3 select-box performer-search" 
              size="sm" 
              :data="[]"/>
            <vue-typeahead-bootstrap 
              v-show="$lists.artistList.length > 0" 
              v-model="query" 
              placeholder="Search for a performer" 
              class="mt-3 select-box performer-search" 
              @input="resetField" 
              @hit="artistSearch" 
              size="sm" 
              :data="$lists.artistList" />
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
</template>


<script>
import { eventBus, staticURL } from "@/main.js";
import { getArtistDetails } from "@/HelperFunctions.js" 

export default {
  data() {
    return {
      radioGrayURL: staticURL + "radio_gray.svg",
      radioWhiteUrl: staticURL + "radio.svg",
      hover: false,
      wikiLink: null,
      query: "",
      listLoading: false,

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
      results: [],
      img: ""
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
  watch: {
    apiKeyGot() {
      if (this.$route.query.artist) {
        this.results = []
        let artistDict = {name: this.$route.query.artist, img: "NA"};
        getArtistDetails(artistDict, this.results, this.$auth.knowledgeKey);
      }
    },
    artistDictGot() {
      if (this.$route.query.artist) { 
        this.getArtistPic(this.$route.query.artist);
      }
    },
  },
  methods: {
    getArtistPic(artistName){
         for (let i = 0; i < this.$lists.artistDict.length; i++) {
            let artist = this.$lists.artistDict[i];
            if (artist.name == artistName){
              this.img = artist.img
              break;
            }
          }
      },
    capitalize(string) {
      let capitalized = string[0].toUpperCase() + string.substring(1);
      return capitalized;
    },
    artistSearch(artist) {
      this.getArtistPic(artist);
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
      eventBus.$emit("requestAlbums", this.$config.work, this.query, this.albumSortField.value);
    },
    resetAlbumSort() {
      this.albumSortField = { value: "recommended", text: "Recommended sorting" };
    },
    setArtistField(artist) {
      this.results = [];
      this.getArtistPic(artist);
      let artistDict = {name: artist, img: "NA"};
      getArtistDetails(artistDict, this.results, this.$auth.knowledgeKey);
      this.$router.push("/performers?artist=" + artist);
      this.query = artist;
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
      this.query = this.$route.query.artist;
      this.$config.artist = this.$route.query.artist;
      if (this.$auth.knowledgeKey) {
        let artistDict = {name: this.$route.query.artist, img: "NA"};
        getArtistDetails(artistDict, this.results, this.$auth.knowledgeKey);
      }
    }
    eventBus.$on("fireArtistAlbums", this.resetAlbumSort);
    eventBus.$on("requestComposersForArtist", this.setArtistField);
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
</style><style scoped>
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
table {
  display: inline-block;
  text-align: left;
  vertical-align: middle;
  line-height: normal;
  margin-bottom: 3px;
}
.dummy-table{
  padding: 20px;
  text-align: center !important;
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
.card-body {
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
.performer-search {
  margin-top: 1.3px !important;
  font-size: 14px;
  background-color: var(--search-gray) !important;
  height: 31px;
  border: none;
  border-radius: 4px;
}
</style>
