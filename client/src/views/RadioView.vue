<template>
  <div id="home">
    <RadioHeading/>
    <div class="container-fluid">
      <b-row>
        <b-col class="display-height"><ComposerList/></b-col>
        <b-col class="display-height"><WorkList/></b-col>
        <b-col class="display-height"><AlbumList/></b-col>
      </b-row>
    </div>
  </div>
</template>

<script>
import RadioHeading from '@/components/RadioHeading.vue'
import ComposerList from '@/components/ComposerList.vue'
import WorkList from '@/components/WorkList.vue'
import AlbumList from '@/components/AlbumList.vue'

export default {
  name: 'RadioView',
  components: {
    RadioHeading,
    ComposerList,
    WorkList,
    AlbumList,
  },
  created(){
    this.$view.mode = 'radio';
  }
}
</script>

<style>
  .display-height{
    height: calc(100vh - 66px - 78px - 100px - var(--panelheight));
    overflow-y: scroll;
    overflow-x: hidden;
  }
</style>
