<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
const principal = ref(800000)
const annual_rate = ref(4.2)
const months = ref(360)
const firstDaily = ref(false)
const firstDays = ref(30)
const persist = ref(true)
const out = ref(null)
const err = ref('')
const run = async () => {
  err.value = ''
  try {
    out.value = await postJSON('/api/schedule', {
      principal: principal.value, annual_rate: annual_rate.value, months: months.value,
      persist: persist.value, first_period_daily: firstDaily.value, first_period_days: firstDays.value,
    })
  } catch (e) {
    out.value = null
    err.value = '请求被拒绝，未写入记录：请检查输入（首期天数 D 须在 1–60 之间）'
  }
}
</script>
<template><div class="page"><h1>等额本息试算</h1>
<label>本金 <input v-model.number="principal" /></label>
<label>年利率% <input v-model.number="annual_rate" /></label>
<label>月数 <input v-model.number="months" /></label>
<label><input type="checkbox" v-model="firstDaily" /> 首期按日计息</label>
<label v-if="firstDaily">首期天数 D <input type="number" v-model.number="firstDays" min="1" max="60" /></label>
<label><input type="checkbox" v-model="persist" /> 写入记录</label>
<button @click="run">计算</button>
<p v-if="err" class="err">{{ err }}</p>
<template v-if="out">
<p>后续月供 {{ out.monthly_payment }} · 利息合计 {{ out.total_interest }}<template v-if="out.run_id"> · 已写入 #{{ out.run_id }}</template></p>
<table>
<tr><th></th><th>月供</th><th>利息</th><th>计息天数</th></tr>
<tr><td>首期</td><td>{{ out.first_period_payment }}</td><td>{{ out.first_period_interest }}</td><td>{{ out.first_period_daily ? out.first_period_days : '—' }}</td></tr>
<tr><td>后续每期</td><td>{{ out.monthly_payment }}</td><td>逐期递减</td><td>30</td></tr>
</table>
</template>
</div></template>
<style scoped>
.err { color: #a33; }
</style>
