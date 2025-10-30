const state = { items: [], cart: {} };
async function loadMenu(){
  const res = await fetch("/api/menu");
  state.items = await res.json();
  renderMenu(); renderCart();
}
function renderMenu(){
  const root=document.getElementById("menu-list"); root.innerHTML="";
  state.items.forEach(it=>{
    const card=document.createElement("div"); card.className="card";
    card.innerHTML=`<img src="${it.image_url}" alt="${it.name}">
    <h4>${it.name}</h4><p>${it.description}</p>
    <button class="add" data-id="${it.id}">Add</button>`;
    root.appendChild(card);
  });
  root.querySelectorAll(".add").forEach(btn=>btn.addEventListener("click",()=>{
    const id=btn.dataset.id; state.cart[id]=(state.cart[id]||0)+1; renderCart();
  }));
}
function renderCart(){
  const ul=document.getElementById("cart-items"); ul.innerHTML="";
  let total=0;
  for(const [id,qty] of Object.entries(state.cart)){
    const item=state.items.find(i=>i.id==id);
    total+=item.price_cents*qty;
    const li=document.createElement("li");
    li.innerText=`${item.name} x ${qty} - $${(item.price_cents*qty/100).toFixed(2)}`;
    ul.appendChild(li);
  }
  document.getElementById("cart-total").textContent=`$${(total/100).toFixed(2)}`;
}
async function checkout(){
  const items=Object.entries(state.cart).map(([id,qty])=>({id,quantity:qty}));
  const res=await fetch("/create-checkout-session",{
    method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({items})
  });
  const data=await res.json();
  window.location.href=data.checkout_url;
}
document.getElementById("checkout").addEventListener("click",checkout);
document.getElementById("checkout-bottom").addEventListener("click",checkout);
loadMenu();
