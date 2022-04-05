<template>
  <div id="app">
    <NavBar/>
    <ColumnHeadings/>
    <div class="container-fluid">
      <b-row>
        <b-col class="composer-list"><ComposerList/></b-col>
        <b-col class="work-list"><WorkList/></b-col>
        <b-col class="album-list"><AlbumList/></b-col>
      </b-row>
    </div>
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue'
import ColumnHeadings from './components/ColumnHeadings.vue'
import ComposerList from './components/ComposerList.vue'
import WorkList from './components/WorkList.vue'
import AlbumList from './components/AlbumList.vue'

export default {
  name: 'App',
  components: {
    NavBar,
    ColumnHeadings,
    ComposerList,
    WorkList,
    AlbumList
  }
}
</script>

<style>
  body{
    background: #f1f2f4 !important;
  }
  .composer-list{
    height: calc(100vh - 96px);
    overflow-y: scroll;
  }
  .work-list{
    height: calc(100vh - 96px);
    overflow-y: scroll;
  }
  .album-list{
    height: calc(100vh - 96px);
    overflow-y: scroll;
  }
</style>

