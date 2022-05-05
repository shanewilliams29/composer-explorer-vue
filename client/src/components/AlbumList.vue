<template>
  <div>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
    <div class="row">
      <span v-show="!loading && albums.length < 1 && !this.$view.mode" class="m-4 col no-albums-found">
        No albums found.
      </span>
    </div>
    <div v-if="albums">
      <div class="row">
        <b-card-group deck v-show="!loading">
          <LargeAlbum v-if="$config.albumSize == 'large'" v-bind:albums="albums" v-bind:selectedAlbum="selectedAlbum"/>
          <SmallAlbum v-else v-bind:albums="albums" v-bind:selectedAlbum="selectedAlbum"/>
          <infinite-loading spinner="spiral" :identifier="infiniteId" @infinite="infiniteHandler">
            <div slot="no-more"></div>
            <div slot="no-results"></div>
          </infinite-loading>
        </b-card-group>
      </div>
    </div>
  </div>
</template>

<script>
import LargeAlbum from '@/components/subcomponents/LargeAlbum.vue';
import SmallAlbum from '@/components/subcomponents/SmallAlbum.vue';
import axios from 'axios';
import {eventBus} from "../main.js";

export default {
  components: {
    LargeAlbum,
    SmallAlbum
  },
  data() {
    return {
      albums: [],
      loading: false,
      selectedAlbum: null,
      page: 2,
      workId: '',
      artistName: '',
      sort: '',
      infiniteId: +new Date()
    };
  },
  methods: {
    getAlbums(id, artist, sort) {
      this.changeAlbums();
      this.workId = id;
      if(artist){
        this.artistName = artist;
      } else {
        artist = '';
      }
      if(sort){
        this.sort = sort
      } else {
        sort = '';
      }
      this.loading = true;
      const path = 'api/albums/' + id + '?artist=' + artist + '&sort=' + sort;
      axios.get(path).then((res) => {
        this.$config.composer = res.data.composer;
        localStorage.setItem('config', JSON.stringify(this.$config));
        this.albums = res.data.albums;
        eventBus.$emit('fireArtistList', res.data.artists);
        this.loading = false;
      }).catch((error) => {
        console.error(error);
        this.loading = false;
      });
    },
    // gets albums and begins playback of first (for next and previous buttons)
    // used in Autoplay and the radio
    getAlbumsAndPlay(id, artist, sort) {

      function randomIntFromInterval(min, max) { // min and max included
          return Math.floor(Math.random() * (max - min + 1) + min)
      }

      this.changeAlbums()
      this.workId = id;
      if(artist){
        this.artistName = artist;
      } else {
        artist = '';
      }
      if(sort){
        this.sort = sort
      } else {
        sort = '';
      }
      this.loading = true;

      var path = '';
      if (this.$view.mode == 'radio'){
        var limit = this.$view.radioTrackLimit;
        path = 'api/albums/' + id + '?artist=' + artist + '&sort=' + sort + '&limit=' + limit;
      } else {
        path = 'api/albums/' + id + '?artist=' + artist + '&sort=' + sort;
      }
      axios.get(path).then((res) => {
        if(this.$view.mode == 'radio'){ // only one album in radiomode
          if(this.$view.randomAlbum){

              const rndInt = randomIntFromInterval(0, res.data.albums.length - 1)
              this.albums = [res.data.albums[rndInt]];
          } else {
              this.albums = [res.data.albums[0]];
            }
        } else {
          this.albums = res.data.albums;
        }
        this.loading = false;
        this.selectRow(this.albums[0].id); // select first row on work selection
        this.$config.album = this.albums[0].id;
        this.$config.composer = res.data.composer;
        localStorage.setItem('config', JSON.stringify(this.$config));
        eventBus.$emit('fireArtistList', res.data.artists);
        eventBus.$emit('fireAlbumData', this.albums[0].id);
      }).catch((error) => {
        console.error(error);
        this.loading = false;
      });
    },
    // loads from localstorage on initial startup
    initialGetAlbums(id) {
      this.changeAlbums();
      this.workId = id;
      this.loading = true;
      const path = 'api/albums/' + id;
      axios.get(path).then((res) => {
        this.albums = res.data.albums;
        eventBus.artists = res.data.artists;
        this.loading = false;
        this.selectRow(this.$config.album);
        eventBus.$emit('fireAlbumData', this.$config.album);
        eventBus.$emit('fireArtistList', res.data.artists);
      }).catch((error) => {
        console.error(error);
        this.loading = false;
      });
    },
    getAlbumData(albumId) {
      eventBus.$emit('fireAlbumData', albumId);
      this.$config.album = albumId;
      localStorage.setItem('config', JSON.stringify(this.$config));
    },
    selectRow(album) {
      this.selectedAlbum = album;
    },
    clearAlbums() {
      this.albums = [];
    },
    infiniteHandler($state) {
      if(this.$view.mode){
        $state.complete();
      } else {
      const path = 'api/albums/' + this.workId + '?artist=' + this.artistName + '&sort=' + this.sort + '&page=' + this.page;
        axios.get(path).then(({data}) => {
          if (data.albums.length) {
            this.page += 1;
            this.albums.push(...data.albums);
            $state.loaded();
          } else {
            $state.complete();
          }
        });
      }
    },
    changeAlbums() {
      this.artistName = '';
      this.sort = '';
      this.page = 2;
      this.albums = [];
      this.infiniteId += 1;
    },
  },
  created() {
    if (!this.$view.mode) { // dont get albums in radio or performer mode
      this.initialGetAlbums(this.$config.work);
    }
    eventBus.$on('fireAlbums', this.getAlbums);
    eventBus.$on('fireAlbumsAndPlay', this.getAlbumsAndPlay);
    eventBus.$on('fireClearAlbums', this.clearAlbums);
  },
  beforeDestroy() {
    eventBus.$off('fireAlbums', this.getAlbums);
    eventBus.$off('fireAlbumsAndPlay', this.getAlbumsAndPlay);
    eventBus.$off('fireClearAlbums', this.clearAlbums);
  }
};
</script>

<style scoped>
.spinner {
  text-align: center;
}
.m-5 {
  color: #343a40;
}
.card-deck {
  display: flex;
  flex-direction: column;
  width: 100%;
  padding-left: 5px;
  padding-right: 5px;
}
.no-albums-found {
  font-size: 14px;
  color: grey;
  text-align: center;
}
</style>
