<template>
<div class="container-fluid">
      <b-row>
        <b-col><b-jumbotron class="jumbotron-heading" lead="Composers"></b-jumbotron></b-col>
        <b-col><b-jumbotron class="jumbotron-heading" :lead="work_heading"></b-jumbotron></b-col>
        <b-col><b-jumbotron class="jumbotron-heading" :lead="album_heading"></b-jumbotron></b-col>
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
.jumbotron-heading{
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
