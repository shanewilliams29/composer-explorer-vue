<template>
  <div id="performer">
    <PerformersHeadings/>
    <div class="container-fluid">
      <Transition name="fade">
      <b-row v-if="showCloud">
        <b-col class="word-cloud"><PerformersOverview/></b-col>
      </b-row>
      </Transition>
      <b-row v-if="!showCloud">
        <b-col class="display-list first-col" ref="scroll-box-comp"><ComposerList/></b-col>
        <b-col class="display-list" ref="scroll-box"><WorkList/></b-col>
        <b-col class="display-list last-col extra-margin"><AlbumList/></b-col>
      </b-row>
    </div>
  </div>
</template>



<script>
import PerformersHeadings from '@/components/performers/PerformersHeadings.vue'
import ComposerList from "@/components/composers/ComposerList.vue";
import WorkList from "@/components/works/WorkList.vue";
import AlbumList from "@/components/albums/AlbumList.vue";
import PerformersOverview from '@/components/performers/PerformersOverview.vue';

import {eventBus} from "../main.js";

export default {
  name: 'PerformerView',
  components: {
    PerformersHeadings,
    ComposerList,
    WorkList,
    AlbumList,
    PerformersOverview
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
    if(this.$config.albumSize == 'large'){
        document.documentElement.style.setProperty('--flex', '0 0 450px');
    } else {
        document.documentElement.style.setProperty('--flex', '0 0 450px');
    } 
    document.documentElement.style.setProperty("--playback-color", "var(--yellow)"); // #6f42c1
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

>>> .highlight{
  background-color: var(--purple);
}
>>> .highlight td{
  background-color: var(--purple);
}
>>> .music-note{
  color: var(--purple);
}
</style>
