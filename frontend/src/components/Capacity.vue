<style>
</style>

<template>

<div id="app">
    <div class="container">
      <h1 class="header">Site Capacity</h1>
      <h3 class="header">Top 10 Capacity</h3>
        <canvas id="maxChart"></canvas>
    </div>
    <div class="container">
      <table class="table">
        <thead>
          <tr>
            <td scope="col">ID</td>
            <td scope="col">Capacity</td>
          </tr>
        </thead>
        <tr v-for="item in capacityTable" :key="item.site_id">
          <td><router-link :to="{ name: 'stats', params: { id: item.site_id }}">{{ item.site_id }}</router-link></td>
          <td>{{ item.capacity }}</td>
        </tr>
      </table>
    </div>

    <div class="container">
      <h3 class="header" style="margin-top: 1em;">Bottom 10 Capacity</h3>
        <canvas id="minChart"></canvas>
    </div>
    <div class="container">
      <table class="table">
        <thead>
          <tr>
            <td scope="col">ID</td>
            <td scope="col">Capacity</td>
          </tr>
        </thead>
        <tr v-for="item in minCapacityTable" :key="item.site_id">
          <td><router-link :to="{ name: 'stats', params: { id: item.site_id }}">{{ item.site_id }}</router-link></td>
          <td>{{ item.capacity }}</td>
        </tr>
      </table>
    </div>
</div>

</template>

<script>

import axios from 'axios'
import Chart from 'chart.js'
export default {
  name: 'Chart',
  data: function () {
    return {
      capacityTable: [],
      minCapacityTable: []
    }
  },
  mounted () {
    this.resetColor()
    this.createChart()
    this.getData(this)
  },
  watch: {
    $route (to, from) {
      this.clearChartData(this)
      this.resetColor()
      this.getData(this)
    }
  },
  methods: {
    resetColor () {
      this.currentColor = {
        r: 66,
        g: 134,
        b: 234
      }
    },
    cycleRGBColor (color) {
      if (color + 20 <= 255) {
        return color + 20
      } else {
        return 20 + (255 - color)
      }
    },
    getBorderColor () {
      this.currentColor.r = this.cycleRGBColor(this.currentColor.r)
      this.currentColor.g = this.cycleRGBColor(this.currentColor.g)
      this.currentColor.b = this.cycleRGBColor(this.currentColor.b)
      return `rgb(${this.currentColor.r}, ${this.currentColor.g}, ${this.currentColor.b})`
    },
    clearChartData (self) {
      self.chart.data.datasets = []
      self.chart.update()
    },
    getData (self) {
      axios.get(`${process.env.apiHost}capacity`)
        .then(function (response) {
          const maxItems = []
          const maxIds = []
          response.data.highest_capacity.forEach(function (item) {
            maxItems.push({x: item.site_id, y: item.capacity})
            maxIds.push('' + item.site_id)
            self.capacityTable.push(item)
          })
          self.maxChart.data.labels = maxIds

          self.maxChart.data.datasets.push({
            labels: maxIds,
            backgroundColor: '#94c635',
            borderColor: '#709628',
            borderWidth: 1,
            data: maxItems
          })
          self.maxChart.update()

          const minIds = []
          const minItems = []
          response.data.lowest_capacity.forEach(function (item) {
            minItems.push({x: item.site_id, y: item.capacity})
            minIds.push('' + item.site_id)
            self.minCapacityTable.push(item)
          })
          self.minChart.data.labels = minIds

          self.minChart.data.datasets.push({
            labels: minIds,
            backgroundColor: '#A50104',
            borderColor: '#590004',
            borderWidth: 1,
            data: minItems
          })
          self.minChart.update()
        })
        .catch(function (error) {
          console.log('Got error')
          console.log(error)
        })
    },
    createChart () {
      const maxCtx = document.getElementById('maxChart').getContext('2d')
      const minCtx = document.getElementById('minChart').getContext('2d')
      this.maxChart = new Chart(maxCtx, {
        // The type of chart we want to create
        type: 'bar',

        // The data for our dataset
        data: {
          datasets: []
        },

        // Configuration options go here
        options: {
          legend: {display: false},
          title: {
            display: true
          },
          scales: {
            xAxes: [{
              labelString: 'Site ID',
              barPercentage: 10,
              maxBarThickness: 60,
              minBarLength: 2,
              gridLines: {
                offsetGridLines: true
              },
              scaleLabel: {labelString: 'Site ID', display: true}
            }],
            yAxes: [{scaleLabel: {labelString: 'Watt-Hours', display: true}}]
          }
        }
      })

      this.minChart = new Chart(minCtx, {
        // The type of chart we want to create
        type: 'bar',

        // The data for our dataset
        data: {
          datasets: []
        },

        // Configuration options go here
        options: {
          legend: {display: false},
          title: {
            display: true
          },
          scales: {
            xAxes: [{
              labelString: 'Site ID',
              barPercentage: 10,
              maxBarThickness: 60,
              minBarLength: 2,
              gridLines: {
                offsetGridLines: true
              },
              scaleLabel: {labelString: 'Site ID', display: true}
            }],
            yAxes: [{scaleLabel: {labelString: 'Watt-Hours', display: true}}]
          }
        }
      })
    }
  }
}

</script>
