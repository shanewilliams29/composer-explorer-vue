<template>
  <div>
    <!-- Image and text -->
    <b-navbar type="dark" variant="dark">
      <b-navbar-brand href="#">
        <img src="../assets/logo.png" class="d-inline-block align-top" alt="Logo" height="40px">
      </b-navbar-brand>
      <b-navbar-nav>
        <b-nav-item href="#">Home</b-nav-item>

        <!-- Navbar dropdowns -->
        <b-nav-item-dropdown text="User">
          <b-dropdown-item href="#">Account</b-dropdown-item>
          <b-dropdown-item href="#">Settings</b-dropdown-item>
        </b-nav-item-dropdown>
      </b-navbar-nav>
    </b-navbar>
  </div>
</template>

<script>
export default {
  name: 'NavBar',
  props: {
    msg: String
  }
}
</script>

<style scoped>
img {
  margin-left: 20px;
}
.navbar.navbar-dark.bg-dark{
  background-color: #343a40!important;
}
</style>
