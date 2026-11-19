(() => {
 const steps=[
  ['studio','.intro','A colour helper for your poster','Your poster may have lots of colours. OVERPRINT suggests a set of printing inks and lets you compare how the poster would look. You choose whether the result is good enough.','The application combines an approximate ink-selection method with colour-error selection and a priority queue.'],
  ['studio','#palette-editor','1. Choose your colours','Click any colour to change it. You can also try a ready-made example. This version applies your colours to the sample poster.','A hash set combines repeated colours, so duplicates do not count twice.'],
  ['studio','#tolerance','2. Choose how much change is okay','Move left to keep colours closer to the originals. Move right to allow bigger changes, which may let more colours share the same ink. Then click Find my ink plan.','Colour differences are measured in CIELAB. A matrix records which ink-to-colour pairs are within your chosen limit.'],
  ['studio','#chosen-inks','3. See the suggested inks','These are the inks in the suggested plan. Switch between Before and After to judge the result for yourself. The example goes from eight colours to four inks.','Weighted greedy set cover chooses the ink with the lowest setup cost per newly matched colour at each step. It is an approximation, not a guarantee of the cheapest possible plan.'],
  ['studio','#review-colors','4. Check what changed most','Start with these colours. They changed more than the others, so they are the ones most worth checking. If you dislike the changes, move the slider left and try again.','Quickselect or Median of Medians identifies the colours to review. A binary max-heap puts the largest change first. The choice between selection methods is under Advanced options.'],
  ['studio','#export-svg','5. Save the result you like','Save the example poster, or save the colours and settings so you can reopen them later. Always check a real test print before printing the full job.','SVG export requires every colour to have an acceptable match and the plan to fit your maximum ink count. JSON preserves inputs and result data.']
 ];
 const $=s=>document.querySelector(s),dialog=$('#tour-dialog');let index=0,previous=null;const technical=document.createElement('details');technical.id='tour-technical';technical.innerHTML='<summary>How the computer does this</summary><p id="tour-technical-copy"></p>';$('#tour-copy').after(technical);
 function clear(){document.querySelectorAll('.tour-highlight').forEach(x=>x.classList.remove('tour-highlight'));}
 function show(){clear();const [view,selector,title,copy,technical]=steps[index];document.querySelector(`.nav[data-view="${view}"]`).click();const target=$(selector);target.classList.add('tour-highlight');target.scrollIntoView({behavior:'instant',block:'center'});$('#tour-step').textContent=`PRODUCT WALKTHROUGH / ${index+1} OF ${steps.length}`;$('#tour-title').textContent=title;$('#tour-copy').textContent=copy;$('#tour-technical-copy').textContent=technical;$('#tour-technical').open=false;$('#tour-prev').disabled=index===0;$('#tour-next').textContent=index===steps.length-1?'Finish tour ✓':'Next →';}
 $('#start-tour').addEventListener('click',()=>{previous=document.activeElement;index=0;show();dialog.showModal();});
 $('#tour-next').addEventListener('click',()=>{if(index===steps.length-1)dialog.close();else{index++;show();}});
 $('#tour-prev').addEventListener('click',()=>{if(index>0){index--;show();}});
 $('#tour-close').addEventListener('click',()=>dialog.close());dialog.addEventListener('close',()=>{clear();previous?.focus();});
 const film=$('#film-dialog'),video=$('#promo-video');video.volume=0.4;
 $('#watch-film').addEventListener('click',()=>{film.showModal();video.play().catch(()=>{});});
 $('#film-close').addEventListener('click',()=>film.close());film.addEventListener('close',()=>video.pause());
})();
