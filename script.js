const PHONE = '9779845656595';
const NE = document.documentElement.lang === 'ne';
const T = NE ? {
  hello: 'नमस्ते धर्मराज कार्टेल, मलाई मूल्य चाहियो।', name: 'नाम: ', biz: 'व्यवसाय: ', line: 'सामानको किसिम: ', qty: 'परिमाण: ', details: 'विवरण: ',
  ask: 'मूल्य सोध्नुहोस्', askLabel: n => n + ' को मूल्य सोध्नुहोस्', askMsg: 'नमस्ते धर्मराज कार्टेल, कृपया यसको मूल्य, स्टक र डेलिभरी बताउनुहोस्: ',
  count: n => n + ' वटा सामान', none: 'मिल्ने सामान भेटिएन। अर्को शब्द वा समूह प्रयोग गर्नुहोस्।'
} : {
  hello: 'Namaste Dharamraj Cartel, I would like a price.', name: 'Name: ', biz: 'Business: ', line: 'Product line: ', qty: 'Quantity: ', details: 'Details: ',
  ask: 'Ask price', askLabel: n => 'Ask the price of ' + n, askMsg: 'Namaste Dharamraj Cartel, please share price, stock and delivery for: ',
  count: n => n + ' products', none: 'No products match. Try another word or group.'
};
const whatsapp = text => 'https://wa.me/' + PHONE + '?text=' + encodeURIComponent(text);

const form = document.getElementById('form');
if (form) {
  const value = id => document.getElementById(id).value.trim();
  document.querySelectorAll('[data-line]').forEach(link => {
    link.addEventListener('click', () => { document.getElementById('f-line').value = link.dataset.line; });
  });
  form.addEventListener('submit', event => {
    event.preventDefault();
    const lines = [
      T.hello,
      T.name + value('f-name'),
      T.biz + (value('f-biz') || '-'),
      T.line + value('f-line'),
      T.qty + (value('f-qty') || '-'),
      T.details + value('f-msg')
    ];
    window.open(whatsapp(lines.join('\n')), '_blank', 'noopener,noreferrer');
  });
}

const list = document.getElementById('goods');
if (list) {
  const LINES = {
    vehicle: ['Motorcycle Parts', 'Motor Vehicle Parts'],
    electrical: ['Electrical', 'Electronics'],
    machinery: ['Machinery Parts'],
    hardware: ['Hardware', 'Wires', 'G.I. Wire', 'Welding Rod', 'Slotted Angle'],
    construction: ['Cement', 'Fiber', 'G.I. Sheet', 'GI Pipes', 'M.S. Pipe', 'M.S. Section', 'Sheets', 'Shutter Section']
  };
  const search = document.getElementById('search');
  const group = document.getElementById('group');
  const count = document.getElementById('count');
  const chips = [...document.querySelectorAll('#lines [data-line]')];
  let line = new URLSearchParams(location.search).get('line') || '';
  if (!LINES[line]) line = '';

  const fillGroups = () => {
    const keep = group.value;
    group.length = 1;
    [...new Set(GOODS.map(g => g.c))]
      .filter(c => !line || LINES[line].includes(c))
      .forEach(c => group.add(new Option(c, c)));
    group.value = [...group.options].some(o => o.value === keep) ? keep : '';
  };

  const render = () => {
    const q = search.value.trim().toLowerCase();
    const found = GOODS.filter(g =>
      (!line || LINES[line].includes(g.c)) &&
      (!group.value || g.c === group.value) &&
      (g.n + ' ' + g.c).toLowerCase().includes(q));
    list.replaceChildren(...found.map(g => {
      const li = document.createElement('li');
      const name = document.createElement('strong');
      const cat = document.createElement('span');
      const ask = document.createElement('a');
      name.textContent = g.n;
      cat.textContent = g.c;
      ask.textContent = T.ask;
      ask.setAttribute('aria-label', T.askLabel(g.n));
      ask.href = whatsapp(T.askMsg + g.n);
      ask.target = '_blank';
      ask.rel = 'noopener noreferrer';
      li.append(name, cat, ask);
      return li;
    }));
    count.textContent = found.length ? T.count(found.length) : T.none;
  };

  const setLine = value => {
    line = value;
    chips.forEach(c => c.setAttribute('aria-pressed', String(c.dataset.line === line)));
    const url = new URL(location.href);
    if (line) url.searchParams.set('line', line); else url.searchParams.delete('line');
    history.replaceState(null, '', url);
    fillGroups();
    render();
  };

  chips.forEach(c => c.addEventListener('click', () => setLine(c.dataset.line)));
  search.addEventListener('input', render);
  group.addEventListener('change', render);
  setLine(line);
}
