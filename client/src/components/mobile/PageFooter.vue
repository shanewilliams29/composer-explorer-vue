<template>
  <div class="container-fluid">
    <b-row class="footer-row">
      <b-col v-show="false" class="info-col">
        <AlbumInfo />
      </b-col>
      <b-col>
        <PlayerControls />
      </b-col>
      <b-col v-show="false">
        <TrackListing />
      </b-col>
    </b-row>
  </div>
</template>

<script>
import axios from 'axios';
import {eventBus} from "@/main.js";
import AlbumInfo from '@/components/subcomponents/AlbumInfo.vue'
import PlayerControls from '@/components/mobile/PlayerControls.vue'
import TrackListing from '@/components/subcomponents/TrackListing.vue'

export default {
  components: {
    AlbumInfo,
    PlayerControls,
    TrackListing
  },
  data() {
    return {
      album: [],
      title: "",
      selectedTrack: ""
    };
  },
  methods: {
    getAlbumInfo(album_id) {
        this.loading = true;
        this.title = eventBus.title;
        const path = 'api/albuminfo/' + album_id;
        axios.get(path)
          .then((res) => {
            this.album = res.data.album; // Change to local file
            this.loading = false;
          })
          .catch((error) => {
            // eslint-disable-next-line
            console.error(error);
            this.loading = false;
          });
      },
    selectTrack(track){
        this.selectedTrack = track;
    },
  },
  created() {
    eventBus.title = "Piano Concerto No. 5 in E♭ major";
    this.getAlbumInfo("BEETHOVEN000163xjbqYLxvXHuanI63XGwri");
    eventBus.$on('fireAlbumData', (album_id) => {
        this.getAlbumInfo(album_id);
    })
  },
};
</script>

<style scoped>
.container-fluid {
  position: relative;
  background-color: #343a40;
  padding-bottom: 0px;
  border-radius: 0px;
  border-radius: 6px;
}
.info-col {
  height: 100px;
  overflow-y: hidden;
}
.album-cover-col {
  padding-right: 0px;
}
.footer-row {
  height: 100px;
  color: white;
}
.col {
  padding: 0px;
}
</style>
