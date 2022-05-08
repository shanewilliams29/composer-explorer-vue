<template>
  <div id="home">
    <RadioHeading/>
    <div class="container-fluid">
      <b-row>
        <b-col class="display-list first-col"><ComposerList/></b-col>
        <b-col class="display-list" ref="scroll-box"><WorkList/></b-col>
        <b-col class="display-list last-col extra-margin"><AlbumList/></b-col>
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
