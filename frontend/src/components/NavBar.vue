<template>
  <nav id="main" class="navbar navbar-expand-lg navbar-light bg-dark">
    <div class="container">

    <img class="navbar-brand" src="/static/img/redis-u-small.png" />
    <a class="navbar-brand text-white" href="#">Solar Power Dashboard</a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      <ul class="navbar-nav mr-auto">
        <li class="nav-item">
          <router-link class="nav-link text-light" to="/map">Map</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link text-light" to="/stats/1">Stats</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link text-light" to="/capacity">Capacity</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link text-light" to="/recent">Recent</router-link>
        </li>
      </ul>
    </div>
  </div>
  </nav>
</template>

<script>
</script>

<style scoped>
 li.router-link-active,
 li.router-link-exact-active {
   background-color: indianred;
   cursor: pointer;
 }
</style>
