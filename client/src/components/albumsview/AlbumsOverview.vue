<template>
  <div>
      <!-- ALBUM POPUP -->
      <div v-for="album in albums" :key="album.album_id">
        <table>
        <tr class="popup" :class="{'reveal': (showAlbum == album.album_id)}">
          <td>
            <img class="album-popup-cover" :ref="album.album_id" :src="album.img_big" />
          </td>
          <td>
            <div class="image-caption">
              <tr>
              <span class="album-title">{{ album.album_name }} </span><br />
              <span class="album-details">℗ {{ album.release_date }} </span>
              <span class="album-details"> {{ album.label }} </span><br />
              <br />
              </tr>
              <tr v-show="!albumDataLoading && albumWorks.length > 0"
                v-for="work in albumWorks" :key="work.id">
              <span class="album-work-composer">{{ work.composer }} </span><br />
              <span class="album-work-title">{{ work.title }} </span><br />
              <span v-if="work.cat" class="album-work-cat">{{ work.cat }} <br/></span>
              <br/>
              </tr>
            </div>
          </td>          
        </tr>
      </table>
      </div>

        <!-- ALBUM POPUP -->
<!--       <Transition name="fade">
        <div>
        <div v-for="album in albums" :key="album.album_id">
          <div class="popup" :class="{'reveal': (showAlbum == album.album_id)}">
            <img class="album-popup-cover" :ref="album.album_id" :src="album.img_big" />
            <div class="image-caption">
              <span class="album-major-artists">{{ album.artists }}</span><br />
              <span v-if="album.minor_artists" class="album-minor-artists">{{ album.minor_artists }}</span>
            </div>
          </div>
        </div>
      </div>
      </Transition> -->

    <!-- ALBUM GRID -->
    <div class="container-fluid">
    <h6 class="message narrow">
       <div v-html="message" />
    </h6>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
      <div v-show="!loading" class="grid-container">
        <div class="grid-item" v-for="album in albums" :key="album.album_id">
          <img @click="showCover = album.album_id" class="album-cover" height="auto" v-lazy="album.img_big" />
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
      albumWorks: [],
      showCover: false,
      albumDataLoading: false,
      loading: false,
      message: "",
      page: 1,
      infiniteId: +new Date(),
      params: {}
    };
  },
  computed: {
    showAlbum() {
      if (this.showCover) {
        console.log(this.showCover);
        const imageWidth = this.$refs[this.showCover][0].width;
        if (imageWidth == 0) {
          return false;
        }
        this.getAlbumWorks(this.showCover);
        document.documentElement.style.setProperty("--imagewidth", imageWidth + 'px');
        return this.showCover;
      } else {
        return false;
      }
    }
  },
  methods: {
    messageBuilder(status, fieldData) {
      if (!fieldData || Object.keys(fieldData).length === 0) {
        return "Error retrieving albums from database! Please try again later.";
      }

      let composer = fieldData.composer;
      let period = fieldData.period;
      let artist = fieldData.artist;
      let work = fieldData.work;
      let sort = fieldData.sort;

      if (status == 'success') {
        let message = "Albums"
        if (!composer && !period && !artist && !work || period == 'all') {
          return (sort == 'popular' || !sort) ? "Popular albums" : ((sort == 'newest') ? "New releases" : "Historical recordings");
        }
        if (composer) {
          message = message + " featuring <b>" + composer + '</b>';
        } else if (period) {
          period = (period == '20th') ? "<b>20th/21st century</b>" : period;
          message = "<b>" + (period.charAt(0).toUpperCase() + period.slice(1)) + "</b> music " + message.toLowerCase();
        }
        if (artist) {
          message = message + " with performances by <b>" + artist + '</b>';
        }
        if (work) {
          message = message + " with work titled <b>" + work + "</b>";
        }
        return message;
      } else {
        return "Error retrieving albums from database! Please try again later."
      }
    },
    getAlbums(fieldData) {
      this.params = fieldData;
      this.params['page'] = 1;
      this.loading = true;

      const params = this.params;
      const path = "api/albumsview";
      axios
        .get(path, { params })
        .then((res) => {
          this.loading = false;
          this.albums = res.data.albums;
          if (this.albums.length > 0) {
            this.message = this.messageBuilder('success', fieldData);
          } else {
            if (fieldData.artist && fieldData.composer) {
              this.message = "No albums found for <b>" + fieldData.artist + "</b> performing <b>" + fieldData.composer + "</b>."
            } else {
              this.message = "No albums found for query."
            }
          }
          if (res.data.works.length > 0) {
            this.$lists.albumViewWorks = res.data.works;
          } else {
            this.$lists.albumViewWorks = this.$lists.workList;
          }

          this.params['page'] += 1;
        })
        .catch((error) => {
          this.loading = false;
          this.message = this.messageBuilder('error');
          console.log(this.message);
          console.error(error);
        });
    },
    getAlbumWorks(album_id){
      this.albumDataLoading = true;
      this.albumWorks = [];
      const params = {'album_id': album_id};
      const path = "api/getalbumworks";
      axios
        .get(path, { params })
        .then(({ data }) => {
          this.albumDataLoading = false;
          if (data.works.length) {
            this.albumWorks.push(...data.works);
          }
        })
        .catch((error) => {
          this.albumDataLoading = false;
          console.error(error);
        });
    },
    infiniteHandler($state) {
      const params = this.params;
      const path = "api/albumsview";
      axios
        .get(path, { params })
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
  },
  mounted() {
    this.getAlbums(this.params);
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
.fade-enter-active,
.fade-leave-active {
  transition: all 0.15s;
}

.fade-enter {
  opacity: 0;
}

.fade-leave-to {
  opacity: 0;
}

.album-title {
  color: var(--my-white) !important;
  font-weight: 600;
  font-size: 16px;
}

.album-details {
  color: var(--medium-light-gray) !important;
  font-size: 14px;
}

.album-work-composer{
  color: var(--orange) !important;
  font-size: 14px;
}

.album-work-title{
  color: var(--my-white) !important;
  font-weight: 600;
  font-size: 14px;
}

.album-work-cat{
  color: var(--medium-light-gray) !important;
  font-size: 12px;
}

.reveal {
  visibility: visible !important;
}

.popup {
  visibility: hidden;
  width: calc(var(--imagewidth) * 1.8);
  line-height: 16px;
  padding: 0px;
  position: fixed;
  top: calc(50% + 22.1px);
  left: 50%;
  transform: translate(-50%, -50%);
  box-shadow: rgba(0, 0, 0, 0.25) 0px 54px 55px, rgba(0, 0, 0, 0.12) 0px -12px 30px, rgba(0, 0, 0, 0.12) 0px 4px 6px, rgba(0, 0, 0, 0.17) 0px 12px 13px, rgba(0, 0, 0, 0.09) 0px -3px 5px;
  background-color: var(--dark-gray);
  z-index: 9999;
}
.col{
  padding-left: 0px !important;
}

.xalbum-title {
  color: var(--my-white) !important;
}

.xalbum-composer {
  color: var(--my-white) !important;
}

.xalbum-cat {
  color: var(--light-gray) !important;
}

.xalbum-work-title {
  color: var(--my-white) !important;
}

.xalbum-composer {
  color: var(--my-white) !important;
}

.xpopup>>>.album-cat {
  color: var(--light-gray) !important;
}

.image-caption {
  visibility: inherit;
  width: 100%;
  padding-top: 8.5px;
  padding-bottom: 10px;
  padding-left: 10px;
  padding-right: 10px;
}

.album-popup-cover{
  box-shadow: rgba(0, 0, 0, 0.16) 0px 1px 4px;
  max-height: calc(80vh - var(--workingheight));
  max-width: 50vw;
}

.orange{
  color: var(--orange) !important;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  grid-gap: 10px;
  grid-auto-flow: dense;
  padding-top: 10px;
  padding-bottom: 15px;
}

.grid-item {
  display: flex;
}

.album-cover {
  width: 100%;
  height: auto;
  box-shadow: rgba(0, 0, 0, 0.2) 0px 1px 4px;
}
.album-cover:hover {
  cursor: pointer;
  box-shadow: rgba(0, 0, 0, 0.6) 0px 2px 4px !important;
  outline: solid 5px var(--orange);
}
.spinner {
  text-align: center;
}
.m-5 {
    color: #9da6af;
}
.message{
  margin-top: 12px;
  text-align: center;
  margin-bottom: 2px;
  color: var(--medium-gray);
}
 .narrow{
  font-family: Roboto Condensed !important;
 }

</style>

