'use strict';
document.querySelectorAll('[data-install-select]').forEach(select=>select.addEventListener('change',()=>{
 const id=select.dataset.installSelect,source=document.getElementById(id+'-'+select.value)||document.getElementById(id+'-auto');
 document.getElementById(id).textContent=source.textContent;
 const button=document.querySelector('[data-copy="'+id+'"]');
 if(button?.nextElementSibling)button.nextElementSibling.textContent='';
}));
document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',async()=>{
 const text=document.getElementById(button.dataset.copy).textContent,status=button.nextElementSibling;
 try{await navigator.clipboard.writeText(text);status.textContent='已复制，可粘贴到对话中。'}catch{status.textContent='请选中上方文字后复制。'}
}));
