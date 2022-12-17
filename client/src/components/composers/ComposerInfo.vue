<template>
  <b-card class="composer-info-card shadow-sm">
    <b-card-title class="card-title">
      <table>
        <tr>
          <td>
            <b-avatar :src="composer.image" v-if="$view.mobile"></b-avatar>
            <b-avatar-group size="60px" v-if="!$view.mobile">
              <b-avatar :src="composer.region"></b-avatar>
              <b-avatar :src="composer.image"></b-avatar>
            </b-avatar-group>
          </td>
          <td class="info-td">
            {{ composer.name_full }}<br />
            <span class="born-died">
              {{ composer.born }} - {{ composer.died > 2049 ? 'present' : composer.died }}
            </span>
          </td>
        </tr>
      </table>
    </b-card-title>
    <b-card-text class="info-card-text" v-if="!$view.mobile">
      <div class="spinner" v-show="loading" role="status">
        <b-spinner class="m-5"></b-spinner>
      </div>
      <div v-show="!loading" style="white-space: pre-line;">
        {{ addLineBreaks(composer.introduction) }}<br />
        <a :href="composer.pageurl" target="_blank" class="wiki-link">
          <br />
          Read more on Wikipedia
        </a>
      </div>
    </b-card-text>
  </b-card>
</template>

<script>
import axios from "axios";
import {addLineBreaksToParagraph} from "@/HelperFunctions.js"

export default {
  data() {
    return {
      loading: true,
      composer: {},
    };
  },
  computed: {
    composerChanged() {
      return this.$config.composer;
    },
  },
  watch: {
    composerChanged(newComposer) {
      if (newComposer) {
        this.getComposerInfo(newComposer);
      }
    },
  },
  methods: {
    addLineBreaks(paragraph){
      return addLineBreaksToParagraph(paragraph);
    },
    getComposerInfo(composer) {
      this.loading = true;
      const path = "api/composerinfo/" + composer;
      axios
        .get(path)
        .then((res) => {
          this.composer = res.data.info;
          this.loading = false;
        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },
  },
  created() {
    this.loading = true;
    this.getComposerInfo(this.$config.composer);
  },
};
</script>

<style scoped>
.spinner {
  text-align: center;
}
.m-5 {
  color: var(--dark-gray);
}
.born-died {
  font-size: 15px !important;
  color: grey !important;
}
.composer-info-card {
  padding: 15px;
  padding-bottom: 10px;
  background-color: var(--my-white) !important;
  border: none !important;
}
.card-title {
  font-size: 16px;
}
.info-td {
  padding-left: 10px;
  font-size: 16px;
}
.card-body {
  background-color: var(--my-white) !important;
}
.info-card-text {
  font-size: 13px;
  line-height: 130%;
  overflow-y: scroll;
  height: 190px;
  padding-left: 5px;
}
.wiki-link {
  font-style: italic;
  color: grey;
}

/*scrollbars*/
.info-card-text {
  --scroll-bar-color: var(--scroll-color-light);
  --scroll-bar-bg-color: var(--my-white);
}
.info-card-text {
  scrollbar-width: thin;
  scrollbar-color: var(--scroll-bar-color) var(--scroll-bar-bg-color) !important;
}
/* Works on Chrome, Edge, and Safari */
.info-card-text::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}
.info-card-text::-webkit-scrollbar-track {
  background: var(--scroll-bar-bg-color) !important;
}
.info-card-text::-webkit-scrollbar-thumb {
  background-color: var(--scroll-bar-color);
  border-radius: 20px;
  border: 3px solid var(--scroll-bar-bg-color) !important;
}

</style>
