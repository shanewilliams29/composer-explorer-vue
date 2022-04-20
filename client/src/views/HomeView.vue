<template>
  <div id="home">
    <ColumnHeadings/>
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
import ColumnHeadings from '@/components/ColumnHeadings.vue'
import ComposerList from '@/components/ComposerList.vue'
import WorkList from '@/components/WorkList.vue'
import AlbumList from '@/components/AlbumList.vue'

export default {
  name: 'HomeView',
  components: {
    ColumnHeadings,
    ComposerList,
    WorkList,
    AlbumList,
  },
  beforeCreate(){
    if( screen.width <= 760 ) {
        window.location.replace('mobile');
    }
  },
  created() {
    window.firstLoad = true; // prevent playback on first load
  },
}
</script>

<style>
  .display-height{
    height: calc(100vh - 66px - 78px - 100px - var(--panelheight));
    overflow-y: scroll;
    overflow-x: hidden;
  }
</style>
