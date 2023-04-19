<template>
  <div>
    <Transition name="fade">
      <div v-show="showCover" id="albums-overlay"></div>
    </Transition>

    <!-- ALBUM POPUP -->
    <div>
      <div v-for="album in albums" :key="album.album_id">
        <Transition name="fade">
        <table class="popup" v-show="showAlbum == album.album_id">
          <tr >
            <td>
              <img class="album-popup-cover" :ref="album.album_id" :src="album.img_big" />
            </td>
            <td>
              <div class="image-caption">
          <tr>
            <span class="album-title">{{ album.album_name }} </span><br>
            <span class="album-details">℗ {{ album.release_date }}</span>
            <span class="album-details"> {{ album.label }} </span><br><br>
          </tr>
          <table class="no-wrap">
            <div class="spinner-left" v-show="albumDataLoading" role="status">
              <b-spinner class="m-5"></b-spinner>
            </div>
  
            <tr v-show="!albumDataLoading && albumWorks.length > 0" v-for="[work, data] in albumWorks" :key="work.id">
              <Transition name="fade">
              <td class="work-td" v-if="showAlbum == album.album_id">
                <span class="album-work-composer">{{ work.composer }} </span><br>
                <span class="album-work-title">{{ work.title }} &nbsp;</span>
                <span v-if="work.cat" class="album-work-cat">{{ work.cat }}</span><br>
                <span v-if="params.artist" class="album-highlight-artist">{{ highlightArtist(data.all_artists) }}</span>
                <span v-if="highlightArtist(data.all_artists)" class="album-work-artists">, </span>
                <span class="album-work-artists">{{ printArtists(data.artists) }}</span><br>
                <span class="album-work-artists"><span style='font-size: 10px;'>
                      <b-icon-clock></b-icon-clock></span>&nbsp;{{ printDuration(data.tracks) }}</span>&nbsp;<b-badge class="duration-badge">{{printFull(work.duration, data.tracks)}}</b-badge><br><span v-if="showTracks(work.duration, data.tracks)"><br></span>
                      <tr v-if="showTracks(work.duration, data.tracks)">
                        <td v-html="printTracks(work, data.tracks)" class="work-td-minor">
                      </td>
                      </tr>
              </td>
            </Transition>
            </tr>
   
          </table>
      </div>
      </td>
      </tr>
      </table>
    </Transition>
    </div>
  </div>

  <!-- ALBUM GRID -->
  <div class="container-fluid">
    <h6 class="message narrow">
      <div v-html="message" />
    </h6>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
    <div v-show="!loading" class="grid-container">
      <div class="grid-item" v-for="album in albums" :key="album.album_id">
        <img @click="showCover = album.album_id" class="album-cover" height="auto" v-lazy="album.img_big" />
      </div>
      <infinite-loading spinner="spiral" :identifier="infiniteId" @infinite="infiniteHandler">
        <div slot="no-more"></div>
        <div slot="no-results"></div>
      </infinite-loading>
    </div>
  </div>
  </div>
</template>

<script>
import { eventBus } from "@/main.js";
import axios from "axios";

export default {
  data() {
    return {
      albums: [],
      albumWorks: [],
      showCover: false,
      albumDataLoading: false,
      loading: false,
      message: "",
      page: 1,
      infiniteId: +new Date(),
      params: {}
    };
  },
  computed: {
    showAlbum() {
      if (this.showCover) {
        const imageWidth = this.$refs[this.showCover][0].width;
        const imageHeight = this.$refs[this.showCover][0].height;
        if (imageWidth == 0) {
          return false;
        }
        this.getAlbumWorks(this.showCover);
        document.documentElement.style.setProperty("--imagewidth", imageWidth + 'px');
        document.documentElement.style.setProperty("--imageheight", imageHeight + 'px');
        return this.showCover;
      } else {
        return false;
      }
    }
  },
  methods: {
    durationAlt(ms) {
      let seconds = Math.floor(ms / 1000);
      let hours = Math.floor(seconds / 3600);
      seconds = seconds - (hours * 3600);
      let minutes = Math.round(seconds / 60);

      if (hours > 1) {
        return hours + "h" + minutes + "m";
      } else {
        return minutes + "m"
      }
    },
    duration(ms) {
      let seconds = Math.floor(ms / 1000);
      let hours = Math.round(seconds / 3600 * 10) / 10;
      let minutes = Math.round(seconds / 60);

      if (hours > 1) {
        return hours + "h";
      } else {
        return minutes + "m"
      }
    },
    highlightArtist(artists){
      if (this.params.artist) {
        if(artists.includes(this.params.artist)){
          return this.params.artist;
        } else {
          return null;
        }
      } else {
        return null;
      }
    },
    printArtists(artists){
      if (this.params.artist) {
        if(artists.includes(this.params.artist + ",")){
          return artists.replace(this.params.artist + ",", '');
        }
        else if (artists.includes(this.params.artist)){
          return artists.replace(this.params.artist, '');
        } else {
          return artists;
        }
      } else {
        return artists;
      }
    },
    printDuration(tracks){
      let duration = 0;
      for (var i = 0; i < tracks.length; i++) {
        duration = duration + tracks[i][3];
      }
      return this.duration(duration);
    },
    printFull(workDuration, tracks){ // add to albums list
      let duration = 0;
      for (var i = 0; i < tracks.length; i++) {
        duration = duration + tracks[i][3];
      }
      if (duration < workDuration / 1.5){
        return "Excerpt"
      }
      return "Full performance";
    },
    showTracks(workDuration, tracks){ // add to albums list
      let duration = 0;
      for (var i = 0; i < tracks.length; i++) {
        duration = duration + tracks[i][3];
      }
      if (duration < workDuration / 1.5){
        return true
      }
      return false;
    },
    printTracks(work, tracks){ // add to albums list
      let duration = 0;
      let tracksList = "";
      for (var i = 0; i < tracks.length; i++) {
        duration = duration + tracks[i][3];
        let trackRaw = tracks[i][0];
        let trackFixed = '';

        if(work.genre == 'Opera' || work.genre == 'Stage Work' || work.genre == 'Ballet'){
          trackFixed = trackRaw.substring(trackRaw.lastIndexOf(' Act ') + 1).trim()
          if(trackFixed.lastIndexOf(':') === -1){
            trackFixed = trackFixed + ": Prelude ";
          }
        } else {
          trackFixed = trackRaw.substring(trackRaw.lastIndexOf(':') + 1)
        }
        tracksList = tracksList + trackFixed + "<br>";
      }
      if (duration < work.duration / 1.5){
        return tracksList;
      }
      return null;
    },
    messageBuilder(status, fieldData) {
      if (!fieldData || Object.keys(fieldData).length === 0) {
        return "Error retrieving albums from database! Please try again later.";
      }

      let composer = fieldData.composer;
      let period = fieldData.period;
      let artist = fieldData.artist;
      let work = fieldData.work;
      let sort = fieldData.sort;

      if (status == 'success') {
        let message = "Albums"
        if (!composer && !period && !artist && !work || period == 'all') {
          return (sort == 'popular' || !sort) ? "Popular albums" : ((sort == 'newest') ? "New releases" : "Historical recordings");
        }
        if (composer) {
          message = message + " featuring <b>" + composer + '</b>';
        } else if (period) {
          period = (period == '20th') ? "<b>20th/21st century</b>" : period;
          message = "<b>" + (period.charAt(0).toUpperCase() + period.slice(1)) + "</b> music " + message.toLowerCase();
        }
        if (artist) {
          message = message + " with performances by <b>" + artist + '</b>';
        }
        if (work) {
          message = message + " with work titled <b>" + work + "</b>";
        }
        return message;
      } else {
        return "Error retrieving albums from database! Please try again later."
      }
    },
    getAlbums(fieldData) {
      this.showCover = false;
      this.params = fieldData;
      this.params['page'] = 1;
      this.loading = true;

      const params = this.params;
      const path = "api/albumsview";
      axios
        .get(path, { params })
        .then((res) => {
          this.loading = false;
          this.albums = res.data.albums;
          if (this.albums.length > 0) {
            this.message = this.messageBuilder('success', fieldData);
          } else {
            if (fieldData.artist && fieldData.composer) {
              this.message = "No albums found for <b>" + fieldData.artist + "</b> performing <b>" + fieldData.composer + "</b>."
            } else {
              this.message = "No albums found for query."
            }
          }
          if (res.data.works.length > 0) {
            this.$lists.albumViewWorks = res.data.works;
          } else {
            this.$lists.albumViewWorks = this.$lists.workList;
          }

          this.params['page'] += 1;
        })
        .catch((error) => {
          this.loading = false;
          this.message = this.messageBuilder('error');
          console.error(error);
        });
    },
    getAlbumWorks(album_id){
      this.albumDataLoading = true;
      this.albumWorks = [];
      const params = {'album_id': album_id};
      const path = "api/getalbumworks";
      axios
        .get(path, { params })
        .then(({ data }) => {
          this.albumDataLoading = false;
          if (data.works.length) {
            this.albumWorks.push(...data.works);
          }
        })
        .catch((error) => {
          this.albumDataLoading = false;
          console.error(error);
        });
    },
    infiniteHandler($state) {
      const params = this.params;
      const path = "api/albumsview";
      axios
        .get(path, { params })
        .then(({ data }) => {
          if (data.albums.length) {
            this.params['page'] += 1;
            this.albums.push(...data.albums);
            $state.loaded();
          } else {
            $state.complete();
          }
        });
    },
  },
  mounted() {
    this.getAlbums(this.params);
    const overlay = document.getElementById('albums-overlay');

    overlay.addEventListener('click', () => {
      this.showCover = false;
      //overlay.style.display = 'none';
    });
  },
  created() {
    eventBus.$on("requestAlbumViewAlbums", this.getAlbums);
  },
  beforeDestroy() {
    eventBus.$off("requestAlbumViewAlbums", this.getAlbums);
  },
}
</script>




<style scoped>
.fade-enter-active {
  transition: all 0.5s;
}

.fade-leave-active {
  transition: all 0.3s;
}

.fade-enter {
  opacity: 0;
}

.fade-leave-to {
  opacity: 0;
}

 #albums-overlay {
        display: block;
        position: fixed;
        top: 66px;
        left: 0;
        width: 100%;
        height: calc(100vh - 66px - 100px);
        background: rgba(52, 58, 64, 0.75);

    }

.album-title {
  color: var(--my-white) !important;
  font-weight: 600;
  font-size: 16px;
}

.album-details {
  color: var(--medium-light-gray) !important;
  font-size: 14px;
  font-family: Roboto Condensed !important;
}

.album-work-composer{
  color: var(--orange) !important;
  font-size: 14px;
}

.album-work-title{
  color: var(--my-white) !important;
  font-weight: 600;
  font-size: 14px;
}

.album-work-cat{
  color: var(--medium-light-gray) !important;
  font-size: 12px;
}

.album-highlight-artist{
  color: turquoise !important;
  font-weight: 600;
  font-size: 12px;
  font-family: Roboto Condensed !important;
}

.album-work-artists{
  color: var(--medium-dark-gray) !important;
  font-size: 12px;
  font-family: Roboto Condensed !important;
}



.reveal {
  visibility: visible !important;
}

.popup {
  line-height: 16px;
  padding: 0px;
  position: fixed !important;
  top: 50%;
  left: 50%;
  transform: translate(-50%, calc(-50% - 33px + 16px - var(--panelheight)/2));
  background-color: var(--dark-gray);
  box-shadow: rgba(0, 0, 0, 0.16) 0px 1px 4px;
  z-index: 100;
}

table.no-wrap{

 border-collapse: collapse;
  width: 100%;
}

table.no-wrap th, table.no-wrap td {

  padding-left: 10px;
  padding-right: 10px;
  text-align: left;
  white-space: nowrap;
  text-overflow: ellipsis;
  padding-top: 10px;
  padding-bottom: 10px;
  width: 100%;
}

td.work-td{
  border-left: solid 1px white;
}

td.work-td-minor{
  width: 100%;
  border-left: solid 1px var(--orange);
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  max-width: calc(var(--imagewidth) - 100px);
  padding-top: 0px !important;
  padding-bottom: 0px !important;
  font-size: 12px;
  color: var(--light-gray) !important;
  font-family: Roboto Condensed !important;
}

/* Change color of the table cell when hovering over it */
td.work-td:hover {
    background-color: #454D54; /* Choose your desired color */
    cursor: pointer;
}

.image-caption {
  max-height: min(var(--imageheight), calc(100vh - 66px - var(--panelheight) - 100px - 40px));
  visibility: inherit;
  width: 100%;
  min-width: calc(var(--imagewidth) / 1.75);
  padding-top: 15px;
  padding-bottom: 15px;
  padding-left: 15px;
  padding-right: 15px;
  overflow-y: auto;
  overflow-x: hidden;
}

.album-popup-cover{
  box-shadow: rgba(0, 0, 0, 0.16) 0px 1px 4px;
/*  max-height: calc(80vh - var(--workingheight));*/
  max-height: calc(100vh - 66px - var(--panelheight) - 100px - 40px);
  max-width: 50vw;
}

.orange{
  color: var(--orange) !important;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  grid-gap: 10px;
  grid-auto-flow: dense;
  padding-top: 10px;
  padding-bottom: 15px;
}

.grid-item {
  display: flex;
}

.album-cover {
  width: 100%;
  height: auto;
  box-shadow: rgba(0, 0, 0, 0.2) 0px 1px 4px;
}
.album-cover:hover {
  cursor: pointer;
  box-shadow: rgba(0, 0, 0, 0.6) 0px 2px 4px !important;
  outline: solid 5px var(--orange);
}
.spinner {
  text-align: center;
}
.spinner-left {
  text-align: left;
}
.m-5 {
    color: #9da6af;
}
.message{
  margin-top: 12px;
  text-align: center;
  margin-bottom: 2px;
  color: var(--medium-gray);
}
 .narrow{
  font-family: Roboto Condensed !important;
 }
 .duration-badge{
  font-size: 10px;
  font-family: Roboto Condensed !important;
  color: var(--light-gray) !important;
  vertical-align: 0.5px;
}


 /*scrollbars*/
.image-caption {
  --scroll-bar-color: var(--scroll-color-light);
  --scroll-bar-bg-color: var(--dark-gray);
}
.info-card-text {
  image-caption: thin;
  image-caption: var(--scroll-bar-color) var(--scroll-bar-bg-color) !important;
}

/* Works on Chrome, Edge, and Safari */
.image-caption::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}
.image-caption::-webkit-scrollbar-track {
  background: var(--scroll-bar-bg-color) !important;
}
.image-caption::-webkit-scrollbar-thumb {
  background-color: var(--scroll-bar-color);
  border-radius: 20px;
  border: 3px solid var(--scroll-bar-bg-color) !important;
}

</style>

