<template>
  <b-card no-body class="track-info-card shadow-sm">
    <b-card-text class="info-card-text-tracks disable-scrollbars" ref="scroll-box">
      <table>
        <tr v-for="(track, index) in album.tracks" 
          @click="selectTrack(track); playTracks(track[2]);" 
          :class="{'highlight-track': trackMatch(track)}" 
          :id="track[1]" 
          :key="track[1]">
          <td class="left-padding">
            <b-avatar v-if="trackMatch(track)" variant="warning" size="36px" icon="soundwave">
            </b-avatar>
            <b-avatar v-if="!trackMatch(track)" size="36px" :text="(index + 1).toString()">
            </b-avatar>
          </td>
          <td class="info-td">
            <a clss="artist-name">
              <span v-if="genre == 'Opera' || genre == 'Stage Work' || genre == 'Ballet'">
                {{ track[0].substring(track[0].lastIndexOf(' Act ') + 1).trim() }}</span>
              <span v-else>
                {{ track[0].substring(track[0].lastIndexOf(':') + 1) }}
              </span>
            </a>
            <br />
          </td>
        </tr>
      </table>
    </b-card-text>
  </b-card>
</template>

<script>
import { eventBus } from "@/main.js";
import { trackMixin } from "@/components/playback/TrackListing.js"

export default {
  mixins: [trackMixin],
  props: {
    showPanel: Boolean
  },
  computed:{
    panelShow(){
      return this.showPanel;
    }
  },
  watch: {
    panelShow(panelState) {
      if (panelState == true){
        this.selectTrack(this.selectedTrack);
      }
    }
  },
  methods: {
    selectTrack(track){
        this.selectedTrack = track;
    }
  },
  created() {
    eventBus.$on('fireSetAlbum', (album) => {
        this.genre = this.$config.genre;
        this.album = album;
    })
    eventBus.$on('fireSetAlbumHopper', (album) => {
      this.genre = this.$config.genre;
      this.album = album;
  })
}
};
</script>

<style scoped>
table {
  width: 100%;
  margin-bottom: 6px;
}
table tr:not(:last-child) td {
    border-bottom: 1px solid var(--light-gray);
}
td {
  padding-top: 10px;
  padding-bottom: 10px;
}
a {
  color: black;
  font-weight: 600;
  font-size: 14px;
}
a:hover {
  cursor: pointer;
}
.left-padding{
  padding-left: 5px;
  width: 1%;
}
.heading-tr {
  vertical-align: middle;
  height: 62px !important;
}
.heading-td {
  padding-left: 10px;
  font-size: 16px;
}
.spinner {
  text-align: center;
}
.m-5 {
  color: var(--dark-gray);
}
.born-died {
  font-size: 13px !important;
  color: grey !important;
}
.track-info-card {
  padding: 15px;
  padding-top: 15px !important;
  padding-bottom: 10px;
  background-color: 343a40 !important;
  border: none !important;
}
.info-td {
  padding-left: 10px;
}
.highlight-track {
  background-color: var(--light-gray);
  color: var(--black) !important;
}
.disclaimer {
  margin-bottom: 11px;
}
.card-title {
  font-size: 16px;
  height: 62px;
}
.card-body {
  background-color: var(--my-white) !important;
  --scroll-bar-bg-color: var(--light-gray);
}

.info-card-text-tracks {
  font-size: 13px;
  line-height: 120%;
  overflow-y: scroll;
  height: auto;
  padding-left: 2px;
}

.wiki-link {
  font-style: italic;
  color: grey;
}
.open-in-spotify {
  font-size: 12px;
}
.spotify-logo {
  width: auto;
  height: 20px;
}

.disable-scrollbars::-webkit-scrollbar {
  background: transparent; /* Chrome/Safari/Webkit */
  width: 0px;
}
    
.disable-scrollbars {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none;  /* IE 10+ */
}


</style>

<!-- <style scoped>
.track-card {
  background-color: #454d54 !important;
  border: 0px;
  width: 100%;
  overflow-x: hidden;
  margin-right: 12px !important;
  margin-left: 20px !important;
  padding-left: 6px;
  right: 3px;
  height: 100px;
  border-radius: 0px !important;
}
.track-table {
  width: 100%;
  font-size: 13px;
  line-height: 155%;
}
.track-card-text {
  color: var(--medium-light-gray);
  padding-top: 6px;
  padding-bottom: 0px;
  padding-right: 10px;
}
.track-row:hover {
  cursor: pointer;
  color: var(--my-white);
}
.highlight-track {
  color: #ffc107 !important;
}

/*scrollbars*/
 .track-card {
        --scroll-bar-color: var(--medium-light-gray);
        --scroll-bar-bg-color: #454d54;
    }

    .track-card{
        scrollbar-width: thin;
        scrollbar-color: var(--scroll-bar-color) var(--scroll-bar-bg-color) !important;
    }

    /* Works on Chrome, Edge, and Safari */
    .track-card::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }

    .track-card::-webkit-scrollbar-track {
        background: var(--scroll-bar-bg-color) !important;
    }

    .track-card::-webkit-scrollbar-thumb {
        background-color: var(--scroll-bar-color);
        border-radius: 20px;
        border: 3px solid var(--scroll-bar-bg-color)!important;
    }
</style> -->
