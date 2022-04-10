import axios from 'axios';
import {eventBus} from "./main.js";

var spotify = {

pressPlay(token, device_id) {
  const path = 'https://api.spotify.com/v1/me/player/play?device_id=' + device_id;
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
      console.log(res);
    })
    .catch((error) => {
      console.error(error);
    });
},

playTrack(token, device_id) {
  const path = 'https://api.spotify.com/v1/me/player/play?device_id=' + device_id;
  axios({
      method: 'put',
      url: path,
      data: {
        "context_uri": "spotify:album:5ht7ItJgpBH7W6vJ5BqpPr"
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
}

export default spotify
