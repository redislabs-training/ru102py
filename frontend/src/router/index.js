import Vue from 'vue'
import Router from 'vue-router'

import Map from '@/components/Map'
import Stats from '@/components/Stats'
import Capacity from '@/components/Capacity'
import Recent from '@/components/Recent'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Map',
      component: Map
    },
    {
      path: '/map',
      name: 'Map',
      component: Map
    },
    {
      path: '/stats',
      name: 'stats',
      component: Stats
    },
    {
      path: '/capacity',
      name: 'capacity',
      component: Capacity
    },
    {
      path: '/stats/:id',
      name: 'stats',
      component: Stats
    },
    {
      path: '/recent',
      name: 'Recent',
      component: Recent
    }
  ]
})
