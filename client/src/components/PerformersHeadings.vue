<template>
  <div class="container-fluid">
    <b-row>
      <b-col>
      </b-col>
      <b-col>
      </b-col>
      <b-col class="last-col">
        <b-card class="heading-card albums-card">
          <b-form-group>
           <vue-typeahead-bootstrap v-model="query" placeholder="Search for a performer" class="mt-3 style-chooser performer-search" @hit="artistSearch" size="sm" :data="this.artistList"/>
            <b-row>
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
import {eventBus} from "../main.js";

export default {
  data() {
    return {
      query: '',
      artistList: [],

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
    albumFilter() {
      eventBus.$emit('fireAlbumFilter', this.$config.work, this.query, this.albumSortField.value);
    },
    resetAlbumSort(){
      this.albumSortField = { value: 'recommended', text: 'Recommended sorting' };
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
  },
  created() {
    this.getArtistList();
    if (this.$route.query.artist){
      this.query = this.$route.query.artist;
    }
    eventBus.$on('fireArtistAlbums', this.resetAlbumSort);
  },
  beforeDestroy(){
    eventBus.$off('fireArtistAlbums', this.resetAlbumSort);
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
</style><style scoped>.container-fluid {
  background-color: #54595f;
  color: #3b4047;
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
