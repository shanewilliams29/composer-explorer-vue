import axios from 'axios';
import {eventBus} from "./main.js";

var spotify = {

// may need to use flask endpoint for this
pressPlay(token, device_id) {
  const path = 'https://api.spotify.com/v1/me/player/play';
  axios({
      method: 'put',
      url: path,
      params: {
        'device_id' : device_id
      },
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    })
    .then((res) => {
      if (res.status == 204) {
        eventBus.$emit('fireNowPlaying');
      } else {
        eventBus.$emit('fireNowPaused');
      }
      console.log(res);
    })
    .catch((error) => {
      console.error(error);
    });
},

pauseTrack(token) {
  const path = 'https://api.spotify.com/v1/me/player/pause';
  axios({
      method: 'put',
      url: path,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    })
    .then((res) => {
      if (res.status == 204) {
        eventBus.$emit('fireNowPaused');
      } else {
        eventBus.$emit('fireNowPlaying');
      }
      console.log(res);
    })
    .catch((error) => {
      console.error(error);
    });
},

playTracks(token, device_id, tracks) {
  const path = 'https://api.spotify.com/v1/me/player/play';
  axios({
      method: 'put',
      url: path,
      data: tracks,
      params: {
        'device_id' : device_id
      },
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    })
    .then((res) => {
      if (res.status == 204) {
        eventBus.$emit('fireNowPlaying');
      } else {
        eventBus.$emit('fireNowPaused');
      }
      console.log(res);
    })
    .catch((error) => {
      console.error(error);
    });
},
}

export default spotify
