<style>
</style>

<template>
<div id="app">
    <div class="container margin-md">
      <h1 class="header">Recent Meter Readings</h1>
    </div>
    <div class="container">
      <table class="table">
        <thead>
          <tr>
            <td scope="col">Timestamp</td>
            <td scope="col">Site ID</td>
            <td scope="col">Watt-hours Generated</td>
            <td scope="col">Watt-hours Used</td>
            <td scope="col">Temp (Celsius)</td>
          </tr>
        </thead>
        <tr v-for="reading in meterReadings" :key="reading.site_id">
          <td>{{ new Date(reading.timestamp * 1000).toISOString() }}</td>
          <td><router-link :to="{ name: 'stats', params: { id: reading.site_id }}">{{ reading.site_id }}</router-link></td>
          <td>{{ Number.parseFloat(reading.wh_generated).toPrecision(4) }}</td>
          <td>{{ Number.parseFloat(reading.wh_used).toPrecision(4) }}</td>
          <td>{{ Number.parseFloat(reading.temp_c).toPrecision(4) }}</td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script>
</script>

<style>
</style>

<script>

import axios from 'axios'
export default {
  name: 'Recent',
  data: function () {
    return {
      meterReadings: [],
    }
  },
  mounted () {
    this.getData()
  },
  methods: {
    getData () {
      axios.get(`${process.env.apiHost}meter_readings`)
        .then((response) => {
          this.meterReadings = response.data.readings
        })
        .catch(function (error) {
          console.log('Got error')
          console.log(error)
        })
      }
    }
}

</script>
