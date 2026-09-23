import mermaid from 'mermaid'

mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'loose',
})

let idCounter = 0

export async function renderMermaid(element) {
  const blocks = element.querySelectorAll('code.language-mermaid')
  for (const block of blocks) {
    const code = block.textContent
    const container = block.parentElement
    try {
      const id = `mermaid-${++idCounter}`
      const { svg } = await mermaid.render(id, code)
      container.outerHTML = `<div class="mermaid">${svg}</div>`
    } catch (e) {
      container.outerHTML = `<pre class="mermaid-error">图表渲染失败: ${e.message}</pre>`
    }
  }
}
