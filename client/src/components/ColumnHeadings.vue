<template>
<div class="container-fluid">
      <b-row>
        <b-col><b-jumbotron class="jumbotron-heading" lead="Composers"></b-jumbotron></b-col>
        <b-col><b-jumbotron class="jumbotron-heading" :lead="work_heading"></b-jumbotron></b-col>
        <b-col><b-jumbotron class="jumbotron-heading" lead="Albums"></b-jumbotron></b-col>
      </b-row>
    </div>
</template>

<script>
import {eventBus} from "../main.js";

export default {
  data() {
    return {
      work_heading: "",
    };
  },
  created() {
    this.work_heading = "Works by Beethoven";
    eventBus.$on('fireMethod', (composer) => {
        this.work_heading = "Works by " + composer;
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
  font-size: 18px;
  margin: 0px;
  padding-left: 12px;
  padding-bottom: 3px;
}
.col{
  padding:  0px;
}
</style>
