<template>
  <div id="app">
    <NavBar/>
    <div class="container-fluid">
      <b-row>
        <b-col><ComposerList/></b-col>
        <b-col>2 of 3</b-col>
        <b-col cols="6">3 of 3</b-col>
      </b-row>

    </div>
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue'
import ComposerList from './components/ComposerList.vue'

export default {
  name: 'App',
  components: {
    NavBar,
    ComposerList
  }
}
</script>

<style>
  body{
    background: #f1f2f4 !important;
  }
</style>

