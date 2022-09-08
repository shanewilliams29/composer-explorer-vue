<template>
  <div id="userlist">
    <div class="container-fluid">
      <b-row>
        <b-col class="user-list" v-html="composers"></b-col>
      </b-row>
    </div>
  </div>
</template>

<script>

import axios from 'axios';
import moment from "../moment.js";

function flask_moment_render(elem) {{
    const timestamp = moment(elem.dataset.timestamp);
    const func = elem.dataset.function;
    const format = elem.dataset.format;
    const timestamp2 = elem.dataset.timestamp2;
    const no_suffix = elem.dataset.nosuffix;
    const units = elem.dataset.units;
    let args = [];
    if (format)
        args.push(format);
    if (timestamp2)
        args.push(moment(timestamp2));
    if (no_suffix)
        args.push(no_suffix);
    if (units)
        args.push(units);
    elem.textContent = timestamp[func].apply(timestamp, args);
    elem.classList.remove('flask-moment');
    elem.style.display = "";
}}
function flask_moment_render_all() {{
    const moments = document.querySelectorAll('.flask-moment');
    moments.forEach(function(moment) {{
        flask_moment_render(moment);
        const refresh = moment.dataset.refresh;
        if (refresh && refresh > 0) {{
            (function(elem, interval) {{
                setInterval(function() {{
                    flask_moment_render(elem);
                }}, interval);
            }})(moment, refresh);
        }}
    }})
}}

export default {
  name: 'UserList',
  data() {
    return {
      composers: [],
    };
  },
  methods: {
    getComposers() {
      this.loading = true;
      moment.locale("en");
      const path = '/user_list';
      axios.get(path)
        .then((res) => {
          this.composers = res.data;
          setTimeout(function() { flask_moment_render_all(); }, 1000);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.loading=false;
        });
    },
  },
  created() {
    this.getComposers();
  },
}
</script>
<style scoped>
.user-list{
    height: calc(100vh - 244px - var(--panelheight));
    overflow-y: scroll;
    overflow-x: hidden;
}
</style>
