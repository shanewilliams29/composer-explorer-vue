<template>
<div class="container-fluid">
      <b-row class="footer-row">
        <b-col class="info-col">
  <b-card no-body bg-variant="dark">
    <b-row no-gutters>
      <b-col cols="12" md="auto">
        <b-card-img :src="composer_img" alt="Image" class="rounded-0"></b-card-img>
      </b-col>
      <b-col>
        <b-card-body>
          <b-card-text>
            {{ composer_info }}
          </b-card-text>
        </b-card-body>
      </b-col>
    </b-row>
  </b-card>
        </b-col>
        <b-col>Player</b-col>
        <b-col>Tracks</b-col>
      </b-row>
    </div>
</template>

<script>
import axios from 'axios';
import {eventBus} from "../main.js";

export default {
  data() {
    return {
      composer_img: "",
      composer_info: ""
    };
  },
  methods: {
    getComposerInfo(composer) {
        const path = 'http://localhost:5000/api/composerinfo/' + composer;
        axios.get(path)
          .then((res) => {
            this.composer_img = res.data.data.image;
            this.composer_info = res.data.data.introduction;
          })
          .catch((error) => {
            // eslint-disable-next-line
            console.error(error);
          });
      },
  },
  created() {
    this.getComposerInfo("Beethoven");
    eventBus.$on('fireMethod', (composer) => {
        this.getComposerInfo(composer);
    })
  },
};
</script>

<style scoped>
.info-col{
  height: 100px;
  overflow-y: scroll;
}
.card{
  background: none !important;
  border: 0px;
  width: 100%;
  overflow-x: hidden;

}
.card-img{
    height: auto;
    width: auto;
    max-width: 100px;
    max-height: 100px;
}
.card-title {
    font-size: 12px;
}
.card-body {
    font-size: 12px;
    padding-left: 0px;
    padding-top: 7px;


}
.footer-row{
  height: 100px;
  color: white;
  background-color: rgb(52, 58, 64, 0.85);

}
.lead{
  font-weight: 500;
  font-size: 14px;
  margin: 0px;
  padding-left: 10px;
  padding-bottom: 1px;
}
.col{
  padding:  0px;
}
</style>
