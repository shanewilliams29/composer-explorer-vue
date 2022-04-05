<template>
  <div v-if="albums">
  <div class ="row">
    {{ albums }}
  </div>
  </div>
  <div v-else>
    <div class ="row">
    <span class="no-albums-found"><br>No albums found.</span>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      albums: [],
    };
  },
  methods: {
    getAlbums(id) {
      const path = 'http://localhost:5000/api/albums/' + id;
      axios.get(path)
        .then((res) => {
          this.albums = res.data.status;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {
    this.getAlbums('Cake');
  },
};
</script>


<style scoped>
td{
   padding: 1px;
   vertical-align: bottom;
   border-top: 1px dotted lightgray;
}
tr{
  border-bottom: 0px;
}
table{
   width: 100%;
   border-collapse: separate;
   font-size: 12px;
   padding: 6px;
   padding-bottom: 2px;
}
.composer-img{
    border-radius: 50%;
    object-fit: cover;
}
header.card-header{
  background-color: #fff;
  border: none;
  padding-left: 10px;
  padding-bottom: 0px;
}
.mb-0{
  font-size: 14px;
  font-weight: bold;
}
.card{
  background-color: #fff;
  border: none;
  margin-top: 5px;
}
.card-deck{
  padding-left: 5px;
  padding-right: 5px;
}
.badge{
  color: #fff;
  background-color: #777777;
  border-radius: 7px;
}
.no-albums-found{
  font-size: 14px;
  color: grey;
  text-align: center;
}
</style>
