<template>
  <b-row>
    <b-col>
      <div class="grid-container">
        <div class="grid-item" v-for="artist in artists" :key="artist[0]">
          <b-card class="album-info-card shadow-sm">
            <b-card-body class="card-body">
              <b-card-text class="info-card-text">
                <div>
                  <table>
                    <tr>
                      <td>
                        <b-avatar :badge="toK(artist[3])" badge-left badge-variant="dark" size="48px" :src="artist[1]"></b-avatar>
                      </td>
                      <td class="info-td">
                        <a class="artist-name" @click="wordClick(artist[0])">{{ artist[0] }}</a><br />
                        <span v-if="artist[2]" class="born-died">{{artist[2]}}<br></span>
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
        <div class="grid-item" v-for="artist in groups" :key="artist[0]">
          <b-card class="album-info-card shadow-sm">
            <b-card-body class="card-body">
              <b-card-text class="info-card-text">
                <div>
                  <table>
                    <tr>
                      <td>
                        <b-avatar :badge="toK(artist[3])" badge-left badge-variant="dark" size="48px" :src="artist[1]"></b-avatar>
                      </td>
                      <td class="info-td">
                        <a class="artist-name" @click="wordClick(artist[0])">{{ artist[0] }}</a><br />
                        <span v-if="artist[2]" class="born-died">{{artist[2]}}<br></span>
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
    toK(num){
      return num.toString().slice(0, -3) + "k";
    },
    wordClick(word){
      eventBus.$emit('requestComposersForArtist', word);
    }
  },
  created() {
    this.artists = require('@/assets/topartists.json');
    this.groups = require('@/assets/toporch.json')
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
  padding-top: 10px;
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
  overflow-x: hidden;
  padding-left: 2px;
}
.info-td {
  padding-left: 10px;
  white-space: nowrap; 
  text-overflow: ellipsis; 
  overflow: hidden; 
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
</style>

