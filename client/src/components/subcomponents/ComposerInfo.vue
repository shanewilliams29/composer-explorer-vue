<template>
  <div>
      <div class="spinner" v-show="loading" role="status">
          <b-spinner class="m-5"></b-spinner>
      </div>
      <b-card class="composer-info-card shadow-sm" v-show="!loading">
          <b-card-body class="card-body">
              <b-card-title class="card-title">
                  <table>
                      <tr>
                          <td>
                              <b-avatar-group size="60px">
                                  <b-avatar :src="composer.region"></b-avatar>
                                  <b-avatar :src="composer.image"></b-avatar>
                              </b-avatar-group>
                          </td>
                          <td class="info-td">
                              {{ composer.name_full }}<br />
                              <span class="born-died">{{ composer.born }} - {{ composer.died }}</span>
                          </td>
                      </tr>
                  </table>
              </b-card-title>
              <b-card-text class="info-card-text">
                  {{ composer.introduction }}<br />
                  <a :href="composer.pageurl" target="_blank" class="wiki-link">
                      <br />
                      Read more on Wikipedia
                  </a>
              </b-card-text>
          </b-card-body>
      </b-card>
  </div>
</template>

<script>
import axios from 'axios';
import {eventBus} from "../../main.js";

export default {
  data() {
    return {
      loading: true,
      composer: {}
    };
  },
  methods: {
    getComposerInfo(composer) {
        this.loading = true;
        const path = 'api/composerinfo/' + composer;
        axios.get(path)
          .then((res) => {
            this.composer = res.data.info;
            this.loading = false;
          })
          .catch((error) => {
            // eslint-disable-next-line
            console.error(error);
            this.loading = false;
          });
      },
  },
  created() {
    this.loading = true;
    this.getComposerInfo(this.$config.composer);
    eventBus.$on('fireComposers', (composer) => {
      this.loading = true;
      this.getComposerInfo(composer);
    })
    eventBus.$on('fireArtistWorks', (artist, composer) => {
      this.loading = true;
      this.getComposerInfo(composer);
    })
  },
};
</script>

<style scoped>
.spinner {
  text-align: center;
}
.m-5 {
  color: #343a40;
}
.born-died{
  font-size: 15px !important;
  color: grey !important;
}
.composer-info-card{
  padding: 15px;
  padding-bottom: 10px;
  background-color: white !important;
  border: none !important;
}





.card-title{
  font-size: 16px;
}
.info-td{
  padding-left: 10px;
}
.card-body{
  background-color: white !important;
}



.info-card-text{
  font-size: 13px;
  line-height: 130%;
  overflow-y: scroll;
  height: 190px;
  padding-left: 5px;
}
.wiki-link{
  font-style: italic;
  color: grey;
}

/*scrollbars*/
 .info-card-text {
        --scroll-bar-color: #d6d9db;
        --scroll-bar-bg-color: #fff;
    }

    .info-card-text{
        scrollbar-width: thin;
        scrollbar-color: var(--scroll-bar-color) var(--scroll-bar-bg-color) !important;
    }

    /* Works on Chrome, Edge, and Safari */
    .info-card-text::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }

    .info-card-text::-webkit-scrollbar-track {
        background: var(--scroll-bar-bg-color) !important;
    }

    .info-card-text::-webkit-scrollbar-thumb {
        background-color: var(--scroll-bar-color);
        border-radius: 20px;
        border: 3px solid var(--scroll-bar-bg-color)!important;
    }


</style>
