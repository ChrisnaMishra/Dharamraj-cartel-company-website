/* Accessible hero slider: auto-rotates, with manual controls and reduced-motion support */
(function(){
 const slides=[
  {kicker:'Retail · Wholesale · Global sourcing',one:'Trade Beyond',two:'Borders',sub:'Premium sourcing from India & China for businesses — and a curated store of pooja samagri, electronics & lifestyle goods for everyone.'},
  {kicker:'Sourcing from India & China',one:'Global Products',two:'Closer to Home',sub:'Discover products, compare requirements and build reliable supply for homes, retailers and businesses across Nepal.'},
  {kicker:'Built for retailers and growing businesses',one:'Source Smart.',two:'Grow Together.',sub:'From product enquiries to bulk sourcing and dealer partnerships, Dharamraj Cartel connects demand with dependable supply.'}
 ];
 const backgrounds=[...document.querySelectorAll('.slider-bg')],dots=[...document.querySelectorAll('.slider-dots button')];
 const kicker=document.getElementById('slide-kicker'),one=document.getElementById('slide-line-one'),two=document.getElementById('slide-line-two'),sub=document.querySelector('.hero .sub');
 const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;let index=0,timer;
 function show(n){index=(n+slides.length)%slides.length;const s=slides[index];kicker.textContent=s.kicker;one.textContent=s.one;two.innerHTML=s.two+'<span class="gold">.</span>';sub.innerHTML=s.sub.replace('India & China','<b>India &amp; China</b>').replace('pooja samagri, electronics & lifestyle goods','<b>pooja samagri, electronics &amp; lifestyle goods</b>');backgrounds.forEach((el,i)=>el.classList.toggle('active',i===index));dots.forEach((el,i)=>el.classList.toggle('active',i===index));}
 function restart(){clearInterval(timer);if(!reduce)timer=setInterval(()=>show(index+1),6000)}
 document.querySelector('.slider-prev')?.addEventListener('click',()=>{show(index-1);restart()});
 document.querySelector('.slider-next')?.addEventListener('click',()=>{show(index+1);restart()});
 dots.forEach((d,i)=>d.addEventListener('click',()=>{show(i);restart()}));
 show(0);restart();
})();

/* ---------- End of original hero slider; main site logic follows ---------- */

const hasGsap=typeof window.gsap!=='undefined';
const hasScrollTrigger=typeof window.ScrollTrigger!=='undefined';
if(hasGsap && hasScrollTrigger) gsap.registerPlugin(ScrollTrigger);

/* ---------- PRELOADER ---------- */
(function(){
  const bar=document.getElementById('loadbar'), pct=document.getElementById('loadpct'), loader=document.getElementById('loader');
  let p=0;
  const tick=setInterval(()=>{
    p=Math.min(100,p+Math.random()*16);
    bar.style.width=p+'%';
    pct.textContent=String(Math.floor(p)).padStart(2,'0');
    if(p>=100){
      clearInterval(tick);
      if(hasGsap){
        gsap.to(loader,{opacity:0,duration:.7,delay:.25,onComplete:()=>{loader.style.display='none';heroIn();}});
      }else{
        loader.style.display='none';
        heroIn();
      }
    }
  },90);
})();

function heroIn(){
  const heroItems=document.querySelectorAll('.hero .rv');
  if(hasGsap){
    gsap.to(heroItems,{opacity:1,y:0,duration:1.1,stagger:.12,ease:'power3.out'});
  }else{
    heroItems.forEach(el=>{el.style.opacity='1';el.style.transform='none';});
  }
}

/* ---------- GATEWAY glow follows mouse ---------- */
document.querySelectorAll('.gate').forEach(g=>{
  g.addEventListener('mousemove',e=>{
    const r=g.getBoundingClientRect();
    g.style.setProperty('--mx',(e.clientX-r.left)+'px');
    g.style.setProperty('--my',(e.clientY-r.top)+'px');
  });
});

/* ---------- NAV scroll state ---------- */
const siteYear=document.getElementById('siteYear');
if(siteYear) siteYear.textContent=String(new Date().getFullYear());
const nav=document.getElementById('nav');
if(nav) window.addEventListener('scroll',()=>nav.classList.toggle('scrolled',window.scrollY>40));

/* ---------- MOBILE NAV ---------- */
const navLinks=document.getElementById('primary-navigation');
const menuToggle=document.getElementById('menuToggle');
function closeMobileNav(){
  navLinks.classList.remove('is-open');
  menuToggle.setAttribute('aria-expanded','false');
  menuToggle.setAttribute('aria-label','Open navigation');
  menuToggle.textContent='☰';
}
if(menuToggle && navLinks) menuToggle.addEventListener('click',()=>{
  const isOpen=!navLinks.classList.contains('is-open');
  navLinks.classList.toggle('is-open',isOpen);
  menuToggle.setAttribute('aria-expanded',String(isOpen));
  menuToggle.setAttribute('aria-label',isOpen?'Close navigation':'Open navigation');
  menuToggle.textContent=isOpen?'×':'☰';
});
if(navLinks) navLinks.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>{
  if(window.matchMedia('(max-width: 900px)').matches) closeMobileNav();
}));
document.addEventListener('keydown',event=>{if(event.key==='Escape') closeMobileNav();});

/* ---------- SCROLL REVEALS ---------- */
const revealItems=document.querySelectorAll('section .rv, .dealer-band, footer .rv');
if(hasGsap && hasScrollTrigger){
  revealItems.forEach(el=>{
    gsap.to(el,{opacity:1,y:0,duration:1,ease:'power3.out',
      scrollTrigger:{trigger:el,start:'top 85%'}});
  });
}else{
  revealItems.forEach(el=>{el.style.opacity='1';el.style.transform='none';});
}

/* ---------- MARQUEE duplicate for seamless loop ---------- */
const t=document.getElementById('mqtrack');if(t && !t.dataset.duplicated){t.innerHTML+=t.innerHTML;t.dataset.duplicated='true';}

/* ---------- STORE: graceful photo fallback ---------- */
document.querySelectorAll('.cat-photo img').forEach(image=>{
  image.addEventListener('error',()=>{
    const fallback=document.createElement('div');
    fallback.className='store-photo-fallback';
    fallback.textContent='DHARAMRAJ CARTEL';
    image.replaceWith(fallback);
  },{once:true});
});

/* ---------- STORE: Home & Kitchen expands its catalogue in place ---------- */
const kitchenwareToggle=document.querySelector('[data-kitchenware-toggle]');
const kitchenwarePanel=document.getElementById('kitchenware');
const kitchenwareClose=document.getElementById('kitchenware-close');
let kitchenProductCards=[...document.querySelectorAll('.kw-product-card')];
const kitchenFilters=[...document.querySelectorAll('.kw-filter')];
const kitchenEmpty=document.querySelector('.kw-product-empty');
const kitchenCount=document.querySelector('.kw-count');

function filterKitchenProducts(category){
  let shown=0;
  kitchenProductCards=[...document.querySelectorAll('.kw-product-card')];
  kitchenProductCards.forEach(card=>{
    const visible=category==='All products'||card.dataset.category===category;
    card.hidden=!visible;
    if(visible) shown+=1;
  });
  kitchenFilters.forEach(button=>{
    button.setAttribute('aria-pressed',String(button.dataset.filter===category));
  });
  if(kitchenEmpty) kitchenEmpty.style.display=shown===0?'block':'none';
  if(kitchenCount) kitchenCount.textContent=shown+' product line'+(shown===1?'':'s');
}

function setKitchenwareOpen(open,scrollIntoView=true){
  if(!kitchenwarePanel||!kitchenwareToggle) return;
  kitchenwarePanel.classList.toggle('is-expanded',open);
  kitchenwareToggle.setAttribute('aria-expanded',String(open));
  const cta=kitchenwareToggle.querySelector('.go');
  if(cta) cta.innerHTML=open?'Close catalogue <s>↑</s>':'Explore kitchenware <s>↓</s>';
  if(open){
    filterKitchenProducts('All products');
    if(scrollIntoView) kitchenwarePanel.scrollIntoView({behavior:'smooth',block:'start'});
  }else if(scrollIntoView){
    kitchenwareToggle.scrollIntoView({behavior:'smooth',block:'center'});
  }
}

if(kitchenwareToggle){
  kitchenwareToggle.addEventListener('click',event=>{
    event.preventDefault();
    const select=document.getElementById('q-cat');
    if(select) select.value='Kitchenware & Dining';
    setKitchenwareOpen(!kitchenwarePanel.classList.contains('is-expanded'));
  });
}
if(kitchenwareClose){
  kitchenwareClose.addEventListener('click',()=>setKitchenwareOpen(false));
}

kitchenFilters.forEach(button=>{
  button.addEventListener('click',()=>filterKitchenProducts(button.dataset.filter));
});
if(kitchenFilters.length) filterKitchenProducts(kitchenFilters.find(button=>button.dataset.filter==='All products')?.dataset.filter || 'All products');

document.querySelectorAll('.kw-card[data-category]').forEach(card=>{
  card.addEventListener('click',()=>{
    filterKitchenProducts(card.dataset.category);
  });
});

document.querySelectorAll('.cat[data-category]:not([data-kitchenware-toggle])').forEach(card=>{
  card.addEventListener('click',()=>{
    const select=document.getElementById('q-cat');
    if(select) select.value=card.dataset.category;
  });
});

const kitchenProductGrid=document.querySelector('.kw-product-grid');
if(kitchenProductGrid){
  kitchenProductGrid.addEventListener('click',event=>{
    const card=event.target.closest('.kw-product-card[data-category]');
    if(!card) return;
    const select=document.getElementById('q-cat');
    const details=document.getElementById('q-msg');
    if(select) select.value=card.dataset.category;
    if(details) details.value='I am enquiring about '+card.dataset.product+'. Please share current availability, specifications, minimum order quantity and price.';
  });
}

/* Load the real locally hosted product photos generated from Indigo's catalogue.
   The old cards are only a temporary fallback while the first photo sync runs. */
function localCatalogueAsset(relativePath){
  const path=String(relativePath||'').split('/').map(part=>encodeURIComponent(part)).join('/');
  return new URL('/Dharamraj-cartel-company-website/indigo_images/'+path,window.location.origin).href;
}

function setPhoto(img, primaryPath, fallbackPath, altText, remoteFallback){
  img.src=localCatalogueAsset(primaryPath||fallbackPath||'categories/household-range.webp');
  img.alt=altText;
  img.loading='lazy';
  img.decoding='async';
  img.addEventListener('error',()=>{
    if(fallbackPath && img.dataset.usedFallback!=='1'){
      img.dataset.usedFallback='1';
      img.src=localCatalogueAsset(fallbackPath);
    }else if(remoteFallback && img.dataset.usedRemoteFallback!=='1'){
      img.dataset.usedRemoteFallback='1';
      img.src=remoteFallback;
    }else{
      const placeholder=document.createElement('div');
      placeholder.className='kw-photo-fallback';
      placeholder.textContent='Product photo unavailable';
      img.replaceWith(placeholder);
    }
  },{once:false});
}

async function loadRealKitchenwarePhotos(){
  const grid=document.querySelector('.kw-product-grid');
  if(!grid) return;
  try{
    let response;
    const manifestUrls=[
      new URL('./indigo_images/products.json',window.location.href).href,
      new URL('/Dharamraj-cartel-company-website/indigo_images/products.json',window.location.origin).href
    ];
    let lastError;
    for(const manifestUrl of [...new Set(manifestUrls)]){
      try{
        const candidate=await fetch(manifestUrl,{cache:'no-cache'});
        if(candidate.ok){response=candidate;break;}
        lastError=new Error('Catalogue manifest returned HTTP '+candidate.status);
      }catch(error){lastError=error;}
    }
    if(!response) throw lastError||new Error('Catalogue manifest could not be loaded.');
    const manifest=await response.json();
    const groups=Array.isArray(manifest.categories)?manifest.categories:[];
    const byName=new Map(groups.map(group=>[group.name,group]));
    const allProducts=groups.flatMap(group=>(group.products||[]).map(product=>({
      ...product,
      category:group.name,
      categorySlug:group.slug
    })));
    const photoCount=allProducts.reduce((total,product)=>total+(Array.isArray(product.images)&&product.images.length?1:0),0);
    if(!allProducts.length||photoCount===0) throw new Error('No product photographs were found in the manifest yet.');

    const firstPhotoByCategory=new Map();
    const firstRemotePhotoByCategory=new Map();
    for(const group of groups){
      const firstProduct=(group.products||[]).find(product=>Array.isArray(product.images)&&product.images.length);
      if(firstProduct) firstPhotoByCategory.set(group.name,firstProduct.images[0]);
      const remoteProduct=(group.products||[]).find(product=>Array.isArray(product.image_urls)&&product.image_urls.length);
      if(remoteProduct) firstRemotePhotoByCategory.set(group.name,remoteProduct.image_urls[0]);
    }
    const overallProduct=allProducts.find(product=>Array.isArray(product.images)&&product.images.length);
    const overallPhoto=overallProduct?.images[0]||'categories/household-range.webp';
    const overallRemotePhoto=allProducts.find(product=>Array.isArray(product.image_urls)&&product.image_urls.length)?.image_urls[0];

    /* Replace every category illustration with a real product photo. */
    document.querySelectorAll('.kw-card[data-category]').forEach(card=>{
      const group=byName.get(card.dataset.category);
      const categoryPhoto=firstPhotoByCategory.get(card.dataset.category)||overallPhoto;
      const imagePath=group&&group.slug?('categories/'+group.slug+'.webp'):overallPhoto;
      const existing=card.querySelector('.kw-placeholder');
      if(existing){
        const img=document.createElement('img');
        img.className='kw-art';
        setPhoto(img,imagePath,categoryPhoto,card.dataset.category+' product photo',firstRemotePhotoByCategory.get(card.dataset.category)||overallRemotePhoto);
        existing.replaceWith(img);
      }
    });

    /* Replace the Home & Kitchen tile photo with a local catalogue collage. */
    const homePhoto=document.querySelector('[data-kitchenware-toggle] .cat-photo img');
    if(homePhoto) setPhoto(homePhoto,'categories/household-range.webp',overallPhoto,'Kitchenware and household product photos',overallRemotePhoto);

    /* Render every supplier product with its actual local image when available. */
    const fragment=document.createDocumentFragment();
    for(const product of allProducts){
      const productName=product.name||'Household product';
      const category=product.category||'Kitchen Tools';
      const categoryPhoto=firstPhotoByCategory.get(category)||overallPhoto;
      const imagePath=Array.isArray(product.images)&&product.images.length?product.images[0]:categoryPhoto;
      const card=document.createElement('a');
      card.className='kw-product-card';
      card.href=product.url||'#enquiry';
      if(product.url){card.target='_blank';card.rel='noopener noreferrer';}
      card.dataset.category=category;
      card.dataset.product=productName;
      if(product.url) card.dataset.productUrl=product.url;

      const artwork=document.createElement('div');
      artwork.className='kw-product-art';
      const image=document.createElement('img');
      image.className='kw-product-photo';
      setPhoto(image,imagePath,categoryPhoto,productName,Array.isArray(product.image_urls)?product.image_urls[0]:overallRemotePhoto);
      artwork.append(image);

      const copy=document.createElement('div');
      copy.className='kw-product-copy';
      const categoryLabel=document.createElement('span');
      categoryLabel.className='kw-product-cat';
      categoryLabel.textContent=category;
      const title=document.createElement('h5');
      title.textContent=productName;
      const description=document.createElement('p');
      description.textContent='Ask us for the available model, specification, quantity and Nepal delivery price.';
      const callToAction=document.createElement('span');
      callToAction.className='kw-product-cta';
      const callText=document.createElement('span');
      callText.textContent=product.url?'View product details':'Enquire for details';
      const arrow=document.createElement('span');
      arrow.setAttribute('aria-hidden','true');
      arrow.textContent='↗';
      callToAction.append(callText,arrow);
      copy.append(categoryLabel,title,description,callToAction);
      card.append(artwork,copy);
      fragment.append(card);
    }
    grid.replaceChildren(fragment);
    kitchenProductCards=[...document.querySelectorAll('.kw-product-card')];
    filterKitchenProducts('All products');
  }catch(error){
    /* Keep the page usable during the first sync or if the supplier is unavailable. */
    console.warn('Kitchenware product photos have not finished loading:',error);
  }
}
loadRealKitchenwarePhotos();

/* Open the catalogue for direct product links and bookmarks. */
if(window.location.hash==='#kw-products'||window.location.hash==='#kitchenware'){
  setKitchenwareOpen(true,false);
}

/* ---------- ENQUIRY: open WhatsApp with a pre-filled message ---------- */
const enquiryForm=document.getElementById('enqForm');
if(enquiryForm) enquiryForm.addEventListener('submit',e=>{
  e.preventDefault();
  const v=id=>document.getElementById(id).value.trim();
  const lines=[
    'NEW SOURCING ENQUIRY — DHARAMRAJ CARTEL WEBSITE',
    '----------------------------',
    'Name: '+v('q-name'),
    'Business: '+(v('q-biz')||'-'),
    'Category: '+v('q-cat'),
    'Source country: '+v('q-origin'),
    'Quantity / MOQ: '+(v('q-qty')||'-'),
    'Delivery destination: '+(v('q-dest')||'-'),
    'Product details: '+v('q-msg')
  ];
  const url='https://wa.me/9779845656595?text='+encodeURIComponent(lines.join('\n'));
  window.open(url,'_blank','noopener,noreferrer');
});

/* Open full product information inside Dharamraj Cartel (same tab). */
(function setupKitchenwareDetails(){
  const modal=document.getElementById('kw-detail-modal');
  const content=document.getElementById('kw-detail-content');
  const closeButton=document.getElementById('kw-detail-close');
  const grid=document.querySelector('.kw-product-grid');
  if(!modal||!content||!grid) return;
  let detailCache=null;
  const esc=value=>String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const whatsappUrl=name=>'https://wa.me/9779845656595?text='+encodeURIComponent('Namaste Dharamraj Cartel, I am interested in '+name+'. Please share availability, specifications and Nepal delivery price.');
  function close(){modal.classList.remove('is-open');modal.setAttribute('aria-hidden','true');document.body.style.overflow='';}
  closeButton.addEventListener('click',close);
  modal.addEventListener('click',event=>{if(event.target===modal)close();});
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&modal.classList.contains('is-open'))close();});
  async function getDetails(){
    if(detailCache) return detailCache;
    const urls=[new URL('./indigo_images/product-details.json',window.location.href).href,new URL('/Dharamraj-cartel-company-website/indigo_images/product-details.json',window.location.origin).href];
    for(const url of [...new Set(urls)]){try{const response=await fetch(url,{cache:'no-cache'});if(response.ok){detailCache=await response.json();return detailCache;}}catch(e){}}
    throw new Error('Product details are still being prepared.');
  }
  function render(detail,card){
    const name=detail.name||card.dataset.product||'Kitchenware product';
    /* Prefer the image already served by Dharamraj Cartel; supplier-hosted gallery photos follow. */
    const cardImage=card.querySelector('.kw-product-photo')?.getAttribute('src')||'';
    const images=[cardImage,detail.local_image,...(detail.image_urls||[])];
    const uniqueImages=[...new Set(images)].filter(Boolean);
    const firstImage=uniqueImages[0]||'';
    const specs=Array.isArray(detail.specifications)?detail.specifications:[];
    const features=Array.isArray(detail.features)?detail.features:[];
    const specHtml=specs.length?'<div class="kw-detail-section"><h4>Item codes & specifications</h4><table class="kw-detail-specs"><tbody>'+specs.map(row=>'<tr>'+row.map((cell,index)=>index===0?'<th>'+esc(cell)+'</th>':'<td>'+esc(cell)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>':'';
    const featureHtml=features.length?'<div class="kw-detail-section"><h4>Key features</h4><ul class="kw-detail-features">'+features.map(item=>'<li>'+esc(item)+'</li>').join('')+'</ul></div>':'';
    content.className='';
    content.innerHTML='<div class="kw-detail-layout"><div><img class="kw-detail-image" id="kw-detail-main-image" src="'+esc(firstImage)+'" alt="'+esc(name)+'" '+(firstImage?'':'hidden')+'><div class="kw-detail-thumbs">'+uniqueImages.slice(0,8).map(url=>'<button type="button" class="kw-detail-thumb-button" data-image="'+esc(url)+'" style="padding:0;border:0;background:transparent"><img class="kw-detail-thumb" src="'+esc(url)+'" alt="More photos of '+esc(name)+'" loading="lazy"></button>').join('')+'</div></div><div><div class="kw-detail-kicker">'+esc(detail.category||card.dataset.category||'Kitchenware')+'</div><h2 class="kw-detail-title" id="kw-detail-title">'+esc(name)+'</h2><p class="kw-detail-description">'+esc(detail.description||'Product description has not been published by the supplier.')+'</p>'+specHtml+featureHtml+'<a class="kw-detail-enquire" href="'+whatsappUrl(name)+'" target="_blank" rel="noopener noreferrer">Enquire on WhatsApp ↗</a><p class="kw-note">Availability, final specifications and Nepal delivery price are confirmed on enquiry.</p></div></div>';
    content.querySelectorAll('[data-image]').forEach(button=>button.addEventListener('click',()=>{const img=content.querySelector('#kw-detail-main-image');if(img)img.src=button.dataset.image;}));
  }
  grid.addEventListener('click',async event=>{
    const card=event.target.closest('.kw-product-card');
    if(!card) return;
    event.preventDefault();
    modal.classList.add('is-open');modal.setAttribute('aria-hidden','false');document.body.style.overflow='hidden';
    content.className='kw-detail-loading';content.textContent='Loading full product details…';
    try{const all=await getDetails();const detail=all[card.dataset.productUrl]||all.products?.[card.dataset.productUrl];if(!detail)throw new Error('Detailed information for this item is not available yet.');render(detail,card);}
    catch(error){content.className='kw-detail-loading';content.textContent=(error&&error.message)||'Could not load product details. Please try again shortly.';}
  });
})();
