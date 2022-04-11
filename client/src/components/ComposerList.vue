<template>
  <div>
    <div class="spinner" v-show="loading" role="status">
      <b-spinner class="m-5"></b-spinner>
    </div>
    <div class="row">
      <b-card-group deck v-show="!loading">
        <b-card
          v-for="(region, index) in composers"
          :key="index"
          no-body
          header-tag="header"
        >
          <template #header>
            <h6 class="mb-0">{{ index }}</h6>
          </template>
          <b-card-text>
            <table cellspacing="0">
              <tr
                v-for="composer in region"
                :key="composer.id"
                @click="selectRow(composer.id); getWorks(composer.name_short);"
                :class="{'highlight': (composer.id == selectedComposer)}"
              >
                <td
                  width="2%"
                  :style="{border: 'solid 0px !important', backgroundColor:composer.color, opacity: 0.66}"
                ></td>
                <td width="2%"></td>
                <td width="12%" style="white-space: nowrap">
                  <img
                    class="composer-img"
                    :src="composer.flag"
                    height="20"
                    width="20"
                  />
                  <img
                    class="composer-img"
                    :src="composer.img"
                    height="20"
                    width="20"
                  />
                </td>
                <td
                  width="50%"
                  style="
                    white-space: nowrap;
                    text-overflow: ellipsis;
                    overflow: hidden;
                    max-width: 1px;
                  "
                >
                  {{ composer.name_full }}
                </td>
                <td
                  width="25%"
                  style="
                    white-space: nowrap;
                    text-overflow: ellipsis;
                    max-width: 1px;
                    text-align: right;
                  "
                >
                  {{ composer.born }} - {{ composer.died }}
                </td>
              </tr>
            </table>
          </b-card-text>
        </b-card>
      </b-card-group>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import {eventBus} from "../main.js";

export default {
  data() {
    return {
      composers: [],
      loading: false,
      selectedComposer: null
    };
  },
  methods: {
    getComposers() {
      this.loading = true;
      const path = 'api/composers';
      axios.get(path)
        .then((res) => {
          this.composers = res.data.composers;
          this.loading=false;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading=false;
        });
    },
    getFilteredComposers(item) {
      this.loading = true;
      const path = 'api/composers?filter=' + item;
      axios.get(path)
        .then((res) => {
          this.composers = res.data.composers;
          this.loading=false;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading=false;
        });
    },
    getSearchComposers(item) {
      const path = 'api/composers?search=' + item;
      axios.get(path)
        .then((res) => {
          this.composers = res.data.composers;
          this.loading=false;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading=false;
        });
    },
    getWorks(composer) {
        eventBus.$emit('fireComposers', composer);
        //this.$refs.composer.selectColor = "blue";
    },
    selectRow(composer){
        this.selectedComposer = composer;
    },
  },
  created() {
    this.getComposers();
    this.selectRow("1")
    eventBus.$on('fireComposerFilter', (item) => {
        this.getFilteredComposers(item);
    })
    eventBus.$on('fireComposerSearch', (item) => {
        this.getSearchComposers(item);
    })
  },
};
</script>

<style scoped>
.card-deck {
  display: flex;
  flex-direction: column;
  width: 100%;
}
.card {
  width: 100%;
}
td {
  padding: 1px;
  vertical-align: bottom;
  border-top: 1px dotted lightgray;
}
tr {
  border-bottom: 0px;
}
table {
  width: 100%;
  border-collapse: separate;
  font-size: 12px;
  padding: 6px;
  padding-bottom: 2px;
}
.highlight td {
  border-top: 0px solid lightgray;
  background-color: rgb(52, 58, 64, 0.7);
  color: white;
}
tr:hover {
  cursor: pointer;
}
.highlight td:last-child {
  position: relative;
}

.highlight td:last-child:after {
  content: "";
  position: absolute;
  top: 0px;
  bottom: 0px;
  width: 6px;
  display: block;
  background: inherit;
  border: inherit;
  left: 100%;
}
.composer-img {
  border-radius: 50%;
  object-fit: cover;
}
header.card-header {
  background-color: #fff;
  border: none;
  padding-left: 10px;
  padding-bottom: 0px;
}
.mb-0 {
  font-size: 14px;
  font-weight: bold;
}
.spinner {
  text-align: center;
}
.m-5 {
  color: #343a40;
}
.card {
  background-color: #fff;
  border: none;
  margin-top: 5px;
}
.card-deck {
  padding-left: 5px;
  padding-right: 5px;
}
</style>
