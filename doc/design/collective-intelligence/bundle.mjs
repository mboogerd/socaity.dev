import { readFile, writeFile } from 'node:fs/promises';

const read = (name) => readFile(new URL(name, import.meta.url), 'utf8');
const [html, css, js] = await Promise.all([
  read('index.html'), read('styles.css'), read('app.js'),
]);
const stylesheet = '<link rel="stylesheet" href="styles.css">';
const script = '  <script src="app.js" defer></script>\n';
if (!html.includes(stylesheet) || !html.includes(script) || !html.includes('</body>')) {
  throw new Error('Source asset references changed; update the bundler before exporting.');
}
const bundled = html
  .replace(stylesheet, () => `<style>\n${css}\n</style>`)
  .replace(script, '')
  .replace('</body>', () => `<script>\n${js}\n</script>\n</body>`);
await writeFile(new URL('preview.html', import.meta.url), bundled);
console.log('Created preview.html with embedded styles and interactions.');
