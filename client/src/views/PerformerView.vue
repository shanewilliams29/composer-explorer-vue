<template>
  <div id="performer">
    <PerformersHeadings/>
    <div class="container-fluid">
      <b-row>
        <b-col class="display-list first-col"><ComposerList/></b-col>
        <b-col class="display-list"><WorkList/></b-col>
        <b-col class="display-list last-col extra-margin"><AlbumList/></b-col>
      </b-row>
    </div>
  </div>
</template>

<script>
import PerformersHeadings from '@/components/PerformersHeadings.vue'
import ComposerList from '@/components/ComposerList.vue'
import WorkList from '@/components/WorkList.vue'
import AlbumList from '@/components/AlbumList.vue'

export default {
  name: 'PerformerView',
  components: {
    PerformersHeadings,
    ComposerList,
    WorkList,
    AlbumList,
  },
  created() {
    window.firstLoad = false; // allow playback on first load for performer view
    this.$view.mode = 'performer';
  },
}
</script>
<style scoped>
>>> .highlight{
  background-color: var(--purple);
}
>>> .highlight td{
  background-color: var(--purple);
}
</style>
