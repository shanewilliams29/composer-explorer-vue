<template>
  <div>
    <div class="container-fluid">
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
      page: 2,
      infiniteId: +new Date(),
      currentAlbum: 0,
      workId: "WAGNER00012"
    };
  },
  methods:{
    getAlbums(id) {
      this.loading = true;

      const path = "api/albumsview/" + id;
      axios
        .get(path)
        .then((res) => {
          this.loading = false;
          this.albums = res.data.albums;
          this.message = "";
        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },
    infiniteHandler($state) {
        const path = "api/albumsview/" + this.workId + "?page=" + this.page;
        axios.get(path).then(({ data }) => {
          if (data.albums.length) {
            this.page += 1;
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
    this.getAlbums(this.workId);
  },
  created() {

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
}
.spinner {
  text-align: center;
}
.m-5 {
    color: #9da6af;
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

