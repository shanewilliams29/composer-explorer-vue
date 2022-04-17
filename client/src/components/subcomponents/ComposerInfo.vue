<template>
<div>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
        <b-card class="composer-info-card" v-show="!loading">
          <b-card-body class="card-body">
            <b-card-title class="card-title">
                <b-avatar size="60px" :src="composerImage"></b-avatar>&nbsp; {{ composerNameFull }}</b-card-title>
            <b-card-text class="info-card-text">
            {{ composerBlurb }}
            <a :href="wikiLink" target="_blank" class="wiki-link"><br>Read more on Wikipedia</a>
            </b-card-text>
          </b-card-body>
        </b-card>
</div>

<!--   <div class="composer-heading">
    <h6><b-avatar size="60px" src="https://storage.googleapis.com/composer-explorer.appspot.com/img/Beethoven.jpg"></b-avatar>&nbsp; Ludwig van Beethoven</h6>
  </div>
  <div class="composer-body">

  </div> -->

</template>

<script>
import axios from 'axios';
import {eventBus} from "../../main.js";

export default {
  data() {
    return {
      loading: true,
      composerNameFull: "",
      composerImage: "",
      composerBlurb: "",
      wikiLink: ""
    };
  },
  methods: {
    getComposerInfo(composer) {
        this.loading = true;
        const path = 'api/composerinfo/' + composer;
        axios.get(path)
          .then((res) => {
            this.composerNameFull = res.data.info.name_full;
            this.composerImage = res.data.info.image;
            this.composerBlurb = res.data.info.introduction;
            this.wikiLink = res.data.info.pageurl;
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
    eventBus.$on('fireComposers', (composer) => {
      this.loading = true;
      this.getComposerInfo(composer);
    })
    eventBus.$on('expandInfoPanel', (composer) => {
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
.composer-info-card{
  padding: 15px;
  padding-bottom: 10px;
  background-color: white !important;
  border: none !important;

}
.card-title{
  font-size: 20px;
}
.card-body{

  background-color: white !important;
}
.info-card-text{
  font-size: 13px;
  line-height: 130%;
  overflow-y: scroll;
  height: 190px;
}
.info-card-text {
    -ms-overflow-style: none;  /* Internet Explorer 10+ */
    scrollbar-width: none;  /* Firefox */
}
.info-card-text::-webkit-scrollbar {
    display: none;  /* Safari and Chrome */
}
.wiki-link{
  font-style: italic;
  color: grey;
}
</style>
