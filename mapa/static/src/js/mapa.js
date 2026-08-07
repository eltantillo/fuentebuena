const regions = {
  norte: [
    "MXBCN","MXBCS","MXSON","MXCHH","MXCOA","MXNLE","MXDUR","MXZAC","MXSIN","MXNAY","MXJAL","MXCOL","MXGUA","MXAGU"
  ],
  centro: [
    "MXTAM","MXSLP","MXQUE","MXHID","MXMEX","MXMOR","MXMIC","MXPUE","MXTLA","MXVER","MXGRO","MXCMX"
  ],
  sur: [
    "MXOAX","MXCHP","MXVER","MXTAB","MXCAM","MXYUC","MXROO"
  ],
};


function normalizeId(s){
  return s.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_\-]/g,'');
}

function initMap(){
  var svg = document.getElementById('svgRoot');
  if(!svg){
    svg = document.querySelector('svg');
    if(svg) svg.id = 'svgRoot';
  }
  if(!svg) return;
  var stateEls = Array.from(svg.querySelectorAll('[id]')).filter(function(el){ return el.id && el.id.trim().length>0; });

  stateEls.forEach(function(el){
    el.classList.add('state');
    el.addEventListener('mousemove', function(e){
      var tip = document.getElementById('tooltip');
      tip.style.display = 'block';
      tip.style.left = (e.pageX + 12) + 'px';
      tip.style.top = (e.pageY + 12) + 'px';
      tip.innerText = el.getAttribute('data-name') || el.id.replace(/_/g,' ').replace(/\b\w/g,function(c){return c.toUpperCase();});
    });
    el.addEventListener('mouseleave', function(){
      var tip = document.getElementById('tooltip');
      tip.style.display = 'none';
    });
    el.addEventListener('click', function(){
      el.classList.toggle('highlight');
    });
  });

  document.querySelectorAll('.btn').forEach(function(btn){
  btn.addEventListener('click', function(){
    document.querySelectorAll('.btn').forEach(function(b){ b.classList.remove('active'); });
    btn.classList.add('active');

    var region = btn.dataset.region;
    var color = btn.dataset.color || "#ffd54f"; 

    highlightRegion(region, stateEls, color);
  });
  });
  var defaultBtn = document.querySelector('.btn[data-region="all"]');
  if(defaultBtn) defaultBtn.classList.add('active');
}

function highlightRegion(region, stateEls, color){
  stateEls.forEach(function(s){ 
    s.classList.remove('highlight'); 
    s.classList.remove('dim'); 
  });
  
  if(region === 'all') return;
  
  var list = regions[region] || [];
  stateEls.forEach(function(s){
    var stateId = s.id.toUpperCase();
    var isInRegion = list.some(function(regionId){
      return stateId === regionId.toUpperCase();
    });
    
    if(isInRegion){
      s.classList.add('highlight');
      s.style.setProperty('--current-color', color);  
    }
  });
}

document.addEventListener('DOMContentLoaded', function(){
  initMap();
});
