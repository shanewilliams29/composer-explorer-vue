<template>
  <div class="container-fluid">
    <b-row class="flex-nowrap">
      <b-col class="text-center">
        <div class="vertical-centered">
          <table>
            <tr class="tr-performer">
              <td>
                <b-avatar class="avatar" size="64px" :src="$auth.avatar"></b-avatar>
              </td>
              <td class="td-text">
                <span class="display-name">{{ $auth.displayName }}</span><br />
                <span class="my-favorites">My Favorites</span>
              </td>
            </tr>
          </table>
        </div>
      </b-col>
    </b-row>
  </div>
</template>

<script>
export default {
  name: 'BrowseHeading',
};
</script>

<style scoped>
  .spinner {
  text-align: center;
  color: grey;
}
.container-fluid {
  background-color: var(--medium-gray);
  color: var(--search-gray);
}
.vertical-centered{
  height: 78px;
  line-height: 78px;
  text-align: center;
}
table {
  display: inline-block;
  text-align: left;
  vertical-align: middle;
  line-height: normal;
  margin-bottom: 3px;
}
.display-name{
  font-size: 20px;
  color: var(--my-white);
}
.my-favorites{
  color: var(--medium-light-gray);
  font-size: 16px;
}
.avatar{
  margin-right: 10px;
}
.col {
  padding: 0px;
}
</style>
