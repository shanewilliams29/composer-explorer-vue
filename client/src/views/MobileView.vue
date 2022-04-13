<template>
  <div id="home">
    <NavBar/>

  <div class="accordion" role="tablist">
    <b-card no-body class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <b-button block v-b-toggle.accordion-1 variant="secondary">Composers</b-button>
      </b-card-header>
      <b-collapse id="accordion-1" visible accordion="my-accordion" role="tabpanel">
        <b-card-body>
<b-col class="composer-list"><ComposerList/></b-col>
        </b-card-body>
      </b-collapse>
    </b-card>

    <b-card no-body class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <b-button block v-b-toggle.accordion-2 variant="secondary">Works</b-button>
      </b-card-header>
      <b-collapse id="accordion-2" accordion="my-accordion" role="tabpanel">
        <b-card-body>
<b-col class="work-list"><WorkList/></b-col>
        </b-card-body>
      </b-collapse>
    </b-card>

    <b-card no-body class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <b-button block v-b-toggle.accordion-3 variant="secondary">Recordings</b-button>
      </b-card-header>
      <b-collapse id="accordion-3" accordion="my-accordion" role="tabpanel">
        <b-card-body>
 <b-col class="album-list"><AlbumList/></b-col>
        </b-card-body>
      </b-collapse>
    </b-card>
  </div>

    <PageFooter/>
    <SpotifyPlayer/>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import ComposerList from '@/components/ComposerList.vue'
import WorkList from '@/components/WorkList.vue'
import AlbumList from '@/components/AlbumList.vue'
import PageFooter from '@/components/PageFooter.vue'
import SpotifyPlayer from '@/components/SpotifyPlayer.vue'
import axios from 'axios';
import {eventBus} from "../main.js";

export default {
  name: 'MobileView',
  components: {
    NavBar,
    ComposerList,
    WorkList,
    AlbumList,
    PageFooter,
    SpotifyPlayer
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
            eventBus.$emit('fireToken');
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
  created() {
    this.getSpotifyToken();
  },
}
</script>

<style scoped>
  .card-body{
    background: #f1f2f4 !important;
    padding: 0px !important;
  }
  #home{
    overflow-x: hidden;
    background: #f1f2f4 !important;
  }
  .composer-list{
    height: calc(100vh - 66px - 45px - 45px - 45px - 100px);
    overflow-y: scroll;
  }
  .work-list{
    height: calc(100vh - 66px - 45px - 45px - 45px - 100px);
    overflow-y: scroll;
  }
  .album-list{
    height: calc(100vh - 66px - 45px - 45px - 45px - 100px);
    overflow-y: scroll;
    overflow-x: hidden;
  }
</style>
