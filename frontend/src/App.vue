<style>
#app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
}

  .header {
    margin: 0.5em;
  }
</style>

<template>

<div id="app">
    <nav-bar></nav-bar>
    <router-view></router-view>
</div>

</template>

<script>
/* eslint-disable */

import Map from './components/Map.vue'
import NavBar from './components/NavBar.vue'
import Stats from './components/Stats.vue'
import Capacity from './components/Capacity.vue'
import Foot from './components/Foot.vue'
export default {
    name: "app",
    components: {
        Map,
        NavBar,
        Stats,
        Foot,
        Capacity
    }
}

</script>
