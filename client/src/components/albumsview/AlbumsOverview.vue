<template>
  <div>
    <div class="container-fluid">
    <h6 class="message">
      {{ message }}
    </h6>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
      <div v-show="!loading" class="grid-container">
        <div class="grid-item" v-for="album in albums" :key="album.album_id">
          <img class="album-cover" height="auto" v-lazy="album.img_big" />
        </div>
        <infinite-loading spinner="spiral" :identifier="infiniteId" @infinite="infiniteHandler">
          <div slot="no-more"></div>
          <div slot="no-results"></div>
        </infinite-loading>
      </div>
    </div>
  </div>
</template>

<script>
import { eventBus } from "@/main.js";
import axios from "axios";

export default {
  data() {
    return {
      albums: [],
      loading: false,
      selectedAlbum: null,
      sort: "",
      message: "",
      page: 1,
      infiniteId: +new Date(),
      currentAlbum: 0,
      workId: "WAGNER00012",
      params: {}
    };
  },
  methods:{
    messageBuilder(status, composer, period, artist, work, sort){
      if (status == 'success'){
        let message = "Albums"
        if (!composer && ! period && !artist && !work || period == 'all'){
          return (sort == 'popular' || !sort) ? "Popular albums" : ((sort == 'newest') ? "New releases" : "Historical recordings");
        }
        if (composer) {
          message = message + " featuring " + composer;
        } else if (period) {
          period = (period == '20th') ? "20th/21st century" : period;
          message = (period.charAt(0).toUpperCase() + period.slice(1)) + " music " + message.toLowerCase();
        }
        if (artist) {
          message = message + " with performances by " + artist;
        }
        if (work) {
          message = message + " with work titled \"" + work + "\"";
        }
        return message;
      } else {
        return "Error retrieving albums from database! Please try again later."
      }
    },
    getAlbums(composer, period, artist, work, sort) {
      this.loading = true;
      this.params['page'] = 1;
      this.params['composer'] = composer;
      this.params['period'] = period;
      this.params['artist'] = artist;
      this.params['work'] = work;
      this.params['sort'] = sort;

      const params = this.params;
      const path = "api/albumsview";
      axios
        .get(path, {params})
        .then((res) => {
          this.loading = false;
          this.albums = res.data.albums;
          if (this.albums.length > 0) {
            this.message = this.messageBuilder('success', composer, period, artist, work, sort);
          } else {
            this.message = "No albums found for query."
          }
          if (res.data.works.length > 0) {
            this.$lists.albumViewWorks = res.data.works;
          } else {
            this.$lists.albumViewWorks = this.$lists.workList;
          }
          
          this.params['page'] += 1;
        })
        .catch((error) => {
          this.message = this.messageBuilder('error');
          console.error(error);
          this.loading = false;
        });
    },
    infiniteHandler($state) {
      const params = this.params;
        const path = "api/albumsview";
        axios
          .get(path, {params})
          .then(({ data }) => {
            if (data.albums.length) {
              this.params['page'] += 1;
              this.albums.push(...data.albums);
              $state.loaded();
            } else {
              $state.complete();
            }
          });
    },
    shuffleArray(array) {
      for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
      }
      return array.slice(0,30);
    },
    toK(num){
      return num.toString().slice(0, -3) + "k";
    },
    wordClick(word){
      eventBus.$emit('requestComposersForArtist', word);
    }
  },
  mounted(){
    this.getAlbums(null, null, null);
  },
  created() {
    eventBus.$on("requestAlbumViewAlbums", this.getAlbums);
  },
  beforeDestroy() {
    eventBus.$off("requestAlbumViewAlbums", this.getAlbums);
  },
}
</script>

<style scoped>

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  grid-gap: 10px;
  grid-auto-flow: dense;
  padding-top: 10px;
}

.grid-item {
  display: flex;
}

.album-cover {
  width: 100%;
  height: auto;
  box-shadow: rgba(0, 0, 0, 0.2) 0px 1px 4px;
}
.spinner {
  text-align: center;
}
.m-5 {
    color: #9da6af;
}
.message{
  margin-top: 10px;
  text-align: center;
  margin-bottom: 0px;
  color: var(--medium-gray);
}
.album-info-card {
  margin-top: 5px;
  padding: 10px;
  padding-bottom: 5px;
  background-color: var(--my-white) !important;
  border: none !important;
  width: 100%;
}
.info-card-text {
  font-size: 13px;
  line-height: 130%;
  padding-left: 2px;
}
.info-td {
  padding-left: 10px;
}
.born-died {
  font-size: 13px !important;
  color: grey !important;
}
a {
  color: black !important;
  font-weight: 600;
  font-size: 14px;
}
a:hover {
  color: black !important;
  text-decoration: underline !important;
  cursor: pointer;
}
table {
  margin-bottom: 6px;
}
.col{
  padding: 0px;
  padding-left: 5px;
}

</style>

