<template>
  <div>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
    <div class="row">
      <span v-show="!loading && works.length < 1 && !$view.mode" class="col no-works-found">
        <div class="m-4">No works found for {{ $config.composer }}.</div>
      </span>
      <span v-show="!loading && works.length < 1 && $view.mode == 'performer' && $config.artist" class="col no-works-found">
        <div class="m-4">Select a composer to see works performed by {{ $config.artist }}.</div>
      </span>
      <span v-show="!loading && works.length < 1 && $view.mode == 'performer' && !$config.artist" class="col no-works-found">
        <div class="m-4">Search for a performer to view works they perform.</div>
      </span>
      <span v-show="!loading && works.length < 1 && $view.mode == 'radio'" class="col no-works-found">
        <div class="m-4">Select from the options above to create your own customized radio.</div>
      </span>
      <b-card-group deck v-if="!loading && works">
        <b-card v-for="(genre, index) in works" :key="index" no-body header-tag="header" class="shadow-sm">
          <div class="#header" v-b-toggle="index.replace(/\s/g, '')">
            <h6 class="m-2 mb-0">
              {{ index }}<span class="mb-0 float-right when-opened"><b-icon-chevron-up></b-icon-chevron-up></span><span class="mb-0 float-right when-closed"><b-icon-chevron-down></b-icon-chevron-down></span>
            </h6>
          </div>
          <b-collapse :visible="visibility" :id="index.replace(/\s/g, '')">
            <b-card-text>
              <table cellspacing="0">
                <tr v-for="work in genre" :key="work.id" @click="selectRow(work.id); getAlbums(work.id, work.title);" :class="{'highlight': (work.id == selectedWork)}">
                  <td width="17%">
                    <span style="white-space: nowrap; color: darkred;"><span v-if="work.cat">{{ work.cat }}&nbsp;&nbsp;</span><span v-else>{{ work.date }}</span></span>
                  </td>
                  <td width="78%" style="white-space: nowrap; text-overflow: ellipsis; overflow: hidden; max-width: 1px;">{{ work.title }}<span v-if="work.nickname" style="color: gray;"> · {{ work.nickname }}</span></td>
                  <td width="5%" style="text-align: right;">
                    <b-badge>{{ work.album_count }}</b-badge>
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
      works: [],
      playlist: [],
      loading: false,
      selectedWork: null,
      visibility: true,
      shuffle: false
    };
  },
  methods: {
    getWorks(composer) {
      this.loading = true;
      this.$config.composer = composer;
      const path = 'api/works/' + composer;
      axios.get(path).then((res) => {
        this.works = res.data.works;
        this.playlist = res.data.playlist;
        this.visibility = true
        this.loading = false;
        //eventBus.$emit('fireWorksLoaded'); // for mobile
      }).catch((error) => {
        console.error(error);
        this.loading = false;
      });
    },
    getGenreWorks(genres, filter, search) {
      if (genres.length < 1) {
        this.works = [];
      } else {
        const payload = {
          genres: genres,
          filter: filter,
          search: search
        };
        const path = 'api/worksbygenre';
        axios.post(path, payload).then((res) => {
          this.works = res.data.works;
          this.visibility = true;
        }).catch((error) => {
          console.error(error);
        });
      }
    },
    getArtistWorks(artist, composer) {
      this.loading = true;
      this.$config.artist = artist;
      this.$config.composer = composer;
      const path = 'api/artistworks?artist=' + artist + '&composer=' + composer;
      axios.get(path).then((res) => {
        this.works = res.data.works;
        this.playlist = res.data.playlist;
        this.visibility = true
        this.loading = false;
      }).catch((error) => {
        console.error(error);
        this.loading = false;
      });
    },
    getAlbums(workId, title) {
      this.$config.work = workId;
      this.$config.workTitle = title;
      localStorage.setItem('config', JSON.stringify(this.$config));

      if (this.$view.mode != 'performer') {
        eventBus.$emit('fireAlbums', workId);
      } else {
        eventBus.$emit('fireAlbums', workId, this.$config.artist);
      }
    },
    getAlbumsAndPlay(workId, title) {
      this.$config.work = workId;
      this.$config.workTitle = title;
      localStorage.setItem('config', JSON.stringify(this.$config));

      if (this.$view.mode != 'performer') {
        eventBus.$emit('fireAlbumsAndPlay', workId);
      } else {
        eventBus.$emit('fireAlbumsAndPlay', workId, this.$config.artist);
      }
    },
    selectRow(work) {
      this.selectedWork = work;
    },
    getFilteredWorks(item) {
      this.loading = true;
      if (item == "all") {
        this.visibility = false;
      } else {
        this.visibility = true;
      }
      const path = 'api/works/' + this.$config.composer + '?filter=' + item;
      axios.get(path).then((res) => {
        this.works = res.data.works;
        this.playlist = res.data.playlist;
        this.loading = false;
      }).catch((error) => {
        console.error(error);
        this.loading = false;
      });
    },
    getSearchWorks(item) {
      const path = 'api/works/' + this.$config.composer + '?search=' + item;
      axios.get(path).then((res) => {
        this.works = res.data.works;
        this.playlist = res.data.playlist;
        this.visibility = true;
        this.loading = false;
      }).catch((error) => {
        console.error(error);
        this.loading = false;
      });
    },
    fireComposers(composer) {
      this.getWorks(composer);
      this.$config.composer = composer;
      localStorage.setItem('config', JSON.stringify(this.$config));
    },
    fireClearWorks(artist) {
      this.$config.artist = artist;
      this.works = [];
    },
    nextWork() {
      if (this.shuffle) {
        this.$config.previousWork = this.$config.work;
        this.$config.previousWorkTitle = this.$config.workTitle;
        this.playRandomWork();
      } else {
        for (var i = 0; i < this.playlist.length; i++) {
          if (this.playlist[i]['id'] == this.selectedWork && i !== this.playlist.length - 1) {
            this.selectRow(this.playlist[i + 1]['id']);
            this.getAlbumsAndPlay(this.playlist[i + 1]['id']);
            break;
          }
        }
      }
    },
    previousWork() {
      if (this.shuffle) {
        this.selectRow(this.$config.previousWork); //allows you to jump one back
        this.getAlbumsAndPlay(this.$config.previousWork, this.$config.previousWorkTitle)
      } else {
        for (var i = 0; i < this.playlist.length; i++) {
          if (this.playlist[i]['id'] == this.selectedWork && i !== 0) {
            this.selectRow(this.playlist[i - 1]['id']);
            this.getAlbumsAndPlay(this.playlist[i - 1]['id']);
            break;
          }
        }
      }
    },
    playRandomWork() {
      function randomIntFromInterval(min, max) { // min and max included
        return Math.floor(Math.random() * (max - min + 1) + min)
      }
      const rndInt = randomIntFromInterval(0, this.playlist.length - 1)
      this.selectRow(this.playlist[rndInt]['id']);
      this.getAlbumsAndPlay(this.playlist[rndInt]['id']);
    },
    toggleShuffle(shuffleState) {
      this.shuffle = shuffleState;
    },
  },
  created() {
    if (!this.$view.mode) { // dont get works in radio mode or artist mode
      this.getWorks(this.$config.composer);
      this.selectRow(this.$config.work);
    }
    eventBus.$on('fireComposers', this.fireComposers);
    eventBus.$on('fireArtistWorks', this.getArtistWorks);
    eventBus.$on('fireWorkFilter', this.getFilteredWorks);
    eventBus.$on('fireWorkSearch', this.getSearchWorks);
    eventBus.$on('fireClearWorks', this.fireClearWorks);
    eventBus.$on('fireGenreSelectRadio', this.getGenreWorks);
    eventBus.$on('fireNextWork', this.nextWork);
    eventBus.$on('firePreviousWork', this.previousWork);
    eventBus.$on('fireToggleShuffle', this.toggleShuffle);
  },
  beforeDestroy() {
    eventBus.$off('fireComposers', this.fireComposers);
    eventBus.$off('fireArtistWorks', this.getArtistWorks);
    eventBus.$off('fireWorkFilter', this.getFilteredWorks);
    eventBus.$off('fireWorkSearch', this.getSearchWorks);
    eventBus.$off('fireClearWorks', this.fireClearWorks);
    eventBus.$off('fireGenreSelectRadio', this.getGenreWorks);
    eventBus.$off('fireNextWork', this.nextWork);
    eventBus.$off('firePreviousWork', this.previousWork);
    eventBus.$off('fireToggleShuffle', this.toggleShuffle);
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
  background-color: var(--highlight-color);
  color: white !important;
}
.highlight span {
  color: white !important;
}
tr:hover {
  cursor: pointer;
}

.highlight td:first-child,
.highlight td:last-child {
  position: relative;
}

.highlight td:first-child:before,
.highlight td:last-child:after {
  content: "";
  position: absolute;
  top: 0px;
  bottom: 0px;
  width: 6px;
  display: block;
  background: inherit;
  border: inherit;
}
.highlight td:first-child:before {
  right: 100%;
}
.highlight td:last-child:after {
  left: 100%;
}
header.card-header {
  background-color: #fff;
  border: none;
  padding-left: 10px;
  padding-bottom: 0px;
  cursor: pointer;
}
header.card-header:hover {
  cursor: pointer;
}
.mb-0 {
  font-size: 14px;
  font-weight: bold;
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
.badge {
  color: #fff;
  background-color: rgb(52, 58, 64, 0.7);
  border-radius: 7px;
}
.no-works-found {
  font-size: 14px;
  color: grey;
  text-align: center;
}
</style>
