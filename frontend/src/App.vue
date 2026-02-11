<script setup>
import { ref, nextTick } from 'vue'
import mermaid from 'mermaid'

mermaid.initialize({ startOnLoad: false, theme: 'neutral' })

const prompt = ref('')
const diagramType = ref('auto')
const skipRefine = ref(false)
const loading = ref(false)
const error = ref('')
const mermaidCode = ref('')
const domain = ref('')

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function generate() {
  if (!prompt.value.trim()) return

  loading.value = true
  error.value = ''
  mermaidCode.value = ''
  domain.value = ''

  try {
    const res = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: prompt.value,
        diagram_type: diagramType.value,
        skip_refine: skipRefine.value,
      }),
    })

    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.detail || `Request failed (${res.status})`)
    }

    const data = await res.json()
    mermaidCode.value = data.code
    domain.value = data.domain || ''

    await nextTick()
    await renderDiagram(data.code)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function renderDiagram(code) {
  const container = document.getElementById('diagram')
  if (!container) return
  try {
    const { svg } = await mermaid.render('mermaid-output', code)
    container.innerHTML = svg
  } catch (e) {
    error.value = `Render error: ${e.message}`
  }
}

function getSvg() {
  const el = document.getElementById('diagram')
  return el ? el.innerHTML : ''
}

function openInNewTab() {
  const svg = getSvg()
  if (!svg) return
  const blob = new Blob([svg], { type: 'image/svg+xml' })
  window.open(URL.createObjectURL(blob), '_blank')
}

function saveToFile() {
  const svg = getSvg()
  if (!svg) return
  const blob = new Blob([svg], { type: 'image/svg+xml' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'diagram.svg'
  a.click()
}

const copied = ref(false)

function copySource() {
  if (!mermaidCode.value) return
  navigator.clipboard.writeText(mermaidCode.value).then(() => {
    copied.value = true
    setTimeout(() => (copied.value = false), 1500)
  })
}
</script>

<template>
  <div class="app">
    <header>
      <h1>text-to-UML</h1>
    </header>

    <main>
      <section class="input-section">
        <textarea
          v-model="prompt"
          placeholder="Describe a system or process..."
          rows="4"
          :disabled="loading"
          @keydown.meta.enter="generate"
          @keydown.ctrl.enter="generate"
        />

        <div class="controls">
          <select v-model="diagramType" :disabled="loading">
            <option value="auto">auto</option>
            <option value="flowchart">flowchart</option>
            <option value="sequence">sequence</option>
            <option value="class">class</option>
            <option value="erd">erd</option>
          </select>

          <label class="checkbox">
            <input type="checkbox" v-model="skipRefine" :disabled="loading" />
            skip refine
          </label>

          <button @click="generate" :disabled="loading || !prompt.trim()">
            {{ loading ? 'Generating...' : 'Generate' }}
          </button>
        </div>
      </section>

      <section v-if="loading" class="status">
        <div class="spinner" />
        <span>Generating diagram...</span>
      </section>

      <section v-if="error" class="error">
        {{ error }}
      </section>

      <section v-if="mermaidCode" class="output">
        <div v-if="domain" class="domain-tag">domain: {{ domain }}</div>
        <div id="diagram" class="diagram" />

        <div class="actions">
          <button class="action-btn" @click="openInNewTab">open in new tab</button>
          <button class="action-btn" @click="saveToFile">save svg</button>
          <button class="action-btn" @click="copySource">
            {{ copied ? 'copied!' : 'copy source' }}
          </button>
        </div>

        <details>
          <summary>Mermaid source</summary>
          <pre>{{ mermaidCode }}</pre>
        </details>
      </section>
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: monospace;
  background: #fff;
  color: #000;
}

.app {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

header h1 {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #000;
}

textarea {
  width: 100%;
  font-family: monospace;
  font-size: 0.875rem;
  padding: 0.75rem;
  border: 2px solid #000;
  resize: vertical;
  outline: none;
}

textarea:focus {
  border-color: #444;
}

.controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.75rem;
}

select {
  font-family: monospace;
  font-size: 0.875rem;
  padding: 0.4rem 0.5rem;
  border: 2px solid #000;
  background: #fff;
  cursor: pointer;
}

.checkbox {
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  cursor: pointer;
}

button {
  margin-left: auto;
  font-family: monospace;
  font-size: 0.875rem;
  font-weight: 700;
  padding: 0.5rem 1.25rem;
  border: 2px solid #000;
  background: #000;
  color: #fff;
  cursor: pointer;
}

button:hover:not(:disabled) {
  background: #333;
}

button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1.5rem;
  font-size: 0.875rem;
}

.spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid #ccc;
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error {
  margin-top: 1.5rem;
  padding: 0.75rem;
  border: 2px solid #000;
  background: #f5f5f5;
  font-size: 0.875rem;
}

.output {
  margin-top: 1.5rem;
}

.domain-tag {
  font-size: 0.75rem;
  margin-bottom: 0.5rem;
  color: #555;
}

.diagram {
  border: 2px solid #000;
  padding: 1rem;
  overflow-x: auto;
}

.diagram svg {
  max-width: 100%;
  height: auto;
}

.actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.action-btn {
  margin-left: 0;
  font-weight: 400;
  padding: 0.3rem 0.75rem;
  background: #fff;
  color: #000;
  border: 1px solid #000;
  font-size: 0.8rem;
}

.action-btn:hover:not(:disabled) {
  background: #000;
  color: #fff;
}

details {
  margin-top: 0.75rem;
}

summary {
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0.25rem 0;
}

pre {
  margin-top: 0.5rem;
  padding: 0.75rem;
  border: 1px solid #ccc;
  background: #fafafa;
  font-size: 0.8rem;
  overflow-x: auto;
  white-space: pre-wrap;
}
</style>
