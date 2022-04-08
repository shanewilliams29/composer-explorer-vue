<template>
  <div>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
  <div v-if="works">
  <div class ="row">
    <b-card-group deck v-show="!loading">
      <b-card v-for="(genre, index) in works" :key="index" no-body header-tag="header">
        <template #header>
          <h6 class="mb-0">{{ index }}</h6>
        </template>
        <b-card-text>
        <table cellspacing="0">
          <tr v-for="work in genre" :key="work.id" @click="selectRow(work.id); getAlbums(work.id, work.title);" :class="{'highlight': (work.id == selectedWork)}">
            <td width="17%"><span style="white-space: nowrap; color:darkred;"><span v-if="work.cat">{{ work.cat }}</span><span v-else>{{ work.date }}</span><span v-show="work.id == selectedWork">&nbsp;<b-icon icon="heart"></b-icon>&nbsp;</span></span></td>
            <td width="78%" style="white-space: nowrap; text-overflow:ellipsis; overflow: hidden; max-width:1px;">{{ work.title }}<span v-if="work.nickname" style="color:gray;"> · {{ work.nickname }}</span></td>
            <td width="5%" style="text-align: right;"><b-badge>{{ work.album_count }}</b-badge></td>
          </tr>
        </table>
        </b-card-text>
      </b-card>
    </b-card-group>
  </div>
  </div>
  <div v-else>
    <div class ="row">
    <div class="text-center" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
    <span v-show="!loading" class="no-works-found"><br>Works not yet catalogued for {{ composer }}.</span>
    </div>
  </div>
</div>
</template>

<script>
import axios from 'axios';
import {eventBus} from "../main.js";

export default {
  data() {
    return {
      works: [],
      loading: false,
      selectedWork: null
    };
  },
  methods: {
    getWorks(composer) {
      this.loading = true;
      const path = 'http://localhost:5000/api/works/' + composer;
      axios.get(path)
        .then((res) => {
          this.works = res.data.works;
          this.composer = composer;
          this.loading = false;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading = false;
        });
    },
      getAlbums(work_id, title) {
        eventBus.$emit('fireAlbums', work_id, title);
        eventBus.title = title;
    },
      selectRow(work){
        this.selectedWork = work;
    },
  },
  created() {
    this.getWorks('Beethoven');
    this.selectRow("BEETHOVEN00016");
    eventBus.$on('fireComposers', (composer) => {
            this.getWorks(composer);
    })
  },
};
</script>


<style scoped>
.spinner{
  text-align: center;
}
.m-5{
  color: #343a40;
}
.card-deck{
  display: flex;
  flex-direction: column;
  width: 100%;
}
.card{
  width: 100%;
}
td{
   padding: 1px;
   vertical-align: bottom;
   border-top: 1px dotted lightgray;
}
tr{
  border-bottom: 0px;
}
table{
   width: 100%;
   border-collapse: separate;
   font-size: 12px;
   padding: 6px;
   padding-bottom: 2px;
}
.highlight td {
  border-top: 0px solid lightgray;
  background-color: rgb(52, 58, 64, 0.7);
  color: white !important;
}
.highlight span {
  color: white !important;
}
tr:hover {
  cursor: pointer;
}

.highlight td:first-child,
.highlight td:last-child {
   position: relative;
}

.highlight td:first-child:before,
.highlight td:last-child:after {
  content: '';
  position: absolute;
  top: 0px;
  bottom: 0px;
  width: 6px;
  display: block;
  background: inherit;
  border: inherit;
}
.highlight td:first-child:before{
  right: 100%;
}
.highlight td:last-child:after{
  left: 100%;
}
header.card-header{
  background-color: #fff;
  border: none;
  padding-left: 10px;
  padding-bottom: 0px;
}
.mb-0{
  font-size: 14px;
  font-weight: bold;
}
.card{
  background-color: #fff;
  border: none;
  margin-top: 5px;
}
.card-deck{
  padding-left: 5px;
  padding-right: 5px;
}
.badge{
  color: #fff;
  background-color: rgb(52, 58, 64, 0.7);
  border-radius: 7px;
}
.no-works-found{
  font-size: 14px;
  color: grey;
  text-align: center;
}
</style>
