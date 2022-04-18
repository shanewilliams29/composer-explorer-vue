<template>
<div>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
        <b-card class="composer-info-card" v-show="!loading">
          <b-card-body class="card-body">
 <b-card-title class="card-title">
              <table>
                <tr>
                  <td>

                <b-avatar size="60px" :src="workImg"></b-avatar>

                  </td>
                  <td class="info-td">
                    {{ workTitle }}<br>
                    <span v-if="catNo" class="born-died">{{ catNo }}</span><span v-else class="born-died">{{date}}</span>
                  </td>
                </tr>
              </table>
              </b-card-title>
            <b-card-text class="info-card-text">
            {{ workBLurb }}<br>
            <a :href="wikiLink" target="_blank" class="wiki-link"><br>Read more on Wikipedia</a>
            </b-card-text>
          </b-card-body>
        </b-card>
</div>

<!--   <div class="composer-heading">
    <h6><b-avatar size="60px" src="https://storage.googleapis.com/composer-explorer.appspot.com/img/Beethoven.jpg"></b-avatar>&nbsp; Ludwig van Beethoven</h6>
  </div>
  <div class="composer-body">

  </div> -->

</template>

<script>
import axios from 'axios';
import {eventBus} from "../../main.js";

export default {
  data() {
    return {
      loading: true,
      workTitle: "",
      pageTitle: "",
      workImg: "",
      workBlurb: "",
      wikiLink: ""
    };
  },
  methods: {
    getWorkInfo(work) {
        this.loading = true;
        const path = 'api/workinfo/' + work;
        axios.get(path)
          .then((res) => {
            this.composer = res.data.info.composer;
            this.workTitle = res.data.info.title;
            this.workImg = res.data.info.search;
            this.catNo = res.data.info.cat;
            this.date = res.data.info.date;
            this.wikiWork(this.composer + " " + this.workTitle + " " + this.catNo);
          })
          .catch((error) => {
            // eslint-disable-next-line
            console.error(error);

          });
      },
    wikiWork(search_item){
      var url = "https://en.wikipedia.org/w/api.php";
      var params = {
          action: "query",
          list: "search",
          srsearch: search_item,
          srlimit: 1,
          format: "json"
      };

      url = url + "?origin=*";
      Object.keys(params).forEach(function(key){url += "&" + key + "=" + params[key];});

      axios.get(url)
          .then((res) => {

            // SECOND SEARCH
            let pageid = res.data.query.search[0].pageid;
            var url2 = "https://en.wikipedia.org/w/api.php";
            var params2 = {
                action: "query",
                pageids: pageid,
                prop: "extracts&exintro&explaintext",
                redirects: 1,
                format: "json"
            };

            url2 = url2 + "?origin=*";
            Object.keys(params2).forEach(function(key){url2 += "&" + key + "=" + params2[key];});

          axios.get(url2)
          .then((res) => {
                      for (var id in res.data.query.pages) {
                          this.workBLurb = res.data.query.pages[id].extract;
                          this.pageTitle = res.data.query.pages[id].title;
                          let wikiurl = "https://en.wikipedia.org/wiki/" + this.pageTitle;
                          this.wikiLink = wikiurl;
                          this.loading = false;
                          break;
                      }


          })
          .catch((error) => {
            // eslint-disable-next-line
            console.error(error);
          });

          })
          .catch((error) => {
            // eslint-disable-next-line
            console.error(error);
          });
  },
},
  created() {
    this.loading = true;

    eventBus.$on('fireAlbums', (workId, title) => {
      this.loading = false;
      this.workTitle = title;
      this.getWorkInfo(workId);
    })
    // eslint-disable-next-line
    eventBus.$on('expandInfoPanel', (composer, workId) => {
      this.loading = false;
      this.getWorkInfo(workId);
    })
  },
};
</script>

<style scoped>
.info-td{
  padding-left: 10px;
}
.spinner {
  text-align: center;
}
.m-5 {
  color: #343a40;
}
.born-died{
  font-size: 16px !important;
  color: grey !important;
}
.composer-info-card{
  padding: 15px;
  padding-bottom: 10px;
  background-color: white !important;
  border: none !important;

}
.card-title{
  font-size: 18px;
}
.card-body{

  background-color: white !important;
}
.info-card-text{
  font-size: 13px;
  line-height: 130%;
  overflow-y: scroll;
  height: 190px;
}
.info-card-text {
    -ms-overflow-style: none;  /* Internet Explorer 10+ */
    scrollbar-width: none;  /* Firefox */
}
.info-card-text::-webkit-scrollbar {
    display: none;  /* Safari and Chrome */
}
.wiki-link{
  font-style: italic;
  color: grey;
}
</style>
