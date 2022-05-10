<template>
  <div id="performer">
    <PerformersHeadings/>
    <div class="container-fluid">
      <b-row v-if="showCloud">
        <b-col class="word-cloud"><WordCloud/></b-col>
      </b-row>
      <b-row v-else>
        <b-col class="display-list first-col" ref="scroll-box-comp"><ComposerList/></b-col>
        <b-col class="display-list" ref="scroll-box"><WorkList/></b-col>
        <b-col class="display-list last-col extra-margin"><AlbumList/></b-col>
      </b-row>
    </div>
  </div>
</template>

<script>
import PerformersHeadings from '@/components/PerformersHeadings.vue'
import ComposerList from '@/components/ComposerList.vue'
import WorkList from '@/components/WorkList.vue'
import AlbumList from '@/components/AlbumList.vue'
import WordCloud from '@/components/WordCloud.vue'

import {eventBus} from "../main.js";

export default {
  name: 'PerformerView',
  components: {
    PerformersHeadings,
    ComposerList,
    WorkList,
    AlbumList,
    WordCloud
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
  created() {
    window.firstLoad = false; // allow playback on first load for performer view
    eventBus.$on('fireArtistComposers', this.hideCloud);
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
