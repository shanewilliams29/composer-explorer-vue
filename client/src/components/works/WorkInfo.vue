<template>
  <b-card class="composer-info-card shadow-sm">
    <b-card-body class="card-body">
      <b-card-title class="card-title">
        <table @click="goToWork(work)">
          <tr>
            <td>
              <b-avatar size="60px" :src="composerImg" v-if="$view.mobile"></b-avatar>
              <b-avatar size="60px" :src="workImg" v-if="!$view.mobile"></b-avatar>
            </td>
            <td class="info-td">
              <span class="composer-name" v-if="$view.mobile">{{ composer }}<br /></span>
              {{ workTitle }}<br />
              <span v-if="catNo" class="born-died">{{ catNo }}</span>
              <span v-else class="born-died"><span v-if="date">{{date}}</span></span>
            </td>
          </tr>
        </table>
      </b-card-title>
      <b-card-text class="info-card-text" v-if="!$view.mobile">
        <div class="spinner" v-show="loading" role="status">
          <b-spinner class="m-5"></b-spinner>
        </div>
        <div v-show="!loading" style="white-space: pre-line;">
          <b-alert v-if="!workMatch" show variant="warning">
            <b-icon icon="exclamation-circle-fill" variant="warning"></b-icon>
            <span style="font-size: 12px">&nbsp;This Wikipedia article is the most relevant found.</span></b-alert>
            <span><h6 v-if="!workMatch"><span v-if="pageTitle">{{pageTitle}}</span></h6></span>
            <div>{{ workBlurb }}<br />
            <a :href="wikiLink" target="_blank" class="wiki-link" v-if="pageTitle">
              <br />
              Read more on Wikipedia: {{pageTitle}}
            </a>
          </div>
        </div>
      </b-card-text>
    </b-card-body>
  </b-card>
</template>


<script>
import axios from "axios";
import { addLineBreaksToParagraph } from "@/HelperFunctions.js"
import { eventBus } from "@/main.js";

export default {
  data() {
    return {
      loading: true,
      workTitle: "",
      pageTitle: "",
      composerImg: "",
      workImg: "",
      workBlurb: "",
      wikiLink: "",
      catNo: "",
      date: "",
      composer: "",
      workMatch: true,
      work: {},
    };
  },
  computed: {
    workChanged() {
      return this.$config.work;
    },
  },
  watch: {
    workChanged(newWork) {
      this.getWorkInfo(newWork);
    },
  },
  methods: {
    goToWork(work) {
      if(this.$view.mobile){
        this.$emit('togglePanel');
        let delay = 0;
        if (this.$route.name != "home") {
          delay = 200;
          this.$router.push("/mobile?search=" + work.id);
        }
        setTimeout(function() {
          eventBus.$emit("fireWorkOmniSearch", work);
          eventBus.$emit("requestWorksList", work.composer);
          eventBus.$emit("requestAlbums");
        }, delay);
      }
    },
    checkIfWorkMatches(opus, title, text) {
      if (opus) {
        const num = opus.match(/\d+/)[0];
        const cat = opus.match(/\D+/)[0].trim();
        const regex_num = new RegExp(`\\b${num}\\w?`);
        const regex_cat = new RegExp(`\\b${cat}\\w?`);
        return (regex_num.test(text) && regex_cat.test(text));
      } else {
        return text.toLowerCase().includes(title.toLowerCase());
      }
    },

    // Retrieve work data from database
    getWorkInfo(work) {
      this.loading = true;
      const path = "api/workinfo/" + work;
      axios
        .get(path)
        .then((res) => {
          this.work = res.data.info;
          this.composer = res.data.info.composer;
          this.workTitle = res.data.info.title;
          this.workImg = res.data.info.search;
          this.composerImg = `https://usc1.contabostorage.com/a36ba68caf9842799883275ab3ad3a88:composer-explorer.bucket/static/img/${this.composer}.jpg`;
          this.catNo = res.data.info.cat;
          this.date = res.data.info.date;

          if (this.catNo) {
            var num = this.catNo.match(/\d+/);
            this.wikiWork(`${this.composer} OR ${num} ${this.workTitle}`)
          } else {
            this.wikiWork(`${this.composer} ${this.workTitle}`);
          }

        })
        .catch((error) => {
          this.loading = false;
          console.error(error);
        });
    },

    // Retrieve work info from Wikipedia
    wikiWork(search_item) {

      // FIRST SEARCH WIKIPEDIA FOR WORK AND GET PAGE ID
      let url = "https://en.wikipedia.org/w/api.php";
      let params = {
        action: "query",
        list: "search",
        srsearch: search_item,
        srlimit: 1,
        format: "json",
      };

      // Build URL with parameters
      url = url + "?origin=*";
      Object.keys(params).forEach(function (key) {
        url += "&" + key + "=" + params[key];
      });

      axios
        .get(url)
        .then((res) => {
          let pageid = "";
          let matchCheck = false;
          let resultsArray = res.data.query.search

          try {
            // Loop through array of article search results and try to match article with work
            for (var i = 0; i < resultsArray.length; i++) {
              matchCheck = this.checkIfWorkMatches(this.catNo, this.workTitle, resultsArray[i].snippet);

              // Exit if match
              if (matchCheck) {
                break;
              }
            }

            // Return first article if no match
            if (!matchCheck) {
              i = 0;
            }     

            // Retrieve relevant wikipedia page ID
            pageid = res.data.query.search[i].pageid;
            
          } catch (error) {
            this.workBlurb = "Work not found on Wikipedia.";
            this.workMatch = true;
            this.pageTitle = null;
            this.loading = false;
            return error;
          }

          // SECONDLY RETRIEVE DATA FROM WIKIPEDIA ARTICLE USING PAGE ID
          var url2 = "https://en.wikipedia.org/w/api.php";
          var params2 = {
            action: "query",
            pageids: pageid,
            prop: "extracts&exintro&explaintext",
            redirects: 1,
            format: "json",
          };
          url2 = url2 + "?origin=*";

          // Build URL with parameters
          Object.keys(params2).forEach(function (key) {
            url2 += "&" + key + "=" + params2[key];
          });

          axios
            .get(url2)
            .then((res) => {

              // Retrieve Wikipedia information
              for (var id in res.data.query.pages) {
                let text = res.data.query.pages[id].extract;
                this.workMatch = this.checkIfWorkMatches(this.catNo, this.workTitle, text);
                this.workBlurb = addLineBreaksToParagraph(text);
                this.pageTitle = res.data.query.pages[id].title;
                let wikiurl = "https://en.wikipedia.org/wiki/" + this.pageTitle;
                this.wikiLink = wikiurl;
                this.loading = false;
                break;
              }
            })
            .catch((error) => {
              this.loading = false;
              console.error(error);
            });
        })
        .catch((error) => {
          this.loading = false;
          console.error(error);
        });
    },
  },
  created() {
    this.getWorkInfo(this.$config.work);
  },
};

</script>

<style scoped>
.alert{
  padding: 6px;
  margin-bottom: 10px;
}
.info-td{
  padding-left: 10px;
  font-size: 16px;
}
.spinner {
  text-align: center;
}
.m-5 {
  color: var(--dark-gray);
}
.born-died{
  font-size: 15px !important;
  color: grey !important;
}
.composer-info-card{
  padding: 15px;
  padding-bottom: 10px;
  background-color: var(--my-white) !important;
  border: none !important;
}
.card-title{
  font-size: 16px;
}
.card-body{
  background-color: var(--my-white) !important;
}
.info-card-text{
  font-size: 13px;
  line-height: 130%;
  overflow-y: scroll;
  height: 190px;
  padding-left: 5px;
}
.wiki-link{
  font-style: italic;
  color: grey;
}

/*scrollbars*/
 .info-card-text {
        --scroll-bar-color: var(--scroll-color-light);
        --scroll-bar-bg-color: var(--my-white);
    }

    .info-card-text{
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
        border: 3px solid var(--scroll-bar-bg-color)!important;
    }

</style>
