<template>
  <div v-if="works">
  <div class ="row">
    <b-card-group deck>
      <b-card v-for="(genre, index) in works" :key="index" no-body header-tag="header">
        <template #header>
          <h6 class="mb-0">{{ index }}</h6>
        </template>
        <b-card-text>
        <table cellspacing="0">
          <tr v-for="(work, index) in genre" :key="index">
            <td width="17%"><span style="white-space: nowrap; color:darkred;"><span v-if="work.cat">{{ work.cat }}</span><span v-else>{{ work.date }}</span></span></td>
            <td width="78%" style="white-space: nowrap; text-overflow:ellipsis; overflow: hidden; max-width:1px;"><a onclick='' style="cursor: pointer; color:black;">{{ work.title }}</a><span v-if="work.nickname" style="color:gray;"> · {{ work.nickname }}</span></td>
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
    <span class="no-works-found"><br>Works not yet catalogued for {{ composer }}.</span>
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
    };
  },
  methods: {
    getWorks(composer) {
      const path = 'http://localhost:5000/api/works/' + composer;
      axios.get(path)
        .then((res) => {
          this.works = res.data.works;
          this.composer = composer;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {
    this.getWorks('Beethoven');
    eventBus.$on('fireMethod', (composer) => {
            this.getWorks(composer);
    })
  },
};
</script>


<style scoped>
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
.composer-img{
    border-radius: 50%;
    object-fit: cover;
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
  background-color: #777777;
  border-radius: 7px;
}
.no-works-found{
  font-size: 14px;
  color: grey;
  text-align: center;
}
</style>
