<template>
  <div id="home">
    <ColumnHeadings/>
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
import ColumnHeadings from "@/components/browse/ColumnHeadings.vue";
import ComposerList from "@/components/composers/ComposerList.vue";
import WorkList from "@/components/works/WorkList.vue";
import AlbumList from "@/components/albums/AlbumList.vue";

export default {
  name: "HomeView",
  components: {
    ColumnHeadings,
    ComposerList,
    WorkList,
    AlbumList,
  },
  computed: {
    albumSizeChanged() {
      return this.$config.albumSize;
    },
  },
  watch: {
    albumSizeChanged(newSize) {
      if (newSize == "large") {
        document.documentElement.style.setProperty("--flex", "0 0 400px");
      } else {
        document.documentElement.style.setProperty("--flex", "1");
      }
    },
  },
  beforeCreate() {
    if (screen.width <= 760) {
      window.location.replace("mobile");
    }
    this.$view.mobile = false;
    if (this.$config.albumSize == "large") {
      document.documentElement.style.setProperty("--flex", "0 0 400px");
    } else {
      document.documentElement.style.setProperty("--flex", "1");
    }
  },
  created() {
    window.firstLoad = true; // prevent playback on first load
    this.$view.mode = null;
  },
};
</script>

<style>
.display-list {
  height: calc(100vh - var(--workingheight) - var(--panelheight));
  padding-right: 12px;
  padding-bottom: 5px;
  overflow-y: scroll;
  overflow-x: hidden;
}
.card-body {
  padding: 0px !important;
}
@media only screen and (min-width: 1000px) {
  .last-col {
    -ms-flex: var(--flex) !important;
    flex: var(--flex) !important;
  }
}
.extra-margin {
  margin-right: 3.5px;
}
/*scrollbars*/
:root {
  --scroll-bar-color: var(--scroll-color);
  --scroll-bar-bg-color: var(--light-gray);
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

<style scoped>
>>> .highlight{
  background-color: var(--blue);
}
>>> .highlight td{
  background-color: var(--blue);
}
>>> .music-note{
  color: var(--blue);
}
</style>
