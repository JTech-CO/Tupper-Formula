/** Native MathML Core: zero CDN requests, no bundled or remote fonts. */
export function mathElement(latex, markup) {
  const wrapper=document.createElement('div');
  // markup is from the repository's trusted registry, never from imported data.
  wrapper.innerHTML=`<math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><semantics>${markup}<annotation encoding="application/x-tex"></annotation></semantics></math>`;
  const math=wrapper.firstElementChild;
  math.querySelector('annotation').textContent=latex;
  return math;
}
export function populateEquation(element, record, translate) {
  if (!record) return;
  const title=element.querySelector('.equation-title');
  if (title && record.title) title.textContent=record.title[document.documentElement.lang==='ko'?'ko':'en'];
  const body=element.querySelector('.math-body');
  body.replaceChildren(mathElement(record.latex,record.mathml));
  const copy=element.querySelector('[data-copy-latex]');
  copy.dataset.copyLatex=record.latex;
  copy.textContent=translate('copy-latex');
  const code=element.querySelector('.tex-source code');
  if (code) code.textContent=record.latex;
  const summary=element.querySelector('.tex-source summary');
  if (summary) summary.textContent=translate('tex-source');
}
export function dynamicRecord(registry,h,variant='tupper') {
  const template=registry[variant==='bit'?'dynamic-bit':'dynamic'];
  return {latex:template.latex_template.replaceAll('__H__',String(h)),
    mathml:template.mathml_template.replaceAll('__H__',`<mn>${h}</mn>`)};
}
