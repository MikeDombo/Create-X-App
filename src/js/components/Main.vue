<template>
  <div>
    <strong v-if="loading">Loading...</strong>
    <ul v-if="manifestData">
      <li v-for="(data, url) in manifestData" v-bind:key="url">
        <router-link :to="{path: 'template', query: {url}}">{{data.title}}</router-link>
        <br>
        <small>{{data.description}}</small>
      </li>
    </ul>
  </div>
</template>

<script>
import jsyaml from "js-yaml";
export default {
  name: "Main",
  data() {
    return {
      loading: false,
      manifestData: []
    };
  },
  created() {
    this.onMount();
  },
  methods: {
    onMount: async function() {
      this.loading = true;
      const manifests = [
        [
          "https://github.com/MikeDombo/CXAPythonCLI/",
          "https://raw.githubusercontent.com/MikeDombo/CXAPythonCLI/master/manifest.cxa.yml"
        ]
      ];

      this.manifestData = await manifests.reduce(async (soFar, v) => {
        soFar[v[0]] = jsyaml.load(await (await fetch(v[1])).text());
        return soFar;
      }, {});
      this.loading = false;
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
