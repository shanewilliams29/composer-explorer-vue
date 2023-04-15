<template>
  <b-row>
    <b-col>
      <div class="grid-container">
        <div class="grid-item" v-for="artist in conductors" :key="artist[0]">
          <b-card class="album-info-card shadow-sm">
            <b-card-body class="card-body">
              <b-card-text class="info-card-text">
                <div>
                  <table>
                    <tr>
                      <td>
                        <b-avatar size="56px" :src="artist[1]"></b-avatar>
                      </td>
                      <td class="info-td">
                        <a class="artist-name" @click="wordClick(artist[0])">{{ artist[0] }}</a><br />
                        <span v-if="artist[2] !== 'NA'" class="born-died">{{artist[2]}}<br></span>
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
        <div class="grid-item" v-for="artist in orchestras" :key="artist[0]">
          <b-card class="album-info-card shadow-sm">
            <b-card-body class="card-body">
              <b-card-text class="info-card-text">
                <div>
                  <table>
                    <tr>
                      <td>
                        <b-avatar size="56px" :src="artist[1]"></b-avatar>
                      </td>
                      <td class="info-td">
                        <a class="artist-name" @click="wordClick(artist[0])">{{ artist[0] }}</a><br />
                        <span v-if="artist[2] !== 'NA'" class="born-died">{{artist[2]}}<br></span>
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
        <div class="grid-item" v-for="artist in pianists" :key="artist[0]">
          <b-card class="album-info-card shadow-sm">
            <b-card-body class="card-body">
              <b-card-text class="info-card-text">
                <div>
                  <table>
                    <tr>
                      <td>
                        <b-avatar size="56px" :src="artist[1]"></b-avatar>
                      </td>
                      <td class="info-td">
                        <a class="artist-name" @click="wordClick(artist[0])">{{ artist[0] }}</a><br />
                        <span v-if="artist[2] !== 'NA'" class="born-died">{{artist[2]}}<br></span>
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
        <div class="grid-item" v-for="artist in singers" :key="artist[0]">
          <b-card class="album-info-card shadow-sm">
            <b-card-body class="card-body">
              <b-card-text class="info-card-text">
                <div>
                  <table>
                    <tr>
                      <td>
                        <b-avatar size="56px" :src="artist[1]"></b-avatar>
                      </td>
                      <td class="info-td">
                        <a class="artist-name" @click="wordClick(artist[0])">{{ artist[0] }}</a><br />
                        <span v-if="artist[2] !== 'NA'" class="born-died">{{artist[2]}}<br></span>
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
      // for (let i = array.length - 1; i > 0; i--) {
      //   const j = Math.floor(Math.random() * (i + 1));
      //   [array[i], array[j]] = [array[j], array[i]];
      // }
      return array;
    },
    toK(num){
      return num.toString().slice(0, -3) + "k";
    },
    wordClick(word){
      eventBus.$emit('requestComposersForArtist', word);
    }
  },
  created() {
    this.conductors = this.shuffleArray(require('@/assets/topconductors.json'));
    this.orchestras = this.shuffleArray(require('@/assets/toporchestras.json'));
    this.pianists = this.shuffleArray(require('@/assets/toppianists.json'));
    this.singers = this.shuffleArray(require('@/assets/topsingers.json'));
  },
}
</script>

<style scoped>
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  grid-gap: 5px;
  grid-auto-flow: dense;
  height: calc(100vh - 244px - var(--panelheight));
  overflow: auto;
  padding-bottom: 15px;
  padding-top: 5px;
}
.grid-item {
  display: flex;
  padding-right: 5px;
}
.album-info-card {
  margin-top: 5px;
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

