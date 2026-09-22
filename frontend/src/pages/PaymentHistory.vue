<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const detail = ref(null)
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
const open = async (id) => { detail.value = await getJSON('/api/history/' + id) }
const fmt = (v) => (v === null || v === undefined ? '—' : v)
</script>
<template><div class="page"><h1>试算记录</h1>
<table><tr v-for="h in items" :key="h.id" style="cursor:pointer" @click="open(h.id)"><td>#{{ h.id }}</td><td>{{ h.kind }}</td><td>{{ h.created_at }}</td></tr></table>
<div v-if="detail" class="page">
<h2>记录 #{{ detail.id }}</h2>
<p>本金 {{ detail.input.principal }} · 年利率 {{ detail.input.annual_rate }}% · {{ detail.input.months }} 期<template v-if="detail.input.first_period_daily"> · 首期按日计息 D={{ detail.result.first_period_days }} 天</template></p>
<p>首期利息 {{ fmt(detail.result.first_period_interest) }} · 首期月供 {{ fmt(detail.result.first_period_payment) }} · 后续月供 {{ detail.result.monthly_payment }}</p>
</div>
</div></template>
