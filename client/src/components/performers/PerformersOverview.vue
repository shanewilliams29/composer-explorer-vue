<template>
  <div>
    <b-row class="message narrow">
      <b-col >
        Conductors
      </b-col>
      <b-col>
        Groups
      </b-col>
      <b-col>
        Soloists
      </b-col>
      <b-col>
        Vocalists
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <div class="grid-container">
          <div class="grid-item" v-for="artist in conductors" :key="artist.id">
            <b-card class="album-info-card shadow-sm">
              <b-card-body class="card-body">
                <b-card-text class="info-card-text">
                  <div>
                    <table>
                      <tr>
                        <td>
                          <b-avatar size="56px" :src="artist.img"></b-avatar>
                        </td>
                        <td class="info-td">
                          <a class="artist-name" @click="wordClick(artist)">{{ artist.name }}</a><br />
                          <span v-if="artist.description !== 'NA'" class="born-died">{{artist.description}}<br></span>
                        </td>
                      </tr>
                    </table>
                  </div>
                </b-card-text>
              </b-card-body>
            </b-card>
          </div>
        </div>
      </b-col>
      <b-col>
        <div class="grid-container">
          <div class="grid-item" v-for="artist in groups" :key="artist.id">
            <b-card class="album-info-card shadow-sm">
              <b-card-body class="card-body">
                <b-card-text class="info-card-text">
                  <div>
                    <table>
                      <tr>
                        <td>
                          <b-avatar size="56px" :src="artist.img"></b-avatar>
                        </td>
                        <td class="info-td">
                          <a class="artist-name" @click="wordClick(artist)">{{ artist.name }}</a><br />
                          <span v-if="artist.description !== 'NA'" class="born-died">{{artist.description}}<br></span>
                        </td>
                      </tr>
                    </table>
                  </div>
                </b-card-text>
              </b-card-body>
            </b-card>
          </div>
        </div>
      </b-col>
      <b-col>
        <div class="grid-container">
          <div class="grid-item" v-for="artist in soloists" :key="artist.id">
            <b-card class="album-info-card shadow-sm">
              <b-card-body class="card-body">
                <b-card-text class="info-card-text">
                  <div>
                    <table>
                      <tr>
                        <td>
                          <b-avatar size="56px" :src="artist.img"></b-avatar>
                        </td>
                        <td class="info-td">
                          <a class="artist-name" @click="wordClick(artist)">{{ artist.name }}</a><br />
                          <span v-if="artist.description !== 'NA'" class="born-died">{{artist.description}}<br></span>
                        </td>
                      </tr>
                    </table>
                  </div>
                </b-card-text>
              </b-card-body>
            </b-card>
          </div>
        </div>
      </b-col>
      <b-col>
        <div class="grid-container">
          <div class="grid-item" v-for="artist in vocalists" :key="artist.id">
            <b-card class="album-info-card shadow-sm">
              <b-card-body class="card-body">
                <b-card-text class="info-card-text">
                  <div>
                    <table>
                      <tr>
                        <td>
                          <b-avatar size="56px" :src="artist.img"></b-avatar>
                        </td>
                        <td class="info-td">
                          <a class="artist-name" @click="wordClick(artist)">{{ artist.name }}</a><br />
                          <span v-if="artist.description !== 'NA'" class="born-died">{{artist.description}}<br></span>
                        </td>
                      </tr>
                    </table>
                  </div>
                </b-card-text>
              </b-card-body>
            </b-card>
          </div>
        </div>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import { eventBus } from "@/main.js";

export default {
  data() {
    return {
      loading: false,
      artists: [],
      data: [],
    };
  },
  methods:{
    shuffleArray(array) {
      for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
      }
      return array.slice(0,30);
    },
    toK(num){
      return num.toString().slice(0, -3) + "k";
    },
    wordClick(artist){
      eventBus.$emit("requestPerformer", artist);
    }
  },
  created() {
    let n = 100;
    this.conductors = this.shuffleArray(require('@/assets/topconductors.json').slice(0, n));
    this.groups = this.shuffleArray(require('@/assets/topgroups.json').slice(0, n));
    this.soloists = this.shuffleArray(require('@/assets/topsoloists.json').slice(0, n));
    this.vocalists = this.shuffleArray(require('@/assets/topvocalists.json')).slice(0, n);
  },
}
</script>

<style scoped>
.message{
  margin-top: 10px;
  text-align: center;
  margin-bottom: 5px;
  color: var(--medium-gray);
}
.narrow{
  font-family: Roboto Condensed !important;
 }
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  grid-gap: 5px;
  grid-auto-flow: dense;
  height: calc(100vh - 244px - var(--panelheight) - 29px);
  overflow: auto;
  padding-bottom: 15px;
  padding-top: 5px;
}
.grid-item {
  display: flex;
  padding-right: 5px;
}
.album-info-card {
  margin-top: 0px;
  padding: 10px;
  padding-bottom: 5px;
  background-color: var(--my-white) !important;
  border: none !important;
  width: 100%;
}
.info-card-text {
  font-size: 13px;
  line-height: 130%;
  padding-left: 2px;
}
.info-td {
  padding-left: 10px;
}
.born-died {
  font-size: 13px !important;
  color: grey !important;
}
a {
  color: black !important;
  font-weight: 600;
  font-size: 14px;
}
a:hover {
  color: black !important;
  text-decoration: underline !important;
  cursor: pointer;
}
table {
  margin-bottom: 6px;
}
.col{
  padding: 0px;
  padding-left: 5px;
}

</style>

