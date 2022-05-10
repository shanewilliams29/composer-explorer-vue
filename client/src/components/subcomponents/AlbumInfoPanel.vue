<template>
  <div>
    <b-card class="album-info-card shadow-sm">
      <b-card-body class="card-body">
        <b-card-title class="card-title">
          <table>
            <tr class="heading-tr">
              <td class="heading-td">
                {{ album.name }}<br />
                <span class="born-died">
                  ℗ {{album.release_date.slice(0,4)}} · {{ album.label }}
                </span>
              </td>
            </tr>
          </table>
        </b-card-title>
        <b-card-text class="info-card-text">
      <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
     </div>
          <div v-for="result in results" :key="result[0]">
            <table v-show="!loading">
              <tr>
                <td>
                  <b-avatar size="40px" :src="result[2]"></b-avatar>
                </td>
                <td class="info-td">
                  <a clss="artist-name" @click="getArtistComposers(result[0])">{{ result[0] }}</a><br />
                  <span class="born-died">{{result[1]}}</span>
                </td>
              </tr>
            </table>
          </div>
        </b-card-text>
      </b-card-body>
    </b-card>
  </div>
</template>

<script>
import axios from 'axios';
import {eventBus} from "../../main.js";
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
      const path = 'https://kgsearch.googleapis.com/v1/entities:search?indent=true&types=Person&types=MusicGroup&query=' + person + ' Music&limit=50&key=' + this.$auth.knowledgeKey;
      axios({
        method: 'get',
        url: path,
      }).then((res) => {
        let imageUrl = '';
        let description = '';
        this.loading = false;
        if (res.data.itemListElement[0] != null) {
          for (var i = 0; i < res.data.itemListElement.length; i++) {
            var personMatch = person.replace('Sir','').replace('Dame','').trim();
            if (res.data.itemListElement[i].result.name.includes(personMatch)) {
              let rank = 0
              if ('image' in res.data.itemListElement[i].result) {
                imageUrl = res.data.itemListElement[i].result.image.contentUrl;
                rank = rank + 1;
              } else {
                imageUrl = '';
              }
              if ('description' in res.data.itemListElement[i].result) {
                description = res.data.itemListElement[i].result.description;
                rank = rank + 1;
              } else {
                description = '';
              }
              this.results.push([person, description, imageUrl, rank]);
              this.results.sort(function(a, b) {
                return b[3] - a[3]
              });
              break;
            }
            if (i == res.data.itemListElement.length - 1) {
              this.results.push([person, '', '', -1]);
              this.results.sort(function(a, b) {
                return b[3] - a[3]
              });
            }
          }
        } else {
          //console.log(person);
          this.results.push([person, '', '', -1]);
          this.results.sort(function(a, b) {
            return b[3] - a[3]
          });
        }
      }).catch((error) => {
        console.error(error);
          this.loading = false;
          this.results.push([person, '', '', -1]);
          this.results.sort(function(a, b) {
            return b[3] - a[3]
          });
      });
    },
    getArtistComposers(artist) {
      eventBus.$emit('fireArtistComposers', artist);
      this.$config.artist = artist;
      if (this.$route.name != 'performers') {
        this.$router.push('/performers?artist=' + artist);
      }
    },
    setSpotifyAlbum(album) { // spotify album
      this.album = album;
    },
    getSpotifyArtistIDs(album) { // not used
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
      spotify.getSpotifyArtists(this.$auth.appToken, artistIDsString.trim());
    },
    getSpotifyAlbumData(album) { // database album object
      this.loading = true;
      this.results = [];
      this.artists = album.all_artists.split(", ");
      let album_id = album.album_uri.substring(album.album_uri.lastIndexOf(':') + 1);
      spotify.getSpotifyAlbum(this.$auth.appToken, album_id);
      this.artists.forEach(element => this.getPersonInfo(element));
    },
    setSpotifyArtistsData(artistList) { //not used
      this.results = []
      for (var i = 0; i < artistList.length; i++) {
        this.results.push([artistList[i]['name'], "", artistList[i]['images'][1]['url'], 0])
      }
      this.loading = false;
    }
  },
  created() {
    this.getSpotifyAlbumData(this.$config.albumData);
    eventBus.$on('fireSetAlbum', this.getSpotifyAlbumData);
    eventBus.$on('fireSpotifyAlbumData', this.setSpotifyAlbum);
  },
  beforeDestroy(){
    eventBus.$off('fireSetAlbum', this.getSpotifyAlbumData);
    eventBus.$off('fireSpotifyAlbumData', this.setSpotifyAlbum);
  }
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
  height: 20px;
}

/*scrollbars*/
 .info-card-text {
        --scroll-bar-color: #d6d9db;
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
