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
          <b-card
            v-for="album in albums"
            :key="album.id"
            :id="album.id"
            no-body
            header-tag="header"
            @click="selectRow(album.id); getAlbumData(album.id);"
            :class="{'highlight': (album.id == selectedAlbum)}"
          >
            <div class="row">
              <b-col class="album_columns" cols="2">
                <img
                  rounded="left"
                  width="48px"
                  height="48px"
                  v-lazy="album.album_img"
                >
 <!--                <b-avatar
                  v-show="album.id == selectedAlbum"
                  variant="dark"
                  icon="heart"
                  rounded="left"
                  size="48px"
                ></b-avatar> -->
              </b-col>
              <b-col class="album_text_columns">
                <b-card-text>
                  <table cellspacing="0">
                    <tr>
                      <td
                        width="100%"
                        style="
                          white-space: nowrap;
                          text-overflow: ellipsis;
                          overflow: hidden;
                          max-width: 1px;
                        "
                      >
                        <span style="color: black; font-weight: 600"
                          >{{ album.artists }} ({{ album.release_date }})</span
                        >
                      </td>
                    </tr>
                    <tr>
                      <td
                        width="100%"
                        style="
                          white-space: nowrap;
                          text-overflow: ellipsis;
                          overflow: hidden;
                          max-width: 1px;
                        "
                      >

                      <span v-if="album.likes">
                      <b-badge v-if="parseInt(album.likes) == 1 ">{{ album.likes }} Like</b-badge>
                      <b-badge v-if="parseInt(album.likes) > 1 ">{{ album.likes }} Likes</b-badge>
                      &nbsp;</span>
                      <span style="color: grey; font-style: italic">{{ album.minor_artists }}</span>
                      </td>
                    </tr>
                  </table>
                </b-card-text>
              </b-col>
            </div>
          </b-card>
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
import axios from 'axios';
import {eventBus} from "../main.js";
import {currentConfig} from "../main.js";

export default {
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
      infiniteId: +new Date()
    };
  },
  methods: {
    // loads from selected work
    getAlbums(id) {
      this.changeAlbums()
      this.workId = id;
      this.loading = true;
      const path = 'api/albums/' + id;
      axios.get(path)
        .then((res) => {
          this.albums = res.data.albums;
          this.loading = false;
          //console.log(this.albums[0].id);
          this.selectRow(this.albums[0].id); // select first row
          currentConfig.album = this.albums[0].id;
          localStorage.setItem('currentConfig', JSON.stringify(currentConfig));
          eventBus.$emit('fireArtistList', res.data.artists);
          eventBus.$emit('fireAlbumData', this.albums[0].id);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading = false;
        });
    },
    // loads from localstorage
    initialGetAlbums(id) {
      this.changeAlbums()
      this.workId = id;
      this.loading = true;
      const path = 'api/albums/' + id;
      axios.get(path)
        .then((res) => {
          this.albums = res.data.albums;
          eventBus.artists = res.data.artists;
          this.loading = false;

          this.selectRow(currentConfig.album);
          eventBus.$emit('fireAlbumData', currentConfig.album);
          eventBus.$emit('fireArtistList', res.data.artists);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading = false;
        });
    },
    getAlbumData(albumId) {
        eventBus.$emit('fireAlbumData', albumId);
        currentConfig.album = albumId;
        localStorage.setItem('currentConfig', JSON.stringify(currentConfig));
        //this.$refs.composer.selectColor = "blue";
    },
      selectRow(album){
        this.selectedAlbum = album;
    },
    getFilteredAlbums(id, item, sort) {
      this.changeAlbums()
      this.workId = id;
      this.artistName = item;
      this.sort = sort;
      console.log(sort);
      this.loading = true;
      const path = 'api/albums/' + id + '?artist=' + item + '&sort=' + sort;
      axios.get(path)
        .then((res) => {
          this.albums = res.data.albums;
          this.loading = false;

          //this.selectRow(currentConfig.album);
          //eventBus.$emit('fireAlbumData', currentConfig.album);
          //this.selectRow(this.albums[0].album_id); // select first row
          //eventBus.$emit('fireAlbumData', this.albums[0].id);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading = false;
        });
    },
      infiniteHandler($state) {
      const path = 'api/albums/' + this.workId + '?artist=' + this.artistName + '&sort=' + this.sort + '&page=' + this.page;
      console.log(path);
      axios.get(path)
        .then(({ data }) => {
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
      this.sort='';
      this.page = 2;
      this.albums = [];
      this.infiniteId += 1;
    },
  },
  created() {
    if (window.location.href.indexOf("radio") != -1){ // dont get works in radio mode
      this.radioMode = true;
    } else {
      this.initialGetAlbums(currentConfig.work);
    }
    eventBus.$on('fireAlbums', this.getAlbums);
    eventBus.$on('fireAlbumFilter', this.getFilteredAlbums);
    eventBus.$on('fireArtistAlbums', this.getFilteredAlbums);
  },
  beforeDestroy() {
    eventBus.$off('fireAlbums', this.getAlbums);
    eventBus.$off('fireAlbumFilter', this.getFilteredAlbums);
    eventBus.$off('fireArtistAlbums', this.getFilteredAlbums);
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
.spinner {
  text-align: center;
}
.badge-dark {
  background: none;
}
.m-5 {
  color: #343a40;
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
  padding: 0px;
  vertical-align: bottom;
  /*   border-top: 1px dotted lightgray;*/
}
tr {
  border-bottom: 0px;
}
table {
  width: 100%;
  border-collapse: separate;
  font-size: 13px;
  padding: 0px;
  padding-top: 4px;
  padding-left: 3px;
  padding-bottom: 2px;
}
header.card-header {
  background-color: #fff;
  border: none;
  padding-left: 10px;
  padding-bottom: 0px;
}
.mb-0 {
  font-size: 12px;
  font-weight: bold;
}
.card {
  background-color: #fff;
  border: none;
  margin-top: 5px;
}
.card:hover {
  cursor: pointer;
}
.highlight {
/*  background-color: rgb(52, 58, 64, 0.7) !important;*/
  background-color: royalblue !important;
  color: white !important;
}
.highlight span {
  color: white !important;
}
.card-deck {
  padding-left: 5px;
  padding-right: 5px;
}
.badge {
  color: #fff;
  background-color: #777777;
  border-radius: 7px;
}
.no-albums-found {
  font-size: 14px;
  color: grey;
  text-align: center;
}
.album_columns {
  padding-right: 0px;
}
.album_text_columns {
  padding-left: 0px;
}
.badge {
  color: #fff;
  background-color: darkgoldenrod;
  border-radius: 7px;
}
</style>
