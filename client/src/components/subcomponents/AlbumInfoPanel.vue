<template>
<div>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
        <b-card class="album-info-card" v-if="!loading">
          <b-card-body class="card-body">
   <b-card-title class="card-title">
              <table>
                <tr class="heading-tr">
                  <td class="heading-td">
                    {{ album.name }}<br>
                    <span class="born-died"><a :href="album.external_urls.spotify" target="_blank"><img class="spotify-logo" src="@/assets/Spotify_Logo_RGB_Black.png"></a> {{ album.label }} ℗ {{album.release_date.slice(0,4)}}</span>
                  </td>
                </tr>
              </table>
              </b-card-title>
<b-card-text class="info-card-text">
  <div class="disclaimer"><b-badge variant="warning">BETA </b-badge><span class="born-died">&nbsp; Some information may not be correct.</span></div>
  <div v-for="result in results" :key="result[0]" >
              <table>
                <tr>
                  <td>

                <b-avatar size="40px" :src="result[2]"></b-avatar>

                  </td>
                  <td class="info-td">
                    <a clss="artist-name" @click="getArtistComposers(result[0])">{{ result[0] }}</a><br>
                  <span class="born-died">{{result[1]}}</span>
                  </td>
                </tr>
              </table>
            </div>
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
import {spotifyConfig} from "../../main.js";
import spotify from '@/SpotifyFunctions.js'

export default {
  data() {
    return {
      loading: true,
      artists: [],
      results: [],
      album: {}
    };
  },
  methods: {
  getPersonInfo(person) {

  this.loading = true;
  const path = 'https://kgsearch.googleapis.com/v1/entities:search?indent=true&types=Person&types=MusicGroup&query=' + person + ' Music&limit=50&key=AIzaSyA91Endg_KkrNGhkqcrW5evkG1p7y6CA08';
  axios({
      method: 'get',
      url: path,
    })
    .then((res) => {
      let imageUrl = '';
      let description = '';
      this.loading = false;

      if (res.data.itemListElement[0] != null) {

        for (var i = 0; i < res.data.itemListElement.length; i++) {
          if (res.data.itemListElement[i].result.name.slice(-8).includes(person.slice(-8))) {
              //console.log(res.data.itemListElement[i].result.name + " vs " + person)
    let rank = 0

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

        this.results.push([person, description, imageUrl, rank]);
        this.results.sort(function(a,b){return b[3] - a[3]});

        break;

          }
          if (i == res.data.itemListElement.length - 1) {
            this.results.push([person, '', '', -1]);
            this.results.sort(function(a,b){return b[3] - a[3]});
          }
        }
      } else {
        //console.log(person);
        this.results.push([person, '', '', -1]);
        this.results.sort(function(a,b){return b[3] - a[3]});
      }


    })
    .catch((error) => {
      console.error(error);
    });
  },

  getArtistComposers(artist){
    eventBus.$emit('fireArtistComposers', artist);
  },
  setSpotifyAlbum(album){ // spotify album
    this.album = album;
  },
  getSpotifyArtistIDs(album){ // not used
    let artistsList = album.artists;
    let artistIDsString = ""

    for (var i = 0; i < artistsList.length; i++) {
      if (i == 0) {
        artistIDsString = artistsList[i]['id'];
      } else {
        artistIDsString = artistIDsString + "," + artistsList[i]['id'];
      }
    }
    //console.log(artistIDsString);
    spotify.getSpotifyArtists(spotifyConfig.appToken, artistIDsString.trim());
  },
  getSpotifyAlbumData(album){ // database album
      this.loading = true;
      this.results = [];
      this.artists = album.all_artists.split(", ");
      let album_id = album.album_uri.substring(album.album_uri.lastIndexOf(':') + 1);
      spotify.getSpotifyAlbum(spotifyConfig.appToken, album_id);
      this.artists.forEach(element => this.getPersonInfo(element));
  },
  setSpotifyArtistsData(artistList){ //not used
    this.results = []
    for (var i = 0; i < artistList.length; i++) {
      this.results.push([artistList[i]['name'], "", artistList[i]['images'][1]['url'], 0])
    }
    this.loading = false;
    console.log(this.results);
  }
},
  created() {
    eventBus.$on('fireSetAlbum', this.getSpotifyAlbumData);
    eventBus.$on('fireSpotifyAlbumData', this.setSpotifyAlbum);
    // eventBus.$on('fireSpotifyArtistList', this.setSpotifyArtistsData);

  },
};
</script>

<style scoped>
a{
  color: black !important;
  font-weight: 600;
  font-size: 14px;
}
a:hover{
  color: black !important;
  text-decoration: underline !important;
  cursor: pointer;
}
.heading-tr{
  vertical-align: middle;
  height: 62px !important;
}
.heading-td{
  padding-left: 2px !important;

}
.spinner {
  text-align: center;
}
.m-5 {
  color: #343a40;
}
.born-died{
  font-size: 13px !important;
  color: grey !important;
}
.album-info-card{
  padding: 15px;
  padding-bottom: 10px;
  background-color: white !important;
  border: none !important;

}
.info-td{
  padding-left: 10px;
}




.disclaimer{
  margin-bottom: 11px;
}
.card-title{
  font-size: 16px;
  height:  62px;
}
.card-body{
  background-color: white !important;
  --scroll-bar-bg-color: #f1f2f4;
}

.info-card-text{
  font-size: 13px;
  line-height: 130%;
  overflow-y: scroll;
  height: 190px;
  padding-left: 2px;
}
table{
  margin-bottom: 6px;
}
.wiki-link{
  font-style: italic;
  color: grey;
}
.open-in-spotify{
  font-size: 12px;
}
.spotify-logo{
  width: auto;
  height: 18px;
}

/*scrollbars*/
 .info-card-text {
        --scroll-bar-color: #c1c2c3;
        --scroll-bar-bg-color: #fff;
    }

    .info-card-text{
        scrollbar-width: thin;
        scrollbar-color: var(--scroll-bar-color) var(--scroll-bar-bg-color) !important;
    }

    /* Works on Chrome, Edge, and Safari */
    .info-card-text::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }

    .info-card-text::-webkit-scrollbar-track {
        background: var(--scroll-bar-bg-color) !important;
    }

    .info-card-text::-webkit-scrollbar-thumb {
        background-color: var(--scroll-bar-color);
        border-radius: 20px;
        border: 3px solid var(--scroll-bar-bg-color)!important;
    }


</style>
