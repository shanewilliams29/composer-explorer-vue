<template>
  <b-card class="album-info-card shadow-sm">
    <b-card-body class="card-body">
      <b-card-title class="card-title">
        <table v-if="album.release_date">
          <tr class="heading-tr" @click="goToAlbum(album)">
            <td>
              <b-avatar square size="60px" :src="album.album_img"></b-avatar>
            </td>
            <td class="heading-td">
              {{ album.album_name }}<br />
              <span class="album-details">
                ℗ {{album.release_date.slice(0,4)}} · {{ album.label }}
              </span>
            </td>
          </tr>
        </table>
      </b-card-title>
        <b-row>
        <div id="dummy-div">
          <b-col class="cards-col">
            <div class="grid-container disable-scrollbars">
              <div class="grid-item" v-for="artist in artists" :key="artist.id" @click="getArtistComposers(artist)">
                <b-card class="album-info-card">
                  <b-card-body class="card-body centered-content">
                    <b-card-text class="info-card-text disable-scrollbars">
                      <div>
                        <table class="margin-bottom">
                          <tr>
                            <td class="vertical-align-middle">
                              <b-avatar size="36px" :src="artist.img"></b-avatar>
                            </td>
                            <td class="info-td vertical-align-middle">
                              <div class="wrap-text">
                              <a class="artist-name" >{{ artist.name }}</a><br />
                              <span v-if="artist.description !== 'NA'" class="born-died">{{artist.description}}<br></span>
                              </div>
                            </td>
                          </tr>
                        </table>
                      </div>
                    </b-card-text>
                  </b-card-body>
                </b-card>
              </div>
            </div>
          </b-col>
        </div>
        </b-row>
    </b-card-body>
  </b-card>
</template>

<script>
import { eventBus } from "@/main.js";

export default {
  data() {
    return {
      artists: [],
      album: {},
      loading: false
    };
  },
  methods: {
    goToAlbum(album) {
      if (!this.$view.mobile) {
          this.$router.push("/albums?id=" + album.album_id);
      } else {
        this.$router.push("/mobilealbums?id=" + album.album_id);
        this.$emit('togglePanel');
      }
    },
    getArtistComposers(artist) {
      if (!this.$view.mobile) {
        this.$config.artist = artist;
        if (this.$route.name != "performers") {
          this.$router.push("/performers?artist=" + artist.id);
        } else {
          eventBus.$emit("requestPerformer", artist);
        }
      } else {
        this.$config.artist = artist;
        if (this.$route.name != "mobileperformers") {
          this.$router.push("/mobileperformers?artist=" + artist.id);
        } else {
          eventBus.$emit("requestPerformer", artist);
        }
        this.$emit('togglePanel');
      }
    },
    setAlbumInfo(album) {
      this.album = album;
      this.artists = album.artist_details;
    }
  },
  created() {
    this.setAlbumInfo(this.$config.albumData);
    eventBus.$on("fireSetAlbum", this.setAlbumInfo); 
    eventBus.$on("fireSetAlbumHopper", this.setAlbumInfo);
  },
  beforeDestroy() {
    eventBus.$off("fireSetAlbum", this.setAlbumInfo);
    eventBus.$off("fireSetAlbumHopper", this.setAlbumInfo);
  },
};
</script>

<style scoped>
.heading-tr {
  vertical-align: middle;
  height: 62px !important;
  cursor: pointer;
}
.heading-td {
  padding-left: 10px;
  font-size: 16px;
}
.card-title {
  font-size: 16px;
  height: 62px;
}

.album-details {
  font-size: 14px !important;
  color: grey !important;
  font-family: Roboto Condensed !important;
}
.card-body {
  background-color: var(--my-white) !important;
  --scroll-bar-bg-color: var(--light-gray);
}

.disable-scrollbars::-webkit-scrollbar {
  background: transparent; /* Chrome/Safari/Webkit */
  width: 0px;
}
    
.disable-scrollbars {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none;  /* IE 10+ */
}


/* Performers grid */

#dummy-div {
  background: none;
  width: 100%;
  height: auto;
}

.album-info-card .card-body{
  background: none !important;
  padding: 0px !important;
}
.centered-content {
    display: flex;
    align-items: center;
    height: 100%; /* You might need to adjust this */
  }
.vertical-align-middle {
    vertical-align: middle;
    line-height: 100%;
}
.narrow{
  font-family: Roboto Condensed !important;
 }
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  grid-gap: 0px;
  grid-auto-flow: dense;
  height: auto;
  overflow-x: hidden;
  overflow-y: auto;
  padding-right: 15px;
  padding-left: 15px;
  padding-bottom: 0px;
  padding-top: 0px;
}
.grid-item {
  display: flex;
  padding-left: 0px;
  padding-right: 0px;
  padding-bottom: 0px;
  vertical-align: middle;
}
.album-info-card {
  margin-top: 0px;
  background-color: var(--my-white) !important;
  border: none !important;
  width: 100%;
}
.info-card-text {
  vertical-align: middle !important;
  font-size: 13px;
  line-height: 100% !important;
  padding-left: 2px;
}
.info-td {
  padding-left: 5px;
  text-overflow: ellipsis;
}
.wrap-text {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
}
.born-died {
  font-size: 13px !important;
  color: grey !important;
  font-family: Roboto Condensed !important;
  line-height: 80% !important;
}
a {
  color: black !important;
  font-weight: 600;
  font-size: 14px;
}
a:hover {
  text-decoration: none !important;
}
.margin-bottom {
  margin-bottom: 6px;
}
.cards-col{
  padding: 0px;
  padding-left: 0px;
}
.card .album-info-card{
  padding-left: 0px !important;
  padding-right: 5px !important;
  padding-top: 0px !important;
  padding-bottom: 5px !important;
}
</style>
