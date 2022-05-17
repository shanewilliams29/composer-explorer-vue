<template>
  <div class="container-fluid">
    <b-row class="flex-nowrap">
      <b-col class="text-center">
        <div class="vertical-centered">
          <div class="spinner" v-show="loading" role="status">
            <b-spinner></b-spinner>
          </div>
          <div class="no-results" v-if="!results[0] && !loading"><table class="dummy-table">Search for a performer to view composers and works they perform</table></div>
            <table v-if="results && !loading">
              <tr class="tr-performer" v-for="result in results" :key="result[0]">
                <td>
                  <b-avatar class="avatar" size="64px" :src="result[2]"></b-avatar>
                </td>
                <td class="td-text">
                  <span class="artist-name">{{ result[0] }}&nbsp;</span><br>
                  <span class="artist-job">{{result[1]}}</span>
                  
                  <span v-if="wikiLink" class="wiki-link">&nbsp;&nbsp;<a :href="wikiLink" target="_blank"><b-icon icon="info-circle-fill" aria-hidden="true"></b-icon> Wikipedia</a>&nbsp;&nbsp;</span>
                  
                  <span @mouseover="hover = true" @mouseleave="hover = false" @click="goToAristRadio(result[0])" class="radio-link">
                    <img v-if="hover" :src="radioWhiteUrl" class="radio-link" height="14px" />
                    <img v-else :src="radioGrayURL" class="radio-link" height="14px" />
                    <a>&nbsp;Radio</a></span>
                </td>
              </tr>
            </table>
        </div>
      </b-col>
      <b-col class="last-col">
        <b-card class="heading-card albums-card">
          <b-form-group>
           <vue-typeahead-bootstrap v-model="query" placeholder="Search for a performer" class="mt-3 style-chooser performer-search" @input="resetField" @hit="artistSearch" size="sm" :data="this.artistList"/>
            <b-row class="flex-nowrap">
              <b-col style="padding-right: 0px;" cols="8">
                <v-select v-model="albumSortField" label="text" :options="albumSortOptions" @input="albumFilter()" :clearable="false" class="mt-3 style-chooser" :searchable="false"></v-select>
              </b-col>
              <b-col style="padding-left: 5px;" cols="4">
                <v-select v-model="albumSizeField" label="text" :options="albumSizeOptions" @input="albumSize()" :clearable="false" class="mt-3 style-chooser" :searchable="false"></v-select>
              </b-col>
            </b-row>
          </b-form-group>
        </b-card>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import axios from 'axios';
import {eventBus, staticURL} from "../main.js";

export default {
  data() {
    return {
      radioGrayURL: staticURL + 'radio_gray.svg',
      radioWhiteUrl: staticURL + 'radio.svg',
      hover: false,
      wikiLink: null,
      query: '',
      artistList: [],
      loading: false,

      albumSortField: { value: 'recommended', text: 'Recommended sorting' },
      albumSortOptions: [
          { value: 'recommended', text: 'Recommended sorting' },
          { value: 'dateascending', text: 'Sort by date, earliest to latest' },
          { value: 'datedescending', text: 'Sort by date, latest to earliest' }
        ],
      albumSizeField: { value: this.$config.albumSize, text: this.capitalize(this.$config.albumSize)},
      albumSizeOptions: [
          { value: 'large', text: 'Large' },
          { value: 'small', text: 'Small' }
        ],
      results: [],
    };
  },
  methods: {
    getArtistList() {
      const path = 'api/artistlist';
      axios.get(path)
        .then((res) => {
        this.artistList = JSON.parse(res.data.artists);
        })
        .catch((error) => {
          console.error(error);
        });
    },
    capitalize(string){
      let capitalized = string[0].toUpperCase() + string.substring(1);
      return capitalized;
    },
    artistSearch(artist){
      eventBus.$emit('fireArtistComposers', artist);
    },
    resetField(input){
      if(!input){
        this.$router.push('/performers');
        eventBus.$emit('clearPerformers');
        this.results =[];
      }
    },
    albumFilter() {
      eventBus.$emit('fireAlbums', this.$config.work, this.query, this.albumSortField.value);
    },
    resetAlbumSort(){
      this.albumSortField = { value: 'recommended', text: 'Recommended sorting' };
    },
    setArtistField(artist){
      this.getPersonInfo(artist);
      this.$router.push('/performers?artist=' + artist);
      this.query = artist;
    },
    albumSize() {
      if (this.albumSizeField.value == "large") {
        this.$config.albumSize = 'large';
        localStorage.setItem('config', JSON.stringify(this.$config));
      } else {
        this.$config.albumSize = 'small';
        localStorage.setItem('config', JSON.stringify(this.$config));
      }
    },
    goToAristRadio(artist) {
      this.$config.artist = artist;
      this.$router.push('/radio?artist=' + artist);
    },
    getPersonInfo(person) {
      this.loading = true;
      this.results = [];
      const key = localStorage.getItem("APIKey");
      const path = 'https://kgsearch.googleapis.com/v1/entities:search?indent=true&types=Person&types=MusicGroup&query=' + person + ' Music&limit=50&key=' + key;
      axios({
        method: 'get',
        url: path,
      }).then((res) => {
        this.loading = false;
        let imageUrl = '';
        let description = '';
        //this.loading = false;
        if (res.data.itemListElement[0] != null) {
          for (var i = 0; i < res.data.itemListElement.length; i++) {
            var personMatch = person.replace('Sir','').replace('Dame','').trim();
            if (res.data.itemListElement[i].result.name.includes(personMatch)) {
              let rank = 0
              if ('image' in res.data.itemListElement[i].result) {
                imageUrl = res.data.itemListElement[i].result.image.contentUrl;
                rank = rank + 1;
              } else {
                imageUrl = '';
              }
              if ('description' in res.data.itemListElement[i].result) {
                description = res.data.itemListElement[i].result.description;
                rank = rank + 1;
              } else {
                description = '';
              }
              if ('url' in res.data.itemListElement[i].result.detailedDescription) {
                this.wikiLink = res.data.itemListElement[i].result.detailedDescription.url;
                rank = rank + 1;
              } else {
                this.wikiLink = null;
              }
              this.results.push([person, description, imageUrl, rank]);
              break;
            }
            if (i == res.data.itemListElement.length - 1) {
              this.results.push([person, '', '', -1]);
              this.wikiLink = null;
            }
          }
        } else {
          this.wikiLink = null;
          this.results.push([person, '', '', -1]);
        }
      }).catch((error) => {
        console.error(error);
          this.wikiLink = null;
          this.results.push([person, '', '', -1]);
          this.loading = false;
      });
    },
  },
  created() {
    this.$config.artist = null;
    this.getArtistList();
    if (this.$route.query.artist){
      this.artistSearch(this.$route.query.artist);
      this.getPersonInfo(this.$route.query.artist);
      this.query = this.$route.query.artist;
      this.$config.artist = this.$route.query.artist;
    }
    eventBus.$on('fireArtistAlbums', this.resetAlbumSort);
    eventBus.$on('fireArtistComposers', this.setArtistField);
  },
  beforeDestroy(){
    eventBus.$off('fireArtistAlbums', this.resetAlbumSort);
    eventBus.$off('fireArtistComposers', this.setArtistField);
  },
};
</script>

<style>
.form-control {
  background-color: #3b4047 !important;
  border: none !important;
  color: white !important;
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
  background-color: #54595f;
  color: #3b4047;
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
  color: white;
}
.artist-job{
  color: lightgray;
  font-size: 16px;
}
.wiki-link a{
  color: darkgray;
  font-size: 12px;
  text-decoration: none;
}
.radio-link a{
  color: darkgray !important;
  font-size: 12px;
  text-decoration: none;
}
.radio-link a:hover{
  color: white !important;
  cursor: pointer;
}
.wiki-link a:hover{
  color: white;
  cursor: pointer;
}
.no-results{
  font-size: 16px;
  color: lightgray;
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
.style-chooser {
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
  --vs-controls-color: #fff;
  --vs-border-color: #3b4047;
  --vs-border-width: 1px;
  --vs-selected-bg: #3b4047;
  --vs-selected-color: #fff;
  --vs-line-height: 1;
  --vs-search-input-color: #fff;
}
.performer-search {
  margin-top: 1.3px !important;
  font-size: 14px;
  background-color: #3b4047 !important;
  height: 31px;
  border: none;
  border-radius: 4px;
}
</style>
