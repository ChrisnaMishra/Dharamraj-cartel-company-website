const PHONE = '9779845656595';
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
      'Namaste Dharamraj Cartel, I would like a price.',
      'Name: ' + value('f-name'),
      'Business: ' + (value('f-biz') || '-'),
      'Product line: ' + value('f-line'),
      'Quantity: ' + (value('f-qty') || '-'),
      'Details: ' + value('f-msg')
    ];
    window.open(whatsapp(lines.join('\n')), '_blank', 'noopener,noreferrer');
  });
}

const list = document.getElementById('goods');
if (list) {
  const search = document.getElementById('search');
  const group = document.getElementById('group');
  const count = document.getElementById('count');
  [...new Set(GOODS.map(g => g.c))].forEach(c => group.add(new Option(c, c)));
  const render = () => {
    const q = search.value.trim().toLowerCase();
    const found = GOODS.filter(g => (!group.value || g.c === group.value) && (g.n + ' ' + g.c).toLowerCase().includes(q));
    list.replaceChildren(...found.map(g => {
      const li = document.createElement('li');
      const name = document.createElement('strong');
      const cat = document.createElement('span');
      const ask = document.createElement('a');
      name.textContent = g.n;
      cat.textContent = g.c;
      ask.textContent = 'Ask price';
      ask.setAttribute('aria-label', 'Ask the price of ' + g.n);
      ask.href = whatsapp('Namaste Dharamraj Cartel, please share price, stock and delivery for: ' + g.n);
      ask.target = '_blank';
      ask.rel = 'noopener noreferrer';
      li.append(name, cat, ask);
      return li;
    }));
    count.textContent = found.length ? found.length + ' products' : 'No products match. Try another word or group.';
  };
  search.addEventListener('input', render);
  group.addEventListener('change', render);
  render();
}
