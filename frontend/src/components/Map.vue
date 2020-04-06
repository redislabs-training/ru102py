<style>

#mapid {
    height: 900px;
}

</style>

<template>

<div id="app">
    <div class="container">
      <h1 class="header">Solar Site Map</h1>
    </div>
    <div class="container">
        <form v-on:submit.prevent="submitForm($event)" id="search" style="margin: 0.5em;">
            <div class="form-row m-1">
                <div class="col px-1">
                    <input id="lat" name="latitude" type="text" class="form-control" placeholder="Latitude">
                </div>
                <div class="col px-1">
                    <input id="lng" name="longitude" type="text" class="form-control" placeholder="Longitude">
                </div>
                <div class="col-sm-1 px-1">
                    <input name="radius" type="text" class="form-control" placeholder="Radius">
                </div>
                <div class="col2 px-1">
                    <select name="radiusUnit" class="custom-select">
                        <option selected="selected" value="km">KM (Kilometers)</option>
                        <option value="mi">MI (Miles)</option>
                    </select>
                </div>
                <div class="col2 px-1 form-check form-check-inline">
                  <input type="checkbox" name="onlyExcessCapacity" class="form-check-input" id="excessCapacityCheck">
                  <label class="form-check-label" for="excessCapacityCheck">Excess Capacity</label>
                </div>
                <div class="col2 px-1">
                    <button type="submit" class="btn btn-primary">Submit</button>
                </div>
            </div>
        </form>
    </div>
    <div class="container" id="mapid"></div>
</div>

</template>

<script>
import {
  L, LMap, LTileLayer, LMarker
}
  from 'vue2-leaflet'
import axios from 'axios'

export default {
  name: 'App',
  components: {
    LMap,
    LTileLayer,
    LMarker
  },
  mounted () {
    this.createMap()
    this.getData()
  },
  methods: {
    submitForm (event) {
      this.markerLayers.clearLayers()
      console.log(event.srcElement)

      const args = {
        params: {
          lat: event.target.lat.value,
          lng: event.target.lng.value,
          radius: event.target.radius.value,
          radius_unit: event.target.radiusUnit.value,
          only_excess_capacity: event.target.onlyExcessCapacity.checked
        }
      }
      const bounds = []
      axios.get(`${process.env.apiHost}sites`, args)
        .then((response) => {
          response.data.forEach((site) => {
            this.addMarker(site)
            bounds.push([site.coordinate.lat, site.coordinate.lng])
          })
          this.mymap.fitBounds(bounds)
        })
        .catch(function (error) {
          console.log(error)
        })
    },
    getData () {
      var self = this
      axios.get(`${process.env.apiHost}sites`)
        .then(function (response) {
          response.data.forEach(function (site) {
            self.addMarker(site)
          })
        })
        .catch(function (error) {
          alert('Could not connect to backend. Is it running?')
          console.log(error)
        })
    },
    addMarker (site) {
      const coordinate = site.coordinate
      const marker = L.marker([coordinate.lat, coordinate.lng]).addTo(this.markerLayers)
      marker.bindPopup(`<b>${site.address}</b><br/>${site.city}, ${site.state} ${site.postal_code}<br>(${site.coordinate.lat}, ${site.coordinate.lng})<br/><a href="#/stats/${site.id}">Stats</a>`)
    },
    createMap () {
      this.mymap = L.map('mapid').setView([37.715732, -122.027342], 11)
      this.markerLayers = L.featureGroup().addTo(this.mymap)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png?',
        { attribution: 'Map and Image data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors. <a href="https://www.openstreetmap.org/copyright">License</a>.' }
      ).addTo(this.mymap)
    }
  }
}

</script>
