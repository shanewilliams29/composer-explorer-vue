<template>
  <div class ="row">
    <b-card-group deck>
      <b-card v-for="(region, index) in composers" :key="index" no-body header-tag="header">
        <template #header>
          <h6 class="mb-0">{{ index }}</h6>
        </template>
        <b-card-text>
        <table cellspacing="0">
           <tr v-for="(composer, index) in region" :key="index">
            <td width="2%" :style="{border: 'solid 0px !important', backgroundColor:composer.color, opacity: 0.66}">
             </td>
                  <td width="2%"></td>
             <td width="12%" style="white-space: nowrap;">
                <img class="composer-img" :src="composer.flag" height="20" width="20">
                <img class="composer-img" :src="composer.img" height="20" width="20">
             </td>
            <td width="50%" style="white-space: nowrap; text-overflow:ellipsis; overflow: hidden; max-width:1px;"><a @click="getWorks(composer.name_short)" :id="composer.name_short" style="cursor: pointer; color:black;">{{ composer.name_full }}</a></td>
           <td width="25%" style="white-space: nowrap; text-overflow:ellipsis; overflow: hidden; max-width:1px; text-align: right;">{{ composer.born }} - {{ composer.died }}</td>
           </tr>
        </table>
        </b-card-text>
      </b-card>
    </b-card-group>
  </div>
</template>

<script>
import axios from 'axios';
import {eventBus} from "../main.js";

export default {
  data() {
    return {
      composers: [],
    };
  },
  methods: {
    getComposers() {
      const path = 'http://localhost:5000/api/composers';
      axios.get(path)
        .then((res) => {
          this.composers = res.data.composers;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    getWorks(composer) {
        eventBus.$emit('fireMethod', composer);
    }
  },
  created() {
    this.getComposers();
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
</style>
