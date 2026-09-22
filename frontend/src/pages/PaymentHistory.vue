<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
</script>
<template><div class="page"><h1>试算记录</h1><table>
  <tr><th>记录</th><th>类型</th><th>时间</th><th></th></tr>
  <tr v-for="h in items" :key="h.id">
    <td>#{{ h.id }}</td><td>{{ h.kind }}</td><td>{{ h.created_at }}</td>
    <td><router-link v-if="h.kind === 'schedule'" :to="`/schedule?run=${h.id}`">打开</router-link></td>
  </tr>
</table></div></template>
