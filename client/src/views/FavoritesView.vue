<template>
  <div id="home">
    <FavoritesHeading/>
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
import FavoritesHeading from "@/components/favorites/FavoritesHeading.vue";
import ComposerList from "@/components/composers/ComposerList.vue";
import WorkList from "@/components/works/WorkList.vue";
import AlbumList from "@/components/albums/AlbumList.vue";

export default {
  name: "FavoritesView",
  components: {
    FavoritesHeading,
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
    if (this.$config.albumSize == "large") {
      document.documentElement.style.setProperty("--flex", "0 0 400px");
    } else {
      document.documentElement.style.setProperty("--flex", "1");
    }
  },
  created() {
    window.firstLoad = false; // allow playback on first load
    this.$view.mode = "favorites";
    document.documentElement.style.setProperty("--playback-color", "var(--yellow)"); //#dc3545
  },
};

</script>

<style scoped>
>>> .highlight{
  background-color: var(--red);
}
>>> .highlight td{
  background-color: var(--red);
}
>>> .music-note{
  color: var(--red);
}
</style>
