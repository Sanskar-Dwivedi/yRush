// yRush shared utilities & demo data
(function(){
  const STORE = {
    CART_KEY: 'yrush_cart',
    ORDERS_KEY: 'yrush_orders',
    USERS_KEY: 'yrush_users',
    CURRENT_USER: 'currentUser'
  };

  // Demo catalog (use existing global CATALOG if defined elsewhere)
  const DEFAULT_CATALOG = [
    {id:'DRAW-SHEET-001', name:'Drawing Sheet A3', price:12, category:'Drawing', details:'Standard A3 sheet for engineering drawing', image:'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?q=80&w=800'},
    {id:'GEOMETRY-SET-001', name:'Geometry Set', price:95, category:'Geometry', details:'Compass, divider, protractor and set squares', image:'https://images.unsplash.com/photo-1613141411244-0e4ac2598d8a?q=80&w=800'},
    {id:'CALCULATOR-001', name:'Scientific Calculator', price:799, category:'Digital', details:'Non-programmable scientific calculator', image:'https://images.unsplash.com/photo-1596495578065-8ae9a50cf0f2?q=80&w=800'},
    {id:'COMPASS-001', name:'Compass (Metal)', price:65, category:'Practical', details:'Precise metal compass for labs', image:'https://images.unsplash.com/photo-1515616889791-8b2b5b8f74ce?q=80&w=800'},
  ];

  window.CATALOG = Array.isArray(window.CATALOG) && window.CATALOG.length ? window.CATALOG : DEFAULT_CATALOG;

  // Small helpers
  const fmt = new Intl.NumberFormat('en-IN', {style:'currency',currency:'INR'});
  function money(n){ return fmt.format(Number(n||0)); }
  function readJSON(k, fallback){ try{ return JSON.parse(localStorage.getItem(k)) ?? fallback; }catch{ return fallback; } }
  function writeJSON(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){ console.warn('storage', e); } }

  // Hash (SHA-256) for demo auth
  async function sha256(str){
    const data = new TextEncoder().encode(str);
    const digest = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(digest)).map(b=>b.toString(16).padStart(2,'0')).join('');
  }

  // Demo users seeding
  async function seedUsers(){
    const users = readJSON(STORE.USERS_KEY, []);
    if(users.length) return;
    const pass = await sha256('admin123');
    const pass2 = await sha256('student123');
    const seed = [
      {email:'owner@yrush.local', name:'YRush Owner', type:'owner', course:'NA', passHash:pass},
      {email:'student@yrush.local', name:'YRush Student', type:'student', course:'CSE', passHash:pass2},
    ];
    writeJSON(STORE.USERS_KEY, seed);
  }
  seedUsers();

  // Auth
  function getCurrentUser(){
    try{ return JSON.parse(sessionStorage.getItem(STORE.CURRENT_USER)||'{}'); }catch{ return {}; }
  }
  function setCurrentUser(u){
    // never store password
    sessionStorage.setItem(STORE.CURRENT_USER, JSON.stringify({email:u.email, name:u.name, type:u.type, course:u.course}));
  }
  function signOut(){ sessionStorage.removeItem(STORE.CURRENT_USER); }

  function requireAuth(){
    const u = getCurrentUser();
    if(!u || !u.email){ location.href = 'login.html'; }
    return u;
  }

  // Cart
  function getCart(){ return readJSON(STORE.CART_KEY, {}); }
  function saveCart(c){ writeJSON(STORE.CART_KEY, c); }
  function addToCart(id, qty){
    const c = getCart(); c[id] = Math.max(1, (c[id]||0) + (qty||1)); saveCart(c);
  }
  function setQty(id, qty){
    const c = getCart();
    if(qty<=0) delete c[id]; else c[id]=qty;
    saveCart(c);
  }
  function clearCart(){ saveCart({}); }
  function cartLinesArray(cart){
    const list = [];
    for(const [id,qty] of Object.entries(cart)){
      const p = window.CATALOG.find(x=>x.id===id);
      if(p) list.push({id, qty, price:p.price, name:p.name});
    }
    return list;
  }
  function cartTotals(){
    const lines = cartLinesArray(getCart());
    const subtotal = lines.reduce((s,l)=> s + l.price*l.qty, 0);
    const total = subtotal;
    return {subtotal, total, lines};
  }

  // Orders
  function getOrders(){ return readJSON(STORE.ORDERS_KEY, []); }
  function saveOrders(list){ writeJSON(STORE.ORDERS_KEY, list); }
  function token6(){ return Math.floor(100000 + Math.random()*900000).toString(); }

  // Toast
  function toast(msg){
    const t = document.createElement('div');
    t.className='toast'; t.textContent=msg; document.body.appendChild(t);
    setTimeout(()=>t.remove(), 1800);
  }

  // Expose API
  window.yRush = {
    STORE, money, getCart, saveCart, addToCart, setQty, clearCart, cartLinesArray, cartTotals,
    getOrders, saveOrders, token6, toast,
    getCurrentUser, setCurrentUser, signOut, requireAuth,
    sha256
  };
})();