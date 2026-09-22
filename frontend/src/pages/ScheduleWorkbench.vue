<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getJSON, postJSON } from '../api'

const principal = ref(800000)
const annual_rate = ref(4.2)
const months = ref(360)
const dailyEnabled = ref(false)
const first_period_days = ref(45)
const out = ref(null)
const err = ref('')
const savedRunId = ref(null)
const loadedRunId = ref(null)

const route = useRoute()
const router = useRouter()

const buildPayload = (persist) => ({
  principal: Number(principal.value),
  annual_rate: Number(annual_rate.value),
  months: Number(months.value),
  // 未启用按日计息时不传 D，后端缺省按 30，与改造前一致
  first_period_days: dailyEnabled.value ? Number(first_period_days.value) : null,
  persist,
  preview_rows: 12,
})
const validDays = () => {
  const d = Number(first_period_days.value)
  return Number.isInteger(d) && d >= 1 && d <= 90
}
const calc = async (persist) => {
  err.value = ''
  if (dailyEnabled.value && !validDays()) { err.value = '首期天数 D 须为 1..90 的整数'; return }
  try {
    out.value = await postJSON('/api/schedule', buildPayload(persist))
    if (persist && out.value.run_id) {
      savedRunId.value = out.value.run_id
      loadedRunId.value = null
      router.replace({ query: { run: out.value.run_id } })
    }
  } catch (e) { err.value = e.message }
}
const fmt = (v) => (v === null || v === undefined ? '—' : Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }))

onMounted(async () => {
  // 带 run 打开：直接回显已存结果，首期利息与写入时一致
  if (route.query.run) {
    try {
      const rec = await getJSON(`/api/runs/${route.query.run}`)
      loadedRunId.value = rec.id
      const inp = rec.input_json || {}
      principal.value = inp.principal
      annual_rate.value = inp.annual_rate
      months.value = inp.months
      const d = inp.first_period_days
      dailyEnabled.value = d != null && d !== 30
      if (d != null) first_period_days.value = d
      out.value = rec.result_json
    } catch (e) { err.value = e.message }
  }
})
</script>
<template><div class="page"><h1>等额本息试算</h1>
<label>本金 <input v-model.number="principal" type="number" /></label>
<label>年利率% <input v-model.number="annual_rate" type="number" step="0.01" /></label>
<label>月数 <input v-model.number="months" type="number" /></label>
<label class="chk"><input type="checkbox" v-model="dailyEnabled" /> 首期按日计息</label>
<label v-if="dailyEnabled">起息至首次还款天数 D <input v-model.number="first_period_days" type="number" min="1" max="90" /> <small>(1..90，年利率/360×本金×D)</small></label>
<div class="actions">
  <button @click="calc(false)">试算（不保存）</button>
  <button class="alt" @click="calc(true)">保存记录</button>
</div>
<p v-if="err" class="err">{{ err }}</p>
<p v-if="loadedRunId" class="hint">已打开记录 #{{ loadedRunId }}（回显写入时结果）</p>
<p v-else-if="savedRunId" class="hint">已保存为记录 #{{ savedRunId }}</p>

<template v-if="out">
<h2>首期 / 后续对照</h2>
<table class="cmp">
  <tr><th></th><th>首期（D={{ out.first_period_days ?? 30 }} 天{{ out.daily_first_interest ? '，按日' : '，按月' }}）</th><th>第二期起</th></tr>
  <tr><td>利息</td><td>{{ fmt(out.first_interest) }}</td><td>—</td></tr>
  <tr><td>本金</td><td>{{ fmt(out.first_principal) }}</td><td>—</td></tr>
  <tr><td>月供</td><td class="hl">{{ fmt(out.first_payment) }}</td><td class="hl">{{ fmt(out.subsequent_payment) }}</td></tr>
</table>
<p>常规月供 {{ fmt(out.monthly_payment) }} · 利息合计 {{ fmt(out.total_interest) }}</p>
<h2>摊还预览</h2>
<table>
  <tr><th>期次</th><th>月供</th><th>本金</th><th>利息</th><th>余额</th></tr>
  <tr v-for="r in out.preview" :key="r.period" :class="{ first: r.period === 1 }">
    <td>第{{ r.period }}期</td><td>{{ fmt(r.payment) }}</td><td>{{ fmt(r.principal) }}</td><td>{{ fmt(r.interest) }}</td><td>{{ fmt(r.balance) }}</td>
  </tr>
</table>
</template>
</div></template>
<style scoped>
label { display:block; margin:0.4rem 0; }
label.chk { display:flex; align-items:center; gap:0.4rem; }
small { color:#7a6a52; }
.actions { display:flex; gap:0.6rem; margin:0.6rem 0; }
button.alt { background:#5a3a1a; }
.err { color:#a02020; }
.hint { color:#2f6b2f; }
table.cmp td, table.cmp th { text-align:right; }
table.cmp td:first-child, table.cmp th:first-child { text-align:left; }
.hl { font-weight:700; }
tr.first { background:#f3ead8; }
</style>
