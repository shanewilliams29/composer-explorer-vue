<template>
  <div id="app">
    <NavBar/>
    <div class="container-fluid">
      <b-row>
        <b-col><ComposerList/></b-col>
        <b-col><WorkList/></b-col>
        <b-col cols="5">3 of 3</b-col>
      </b-row>

    </div>
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue'
import ComposerList from './components/ComposerList.vue'
import WorkList from './components/WorkList.vue'

export default {
  name: 'App',
  components: {
    NavBar,
    ComposerList,
    WorkList
  }
}
</script>

<style>
  body{
    background: #f1f2f4 !important;
  }
</style>

