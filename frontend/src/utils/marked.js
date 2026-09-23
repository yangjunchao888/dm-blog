import { marked } from 'marked'

function slugify(text) {
  return text.toLowerCase().replace(/<[^>]+>/g, '').replace(/[^a-z0-9\u4e00-\u9fa5]+/g, '-').replace(/(^-|-$)/g, '')
}

const renderer = {
  heading(text, level) {
    const id = slugify(text)
    return `<h${level} id="${id}">${text}</h${level}>\n`
  },
  code(code, language) {
    if (language === 'mermaid') {
      return `<pre><code class="language-mermaid">${code}</code></pre>`
    }
    return false
  },
}

marked.use({ breaks: true, gfm: true, renderer })

export { marked }
