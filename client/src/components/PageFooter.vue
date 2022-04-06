<template>
<div class="container-fluid">
      <b-row class="footer-row">
        <b-col class="info-col">
  <b-card no-body bg-variant="dark">
    <b-row no-gutters>
      <b-col cols="12" md="auto">
        <b-card-img src="https://storage.googleapis.com/composer-explorer.appspot.com/img/Beethoven.jpg" alt="Image" class="rounded-0"></b-card-img>
      </b-col>
      <b-col>
        <b-card-body>
          <b-card-text>
            Ludwig van Beethoven was a German composer and pianist. A crucial figure in the transition between the Classical and Romantic eras in classical music, he remains one of the most recognised and influential of all composers. His best-known compositions include 9 symphonies; 5 piano concertos; 1 violin concerto; 32 piano sonatas; 16 string quartets; a mass, the Missa solemnis; and an opera, Fidelio. His career as a composer is conventionally divided into early, middle, and late periods; the "early" period is typically seen to last until 1802, the "middle" period from 1802 to 1812, and the "late" period from 1812 to his death in 1827.

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
import {eventBus} from "../main.js";

export default {
  data() {
    return {
      work_heading: "",
      album_heading: ""
    };
  },
  created() {
    this.work_heading = "Works by Beethoven";
    this.album_heading = "Albums for \"Symphony No. 5 in C minor\"";
    eventBus.$on('fireMethod', (composer) => {
        this.work_heading = "Works by " + composer;
    })
    eventBus.$on('fireAlbums', (work_id, title) => {
        this.album_heading = "Albums for \"" + title + "\"";
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
