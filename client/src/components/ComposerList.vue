<template>
  <div>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
    <div class="row">
      <span class="m-4 col no-composers-found" v-show="!loading && composers.length < 1 && !$view.mode">No composers found.</span>
      <b-card-group deck v-show="!loading">
        <b-card v-for="(region, index) in composers" :key="index" no-body header-tag="header" class="shadow-sm">
          <div class="#header" v-b-toggle="index.replace(/\s/g, '')">
            <h6 class="m-2 mb-0">
              {{ index }}<span class="mb-0 float-right when-opened"><b-icon-chevron-up></b-icon-chevron-up></span><span class="mb-0 float-right when-closed"><b-icon-chevron-down></b-icon-chevron-down></span>
            </h6>
          </div>
          <b-collapse :visible="visibility" :id="index.replace(/\s/g, '')">
            <b-card-text>
              <table cellspacing="0">
                <tr v-for="composer in region" :key="composer.id" @click="selectRow(composer.id); getWorks(composer.name_short);" :class="{'highlight': (composer.id == selectedComposer)}">
                  <td width="2%" :style="{border: 'solid 0px !important', backgroundColor:composer.color, opacity: 0.66}"></td>
                  <td width="2%"></td>
                  <td width="12%" style="white-space: nowrap;">
                    <img class="composer-img" :src="composer.flag" height="20" width="20" />
                    <img class="composer-img" :src="composer.img" height="20" width="20" />
                  </td>
                  <td width="50%" style="white-space: nowrap; text-overflow: ellipsis; overflow: hidden; max-width: 1px;">
                    {{ composer.name_full }}
                  </td>
                  <td width="25%" style="white-space: nowrap; text-overflow: ellipsis; max-width: 1px; text-align: right;">
                    {{ composer.born }} - {{ composer.died }}
                  </td>
                </tr>
              </table>
            </b-card-text>
          </b-collapse>
        </b-card>
      </b-card-group>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import {eventBus} from "../main.js";


export default {
  data() {
    return {
      composers: [],
      loading: false,
      selectedComposer: null,
      visibility: true,
      artist: "",
    };
  },
  methods: {
    getComposers() {
      this.loading = true;
      const path = 'api/composers';
      axios.get(path)
        .then((res) => {
          this.composers = res.data.composers;
          this.loading=false;
          this.visibility=true;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading=false;
        });
    },
    getFilteredComposers(item) {
      this.loading = true;
      if (item == "all" || item == "alphabet" || item == "romantic" || item == "20th" || item == "common") {
        this.visibility=false;
      } else {
        this.visibility=true;
      }
      const path = 'api/composers?filter=' + item;
      axios.get(path)
        .then((res) => {
          this.composers = res.data.composers;
          this.loading=false;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading=false;
        });
    },
    getSearchComposers(item) {
      this.visibility=true
      const path = 'api/composers?search=' + item;
      axios.get(path)
        .then((res) => {
          this.composers = res.data.composers;
          this.loading=false;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading=false;
        });
    },
    getArtistComposers(artist) {
      this.artist = artist
      this.loading = true;
      this.visibility=true;
      this.selectedComposer = null;
      eventBus.$emit('fireClearWorks', artist);
      const path = 'api/artistcomposers/' + artist;
      axios.get(path)
        .then((res) => {
          this.composers = res.data.composers;
          this.loading=false;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading=false;
        });
    },
    getWorks(composer) {
      if (!this.$view.mode){
        eventBus.$emit('fireComposers', composer);
      } else if (this.$view.mode == 'performer'){
        eventBus.$emit('fireArtistWorks', this.artist, composer);
      }
    },
    selectRow(composerId){
      if (this.$view.mode != 'radio'){
        this.selectedComposer = composerId;
        this.$config.composerId = composerId;
        localStorage.setItem('config', JSON.stringify(this.$config));
      }
    },
    fireRadioSelect(type){
      if(type == "composer"){
      const path = 'api/composersradio';
      axios.get(path)
        .then((res) => {
          eventBus.$emit('fireComposerListToRadio', res.data.composers);
          this.composers = [];
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
      }
    },
    getMultiComposers(composers) {
      if (composers.length < 1){
        this.composers = []
      }
      else{
      const path = 'api/multicomposers';
      axios.post(path, composers)
        .then((res) => {
          this.composers = res.data.composers;
          eventBus.$emit('fireRadioGenreList', res.data.genres);
          this.visibility=true;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
      }
    }
  },
  created() {
    if (!this.$view.mode){ // dont get composers in performer or radio modes
      this.getComposers();
      this.selectRow(this.$config.composerId);
    }
    if (this.$route.query.artist){
      this.getArtistComposers(this.$route.query.artist);
    }

    eventBus.$on('fireComposerFilter', this.getFilteredComposers);
    eventBus.$on('fireComposerSearch', this.getSearchComposers);
    eventBus.$on('fireArtistComposers', this.getArtistComposers);
    eventBus.$on('fireRadioSelect', this.fireRadioSelect);
    eventBus.$on('fireComposerSelectRadio', this.getMultiComposers);
  },
  beforeDestroy() {
    eventBus.$off('fireComposerFilter', this.getFilteredComposers);
    eventBus.$off('fireComposerSearch', this.getSearchComposers);
    eventBus.$off('fireArtistComposers', this.getArtistComposers);
    eventBus.$off('fireRadioSelect', this.fireRadioSelect);
    eventBus.$off('fireComposerSelectRadio', this.getMultiComposers);
  }
};
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.collapsed .when-closed{
  display: show;
}
.collapsed .when-opened{
  display: none;
}
.not-collapsed .when-closed{
  display: none;
}
.not-collapsed .when-opened{
  display: show;
}
.card-deck {
  display: flex;
  flex-direction: column;
  width: 100%;
}
.card {
  width: 100%;
}
td {
  padding: 1px;
  vertical-align: middle;
  border-top: 1px dotted lightgray;
}
tr {
  border-bottom: 0px;
}
table {
  width: 100%;
  border-collapse: separate;
  font-size: 13px;
  padding: 6px;
  padding-top: 0px;
  padding-bottom: 2px;
}
.highlight td {
  border-top: 0px solid lightgray;
  background-color: #007bff;
  color: white;
}
tr:hover {
  cursor: pointer;
}
.highlight td:last-child {
  position: relative;
}

.highlight td:last-child:after {
  content: "";
  position: absolute;
  top: 0px;
  bottom: 0px;
  width: 6px;
  display: block;
  background: inherit;
  border: inherit;
  left: 100%;
}
.composer-img {
  border-radius: 50%;
  object-fit: cover;
}
header.card-header {
  background-color: #fff;
  border: none;
  padding-left: 10px;
  padding-bottom: 0px;
}
header.card-header:hover {
  cursor: pointer;
}
.mb-0 {
  font-size: 14px;
  font-weight: bold;
}
.spinner {
  text-align: center;
}
.m-5 {
  color: #343a40;
}
.card {
  background-color: #fff;
  border: none;
  margin-top: 5px;
}
.card-deck {
  padding-left: 5px;
  padding-right: 5px;
}
.no-composers-found {
  font-size: 14px;
  color: grey;
  text-align: center;
}
</style>
