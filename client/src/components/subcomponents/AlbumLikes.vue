<template>
  <div>
   <span class="likes" v-if="currentLikes">&nbsp;
     <b-badge v-if="parseInt(currentLikes) == 1 ">{{ currentLikes }} Like</b-badge>
     <b-badge v-if="parseInt(currentLikes) > 1 ">{{ currentLikes }} Likes</b-badge>
     <span class="user-liked">&nbsp;<b-icon-heart-fill></b-icon-heart-fill></span>
   </span>
  </div>
</template>

<script>
// Need to add logic for if user likes this album

import {eventBus} from "@/main.js";

export default {
  name: 'AlbumLikes',
  props: {
    album: Object,
    selectedAlbum: String
  },
  data() {
    return {
      currentLikes: this.album.likes
    };
  },
  methods:{
    likeAlbum(){
      if(this.selectedAlbum == this.album.id){
        this.currentLikes = this.album.likes + 1;
      }
    },
    unlikeAlbum(){
      if(this.selectedAlbum == this.album.id){
        this.currentLikes = this.album.likes;
      }
    }
  },
  created() {
    eventBus.$on('fireLikeAlbum', this.likeAlbum);
    eventBus.$on('fireUnlikeAlbum', this.unlikeAlbum);
  },
  beforeDestroy() {
    eventBus.$off('fireLikeAlbum', this.likeAlbum);
    eventBus.$off('fireUnlikeAlbum', this.unlikeAlbum);
  }
}
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