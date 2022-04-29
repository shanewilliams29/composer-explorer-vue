<template>
  <div>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
    <div class="row">
      <span v-show="!loading && albums.length < 1 && !radioMode" class="m-4 col no-albums-found">
        No albums found.
      </span>
    </div>
    <div v-if="albums">
      <div class="row">
        <b-card-group deck v-show="!loading">
          <LargeAlbum v-if="$userSettings.albumSize == 'large'" v-bind:albums="albums" v-bind:selectedAlbum="selectedAlbum"/>
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
import {currentConfig} from "../main.js";

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
      radioMode: false,
      page: 2,
      workId: '',
      artistName: '',
      sort: '',
      infiniteId: +new Date(),
      albumView: currentConfig.albumView
    };
  },
  methods: {
    // loads from selected work
    getAlbums(id) {
      this.changeAlbums()
      this.workId = id;
      this.loading = true;
      const path = 'api/albums/' + id;
      axios.get(path).then((res) => {
        this.albums = res.data.albums;
        this.loading = false;
        this.selectRow(this.albums[0].id); // select first row on work selection
        currentConfig.album = this.albums[0].id;
        localStorage.setItem('currentConfig', JSON.stringify(currentConfig));
        eventBus.$emit('fireArtistList', res.data.artists);
        eventBus.$emit('fireAlbumData', this.albums[0].id);
      }).catch((error) => {
        console.error(error);
        this.loading = false;
      });
    },
    // loads from localstorage on initial startup
    initialGetAlbums(id) {
      this.changeAlbums()
      this.workId = id;
      this.loading = true;
      const path = 'api/albums/' + id;
      axios.get(path).then((res) => {
        this.albums = res.data.albums;
        eventBus.artists = res.data.artists;
        this.loading = false;
        this.selectRow(currentConfig.album);
        eventBus.$emit('fireAlbumData', currentConfig.album);
        eventBus.$emit('fireArtistList', res.data.artists);
      }).catch((error) => {
        console.error(error);
        this.loading = false;
      });
    },
    getAlbumData(albumId) {
      eventBus.$emit('fireAlbumData', albumId);
      currentConfig.album = albumId;
      localStorage.setItem('currentConfig', JSON.stringify(currentConfig));
    },
    selectRow(album) {
      this.selectedAlbum = album;
    },
    getFilteredAlbums(id, item, sort) {
      this.changeAlbums()
      this.workId = id;
      this.artistName = item;
      this.sort = sort;
      this.loading = true;
      const path = 'api/albums/' + id + '?artist=' + item + '&sort=' + sort;
      axios.get(path).then((res) => {
        this.albums = res.data.albums;
        this.loading = false;
      }).catch((error) => {
        console.error(error);
        this.loading = false;
      });
    },
    infiniteHandler($state) {
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
    },
    changeAlbums() {
      this.artistName = '';
      this.sort = '';
      this.page = 2;
      this.albums = [];
      this.infiniteId += 1;
    },
    setAlbumView(view) {
      this.albumView = view;
      currentConfig.albumView = view;
      localStorage.setItem('currentConfig', JSON.stringify(currentConfig));
    },
  },
  created() {
    if (window.location.href.indexOf("radio") != -1) { // dont get works in radio mode
      this.radioMode = true;
    } else {
      this.initialGetAlbums(currentConfig.work);
    }
    eventBus.$on('fireAlbums', this.getAlbums);
    eventBus.$on('fireAlbumFilter', this.getFilteredAlbums);
    eventBus.$on('fireArtistAlbums', this.getFilteredAlbums);
    // eventBus.$on('fireAlbumView', this.setAlbumView);
  },
  beforeDestroy() {
    eventBus.$off('fireAlbums', this.getAlbums);
    eventBus.$off('fireAlbumFilter', this.getFilteredAlbums);
    eventBus.$off('fireArtistAlbums', this.getFilteredAlbums);
    // eventBus.$off('fireAlbumView', this.setAlbumView);
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
