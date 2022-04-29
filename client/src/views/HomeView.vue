<template>
  <div id="home">
    <ColumnHeadings/>
    <div class="container-fluid">
      <b-row>
        <b-col class="display-height first-col"><ComposerList/></b-col>
        <b-col class="display-height"><WorkList/></b-col>
        <b-col class="display-height last-col extra-margin"><AlbumList/></b-col>
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
    padding-right: 12px;
    padding-bottom: 5px;
    overflow-y: scroll;
}
@media only screen and (min-width: 1000px) {
    .last-col{
        -ms-flex: 0 0 380px;
        flex: 0 0 380px;
    }
}
.extra-margin{
    margin-right: 3.5px;
}

/*scrollbars*/
 :root {
        --scroll-bar-color: #c9cccf;
        --scroll-bar-bg-color: #f1f2f4;
    }

    * {
        scrollbar-width: thin;
        scrollbar-color: var(--scroll-bar-color) var(--scroll-bar-bg-color);
    }

    /* Works on Chrome, Edge, and Safari */
    *::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }

    *::-webkit-scrollbar-track {
        background: var(--scroll-bar-bg-color);
    }

    *::-webkit-scrollbar-thumb {
        background-color: var(--scroll-bar-color);
        border-radius: 20px;
        border: 3px solid var(--scroll-bar-bg-color);
    }
</style>
