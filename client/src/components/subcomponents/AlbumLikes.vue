<template>
  <div>
    <span class="likes" v-if="currentLikes">
      <b-badge v-if="parseInt(currentLikes) == 1 ">{{ currentLikes }} Like</b-badge>
      <b-badge v-if="parseInt(currentLikes) > 1 ">{{ currentLikes }} Likes</b-badge>
    </span>
    <span class="user-liked" v-if="userLikes">&nbsp;<b-icon-heart-fill></b-icon-heart-fill></span>
    <span class="likes" v-if="!currentLikes">
      <br />
    </span>
  </div>
</template>

<script>
import { eventBus } from "@/main.js";

export default {
  name: "AlbumLikes",
  props: {
    album: Object,
    selectedAlbum: String,
    likedAlbums: Array,
  },
  data() {
    return {
      currentLikes: this.album.likes,
      userLikes: this.likedAlbums.indexOf(this.album.id) > -1,
    };
  },
  methods: {
    detectLike(album_id) {
      if (album_id == this.album.id && this.userLikes) {
        this.$view.like = true;
      } else if (album_id == this.album.id && !this.userLikes) {
        this.$view.like = false;
      } else if (album_id != this.album.id) {
        // pass
      }
    },
    likeAlbum() {
      if (this.selectedAlbum == this.album.id && !this.userLikes) {
        this.currentLikes = this.currentLikes + 1;
        this.userLikes = true;
      }
    },
    unlikeAlbum() {
      if (this.selectedAlbum == this.album.id && this.userLikes) {
        this.currentLikes = this.currentLikes - 1;
        this.userLikes = false;
      }
    },
  },
  created() {
    eventBus.$on("fireLikeAlbum", this.likeAlbum);
    eventBus.$on("fireUnlikeAlbum", this.unlikeAlbum);
    eventBus.$on("fireAlbumData", this.detectLike);
  },
  beforeDestroy() {
    eventBus.$off("fireLikeAlbum", this.likeAlbum);
    eventBus.$off("fireUnlikeAlbum", this.unlikeAlbum);
    eventBus.$off("fireAlbumData", this.detectLike);
  },
};
</script>

<style scoped>
.badge {
  vertical-align: middle;
  color: #fff !important;
  background-color: darkgoldenrod;
  margin-bottom: 2.5px;
  border-radius: 7px;
}
.highlight .badge {
  color: #000 !important;
  background-color: #fff;
}
.user-liked{
  color: darkgoldenrod !important;
}
.highlight .user-liked{
  color: #fff !important;
}
</style>