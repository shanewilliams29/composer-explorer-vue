<template>
<div>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
        <b-card class="album-info-card" v-show="!loading">
          <b-card-body class="card-body">
 <b-card-title v-for="(result, index) in results" :key="index" class="card-title">
              <table>
                <tr>
                  <td>

                <b-avatar size="40px" :src="result[2]"></b-avatar>

                  </td>
                  <td class="info-td">
                    <a @click="getArtistComposers(result[0])">{{ result[0] }}</a><br>
                  <span class="born-died">{{result[1]}}</span>
                  </td>
                </tr>
              </table>
              </b-card-title>

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
      artists: [],
      results: [],
    };
  },
  methods: {
  getPersonInfo(person) {

  this.loading = true;
  const path = 'https://kgsearch.googleapis.com/v1/entities:search?indent=true&types=Person&types=MusicGroup&query=' + person + ' Music&limit=1&key=AIzaSyA91Endg_KkrNGhkqcrW5evkG1p7y6CA08';
  axios({
      method: 'get',
      url: path,
    })
    .then((res) => {
      let imageUrl = '';
      let description = '';
      this.loading = false;


    let rank = 0
      if (res.data.itemListElement[0] != null) {
          if ('image' in res.data.itemListElement[0].result) {
             imageUrl = res.data.itemListElement[0].result.image.contentUrl;
             rank = rank + 1;
           }else {
              imageUrl = '';
           }
          if ('description' in res.data.itemListElement[0].result) {
             description = res.data.itemListElement[0].result.description;
             rank = rank + 1;
           }else {
              description = '';
           }
       }
      this.results.push([person, description, imageUrl, rank]);
      this.results.sort(function(a,b){return b[3] - a[3]});
    })
    .catch((error) => {
      console.error(error);
    });
  },

  getArtistComposers(artist){
    eventBus.$emit('fireArtistComposers', artist);
  },
},
  created() {
    this.loading = true;
    eventBus.$on('fireSetAlbum', (album) => {
      this.loading = true;
      this.results = [];
      this.artists = album.all_artists.split(", ");
      //console.log(this.artists);
      this.artists.forEach(element => this.getPersonInfo(element));

      //this.results = this.results.reverse();
      //console.log(this.results);
    })
    // eslint-disable-next-line
    eventBus.$on('expandInfoPanel', (composer, workId) => {
      this.loading = false;
      // this.getWorkInfo(workId);
    })
  },
};
</script>

<style scoped>
a{
  color: black !important;
}
a:hover{
  color: black !important;
  text-decoration: underline !important;
  cursor: pointer;
}
.info-td{
  padding-left: 10px;
}
.spinner {
  text-align: center;
}
.m-5 {
  color: #343a40;
}
.born-died{
  font-size: 14px !important;
  color: grey !important;
}
.album-info-card{
  padding: 15px;
  padding-bottom: 10px;
  background-color: white !important;
  border: none !important;

}
.card-title{
  font-size: 16px;
}
.card-body{
  height: 263px;
  overflow-y: scroll;
  background-color: white !important;
}
.card-body {
    -ms-overflow-style: none;  /* Internet Explorer 10+ */
    scrollbar-width: none;  /* Firefox */
}
.card-body::-webkit-scrollbar {
    display: none;  /* Safari and Chrome */
}
.wiki-link{
  font-style: italic;
  color: grey;
}
</style>
