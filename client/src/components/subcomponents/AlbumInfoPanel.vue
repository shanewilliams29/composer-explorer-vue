<template>
<div>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
        <b-card class="album-info-card" v-show="!loading">
          <b-card-body class="card-body">
 <b-card-title v-for="artist in artists" :key="artist.id" class="card-title">
              <table>
                <tr>
                  <td>

                <b-avatar size="40px" :src="artist.image"></b-avatar>

                  </td>
                  <td class="info-td">
                    {{ artist }}<br>
                    <span v-if="artist.description" class="born-died">Musician</span><span v-else class="born-died">Musician</span>
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
// import axios from 'axios';
import {eventBus} from "../../main.js";

export default {
  data() {
    return {
      loading: true,
      artists: []
    };
  },
  methods: {
},
  created() {
    this.loading = true;

    eventBus.$on('fireSetAlbum', (album) => {
      this.loading = false;
      this.artists = album.all_artists.split(", ");
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
