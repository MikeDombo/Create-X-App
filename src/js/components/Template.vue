<template>
  <div>
    <strong v-if="loading">Loading...</strong>
    <div v-if="manifestData">
      <h1>{{manifestData.title}}</h1>
      <h3>{{manifestData.author}}</h3>
      <small>
        <a :href="manifestData.repository">Project Repository</a>
      </small>
      <p>{{manifestData.description}}</p>
    </div>
    <form @submit.prevent="submit">
      <div
        class="form"
        v-if="manifestData.uses_template_variables && manifestData.required_template_variables"
      >
        <template v-for="(variableData, variableName) in manifestData.required_template_variables">
          <div v-bind:key="variableName">
            <label
              v-bind:class="{requiredLabel: !variableData.type.includes('opt(')}"
            >{{variableName}}</label>
            <input
              type="text"
              v-if="variableData.type.includes('string')"
              v-model.trim="formData[variableName]"
            >
            <input
              type="number"
              v-if="variableData.type.includes('integer')"
              v-model.number="formData[variableName]"
            >
          </div>
        </template>
      </div>
      <button class="button btn-primary btn-large" type="submit">Create App Now!</button>
    </form>
  </div>
</template>

<script>
import jsyaml from "js-yaml";
import urljoin from "url-join";
export default {
  name: "Template",
  data() {
    return {
      loading: false,
      url: this.$route.query.url,
      manifestData: {},
      formData: {}
    };
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData: async function() {
      this.loading = true;

      const rawManifestURL = urljoin(
        this.url.replace("github.com", "raw.githubusercontent.com"),
        "master/manifest.cxa.yml"
      );

      this.manifestData = jsyaml.load(
        await (await fetch(rawManifestURL)).text()
      );
      this.loading = false;
    },

    submit: function() {
      console.log("submit");
      fetch("http://localhost:8000/transform", {
        method: "POST",
        body: JSON.stringify({
          gitURL: this.url.replace(/\/$/, "") + ".git",
          template_variables: this.formData
        }),
        headers: { "Content-Type": "application/json" }
      }).then(r => {
        if (r.status === 200) {
          r.blob().then(b => {
            var link = document.createElement("a");
            link.href = window.URL.createObjectURL(b);
            link.download = this.manifestData.title + ".zip";

            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
          });
        }
      });
    }
  }
};
</script>

<style>
.requiredLabel::after {
  content: "*";
  color: red;
}
</style>
