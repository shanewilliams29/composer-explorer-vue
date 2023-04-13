<template>
  <div>
    <vue-word-cloud
      style="height: calc(100vh - 244px - var(--panelheight)); width: 100%;"
      :words="data"
      :color="([, , color]) => color == 0 ? 'var(--dark-gray)' : color == 1 ? 'var(--medium-gray)' : '#727981'"
      font-family="Roboto,Helvetica,Oxygen,Ubuntu,Cantarell,fira sans,droid sans,sans-serif"
      :font-size-ratio="0.2"
      :spacing="0.1"
    >
      <template slot-scope="{text}">
        <div class="composer-name" @click="wordClick(text);">
          {{ text }}
        </div>
      </template>
    </vue-word-cloud>
  </div>
</template>

<script>
import { eventBus } from "@/main.js";

export default {
  data() {
    return {
      data: []
    };
  },
  methods:{
    wordClick(word){
      eventBus.$emit('requestComposersForArtist', word);
    }
  },
  created() {
    const artists = require('@/assets/topartists.json');
    this.data = artists;
  },
}
</script>

<style scoped>
.composer-name{
  cursor: pointer;
}
.composer-name:hover {
  color: #6f42c1;
}
</style>

