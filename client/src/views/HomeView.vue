<template>
  <div id="home">
    <NavBar/>
    <ColumnHeadings/>
    <div class="container-fluid">
      <b-row>
        <b-col class="composer-list"><ComposerList/></b-col>
        <b-col class="work-list"><WorkList/></b-col>
        <b-col cols="4" class="album-list"><AlbumList/></b-col>
      </b-row>
    </div>
    <div class="info-panel" v-show='showPanel'><InfoPanel/></div>
    <PageFooter/>
    <b-button class="info-panel-button float" @click="togglePanel()" variant="warning"><span v-if="!showPanel"><b-icon-chevron-up></b-icon-chevron-up></span><span v-else><b-icon-chevron-down></b-icon-chevron-down></span> INFO PANEL</b-button>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import ColumnHeadings from '@/components/ColumnHeadings.vue'
import ComposerList from '@/components/ComposerList.vue'
import WorkList from '@/components/WorkList.vue'
import AlbumList from '@/components/AlbumList.vue'
import PageFooter from '@/components/PageFooter.vue'
import InfoPanel from '@/components/InfoPanel.vue'

import axios from 'axios';
import {eventBus} from "../main.js";
import {currentConfig} from "../main.js";

export default {
  name: 'HomeView',
  components: {
    NavBar,
    ColumnHeadings,
    ComposerList,
    WorkList,
    AlbumList,
    PageFooter,
    InfoPanel
  },
  data() {
    return {
      showPanel: false
    };
  },
  methods: {
    getSpotifyToken() {
      const path = 'api/get_token';
      axios.get(path)
        .then((res) => {
          if (res.data.status == "success") {
            eventBus.$emit('fireToken');
            eventBus.spotifyToken = res.data.token;
          }
          console.log(eventBus.spotifyToken);
        })
        .catch((error) => {
          eventBus.spotifyToken = null;
          console.error(error);
        });
    },
    togglePanel(){
      this.showPanel = !this.showPanel;
      if (this.showPanel){
        document.documentElement.style.setProperty('--panelheight', `300px`);
        eventBus.$emit('expandInfoPanel', currentConfig.composer, currentConfig.work);
      } else{
        document.documentElement.style.setProperty('--panelheight', `0px`);
      }

    }
  },
  beforeCreate(){
    if( screen.width <= 760 ) {
        //this.$router.replace('mobile');
        window.location.replace('mobile');
    }
  document.documentElement.style.setProperty('--panelheight', `0px`);
  },
  created() {
    this.getSpotifyToken();
  },
}
</script>

<style>
  #home{
    overflow-x: hidden;
    background: #f1f2f4 !important;
  }
  .composer-list{
    height: calc(100vh - 66px - 114px - 100px - var(--panelheight));
    overflow-y: scroll;
  }
  .work-list{
    height: calc(100vh - 66px - 114px - 100px - var(--panelheight));
    overflow-y: scroll;
  }
  .album-list{
    height: calc(100vh - 66px - 114px - 100px - var(--panelheight));
    overflow-y: scroll;
    overflow-x: hidden;
  }
  .info-panel-button{
  font-size: 10px;
  border-radius: 0px;
  padding-top: 1px;
  padding-bottom: 1px;
  position:fixed;
  left: 50%;
  transform: translateX(-50%);
  bottom:92px;
  }
</style>
