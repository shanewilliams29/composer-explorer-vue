<template>
  <div id="home">
    <RadioHeading/>
    <div class="container-fluid">
      <b-row>
        <b-col class="display-list first-col" ref="scroll-box-comp"><ComposerList/></b-col>
        <b-col class="display-list" ref="scroll-box"><WorkList/></b-col>
        <b-col class="display-list last-col extra-margin"><AlbumList/></b-col>
      </b-row>
    </div>
  </div>
</template>

<script>
import RadioHeading from '@/components/radio/RadioHeading.vue'
import ComposerList from "@/components/composers/ComposerList.vue";
import WorkList from "@/components/works/WorkList.vue";
import AlbumList from "@/components/albums/AlbumList.vue";

export default {
  name: 'RadioView',
  components: {
    RadioHeading,
    ComposerList,
    WorkList,
    AlbumList,
  },
  beforeCreate() {
    document.documentElement.style.setProperty('--flex', '0 0 400px');
  },
  created(){
    this.$view.mode = 'radio';
    document.documentElement.style.setProperty("--playback-color", "var(--yellow)"); // #28a745
  }
}
</script>

<style scoped>
>>> .highlight{
  background-color: var(--green);
}
>>> .highlight td{
  background-color: var(--green);
}
>>> .music-note{
  color: var(--green);
}
</style>
