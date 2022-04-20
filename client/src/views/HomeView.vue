<template>
  <div id="home">
    <NavBar/>
    <ColumnHeadings/>
    <div class="container-fluid">
      <b-row>
        <b-col class="display-list"><ComposerList/></b-col>
        <b-col class="display-list"><WorkList/></b-col>
        <b-col class="display-list"><AlbumList/></b-col>
      </b-row>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import ColumnHeadings from '@/components/ColumnHeadings.vue'
import ComposerList from '@/components/ComposerList.vue'
import WorkList from '@/components/WorkList.vue'
import AlbumList from '@/components/AlbumList.vue'

export default {
  name: 'HomeView',
  components: {
    NavBar,
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
  .display-list{
    height: calc(100vh - 66px - 78px - 100px - var(--panelheight));
    overflow-y: scroll;
    overflow-x: hidden;
  }
</style>
