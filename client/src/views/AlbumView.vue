<template>
  <div id="performer">
    <AlbumsViewHeading/>
    <div class="container-fluid">
      <Transition name="fade">
      <b-row v-if="showCloud">
        <b-col class="display-list"><AlbumsOverview/></b-col>
      </b-row>
      </Transition>
    </div>
  </div>
</template>



<script>
import AlbumsViewHeading from '@/components/albumsview/AlbumsViewHeading.vue'
import AlbumsOverview from '@/components/albumsview/AlbumsOverview.vue';

import {eventBus} from "../main.js";

export default {
  name: 'AlbumView',
  components: {
    AlbumsViewHeading,
    AlbumsOverview
  },
  data() {
    return {
      showCloud: true
    };
  },
  methods: {
    hideCloud () {
      this.showCloud = false;
    },
    unhideCloud () {
      this.showCloud = true;
    },
  },
  beforeCreate() {
    document.documentElement.style.setProperty("--flex", "1");
  },
  created() {
    window.firstLoad = false; // allow playback on first load for performer view
    eventBus.$on('requestComposersForArtist', this.hideCloud);
    eventBus.$on('clearPerformers', this.unhideCloud);
    this.$view.mode = 'performer';
    if (this.$route.query.artist){
        this.showCloud = false;
    } else{
      this.showCloud = true;
    }
    document.documentElement.style.setProperty("--playback-color", "var(--yellow)"); //#fd7e14
  },
}
</script>
<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.75s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
>>> .highlight{
  background-color: #e47112 !important;
}
>>> .highlight td{
  background-color: #e47112 !important;
}
>>> .music-note{
  color: var(--orange);
}
.display-list{
  padding: 0px !important;
}
</style>
