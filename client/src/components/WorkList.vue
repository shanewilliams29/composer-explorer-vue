<template>
  <div>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
      <div class="row">
          <span v-show="!loading && works.length < 1 && !artistMode" class="col no-works-found">
            No works found for {{ composer }}.
          </span>
          <span v-show="!loading && works.length < 1 && artistMode" class="col no-works-found">
            Select a composer to see works performed by {{ artist }}.
          </span>
        <b-card-group deck v-show="!loading && works">
          <b-card
            v-for="(genre, index) in works"
            :key="index"
            no-body
            header-tag="header"
          >
            <div class="#header" v-b-toggle="index.replace(/\s/g, '')">
              <h6 class="m-2 mb-0">{{ index }}<span class="mb-0 float-right when-opened"><b-icon-chevron-up></b-icon-chevron-up></span><span class="mb-0 float-right when-closed"><b-icon-chevron-down></b-icon-chevron-down></span></h6>
            </div>
            <b-collapse :visible="visibility" :id="index.replace(/\s/g, '')">
            <b-card-text>
              <table cellspacing="0">
                <tr
                  v-for="work in genre"
                  :key="work.id"
                  @click="selectRow(work.id); getAlbums(work.id, work.title);"
                  :class="{'highlight': (work.id == selectedWork)}"
                >
                  <td width="17%">
                    <span style="white-space: nowrap; color: darkred"
                      ><span v-if="work.cat">{{ work.cat }}&nbsp;&nbsp;</span
                      ><span v-else>{{ work.date }}</span
                      ></span
                    >
                  </td>
                  <td
                    width="78%"
                    style="
                      white-space: nowrap;
                      text-overflow: ellipsis;
                      overflow: hidden;
                      max-width: 1px;
                    "
                  >
                    {{ work.title
                    }}<span v-if="work.nickname" style="color: gray">
                      · {{ work.nickname }}</span
                    >
                  </td>
                  <td width="5%" style="text-align: right">
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
import {currentConfig} from "../main.js";

export default {
  data() {
    return {
      works: [],
      loading: false,
      selectedWork: null,
      visibility: true,
      artist: "",
      artistMode: false
    };
  },
  methods: {
    getWorks(composer) {
      this.loading = true;
      this.composer = composer;
      const path = 'api/works/' + composer;
      axios.get(path)
        .then((res) => {
          this.works = res.data.works;
          this.visibility=true
          this.composer = composer;
          this.loading = false;
          eventBus.$emit('fireWorksLoaded');
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading = false;
        });
    },
    getGenreWorks(genres, filter) {
      console.log(filter);
      if (genres.length < 1){
        console.log("No genres selected");
      }
      else{
      const payload = {genres: genres, filter: filter};
      console.log(payload);
      const path = 'api/worksbygenre';
      axios.post(path, payload)
        .then((res) => {
          console.log(res.data);
          this.works = res.data.works;
          //eventBus.$emit('fireRadioGenreList', res.data.genres);
          this.visibility=true;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
        });
      }
    },
    getArtistWorks(artist, composer) {
      this.loading = true;
      this.artist = artist;
      this.artistMode = true;
      this.composer = composer;
      const path = 'api/artistworks?artist=' + artist + '&composer=' + composer;
      axios.get(path)
        .then((res) => {
          this.works = res.data.works;
          this.visibility=true
          this.composer = composer;
          this.loading = false;
          // eventBus.$emit('fireArtistWorksLoaded');
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading = false;
        });
    },
      getAlbums(workId, title) {
        if(!this.artistMode){
          eventBus.$emit('fireAlbums', workId, title);
          currentConfig.work = workId;
          currentConfig.workTitle = title;
          localStorage.setItem('currentConfig', JSON.stringify(currentConfig));
        } else {
          eventBus.$emit('fireArtistAlbums', workId, this.artist);
        }
    },
      selectRow(work){
        this.selectedWork = work;

    },
    getFilteredWorks(item) {
      this.loading = true;
      if (item == "all") {
        this.visibility=false;
      } else {
        this.visibility=true;
      }
      const path = 'api/works/' + this.composer + '?filter=' + item;
      axios.get(path)
        .then((res) => {
          this.works = res.data.works;
          this.loading=false;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading=false;
        });
    },
    getSearchWorks(item) {
      const path = 'api/works/' + this.composer + '?search=' + item;
      axios.get(path)
        .then((res) => {
          this.works = res.data.works;
          this.visibility=true;
          this.loading=false;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading=false;
        });
    },
    fireComposers(composer) {
        this.getWorks(composer);
        currentConfig.composer = composer;
        localStorage.setItem('currentConfig', JSON.stringify(currentConfig));
    },
    fireClearWorks(artist){
      this.artistMode = true;
      this.artist = artist;
      this.getSearchWorks('ggesagoseofsa'); // get no results
    }
  },
  created() {
    this.getWorks(currentConfig.composer);
    this.selectRow(currentConfig.work);
    eventBus.$on('fireComposers', this.fireComposers);
    eventBus.$on('fireArtistWorks', this.getArtistWorks);
    eventBus.$on('fireWorkFilter', this.getFilteredWorks);
    eventBus.$on('fireWorkSearch', this.getSearchWorks);
    eventBus.$on('fireClearWorks', this.fireClearWorks);
    eventBus.$on('fireGenreSelectRadio', this.getGenreWorks);
  },
  beforeDestroy() {
    eventBus.$off('fireComposers', this.fireComposers);
    eventBus.$off('fireArtistWorks', this.getArtistWorks);
    eventBus.$off('fireWorkFilter', this.getFilteredWorks);
    eventBus.$off('fireWorkSearch', this.getSearchWorks);
    eventBus.$off('fireClearWorks', this.fireClearWorks);
    eventBus.$off('fireGenreSelectRadio', this.getGenreWorks);
  }
};
</script>

<style scoped>
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
  background-color: royalblue;
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
