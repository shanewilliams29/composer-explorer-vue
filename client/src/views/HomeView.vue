<template>
  <div id="home">
    <BrowseHeading/>
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
import BrowseHeading from "@/components/browse/BrowseHeading.vue";
import ComposerList from "@/components/composers/ComposerList.vue";
import WorkList from "@/components/works/WorkList.vue";
import AlbumList from "@/components/albums/AlbumList.vue";

export default {
  name: "HomeView",
  components: {
    BrowseHeading,
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
    document.documentElement.style.setProperty("--playback-color", "var(--yellow)"); // 007bff
  },
  created() {
    // remove query parameters for landing from search on another page
    if (this.$route.query.search) {
      window.firstLoad = false; // allow playback on first load from another page
        setTimeout(() => {
          this.$router.replace({'query': null});
        }, 1000);
    } else {
      window.firstLoad = true; // prevent playback on first load
    }
    this.$view.mode = null;
  },
};
</script>

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
