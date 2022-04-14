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
    <PageFooter/>

  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import ColumnHeadings from '@/components/ColumnHeadings.vue'
import ComposerList from '@/components/ComposerList.vue'
import WorkList from '@/components/WorkList.vue'
import AlbumList from '@/components/AlbumList.vue'
import PageFooter from '@/components/PageFooter.vue'

import axios from 'axios';
import {eventBus} from "../main.js";

export default {
  name: 'HomeView',
  components: {
    NavBar,
    ColumnHeadings,
    ComposerList,
    WorkList,
    AlbumList,
    PageFooter
  },
  data() {
    return {
    };
  },
  methods: {
    getSpotifyToken() {
      const path = 'api/get_token';
      axios.get(path)
        .then((res) => {
          if (res.data.status == "success") {
            // eventBus.$emit('fireToken');
            eventBus.spotifyToken = res.data.token;
          }
          console.log(eventBus.spotifyToken);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  beforeCreate(){
    if( screen.width <= 760 ) {
        //this.$router.replace('mobile');
        window.location.replace('mobile');
    } else {
      this.getSpotifyToken();
    }
  },
}
</script>

<style>
  #home{
    overflow-x: hidden;
    background: #f1f2f4 !important;
  }
  .composer-list{
    height: calc(100vh - 66px - 114px - 100px);
    overflow-y: scroll;
  }
  .work-list{
    height: calc(100vh - 66px - 114px - 100px);
    overflow-y: scroll;
  }
  .album-list{
    height: calc(100vh - 66px - 114px - 100px);
    overflow-y: scroll;
    overflow-x: hidden;
  }
</style>
