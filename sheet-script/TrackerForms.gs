/**
 * Maystone – customer details form + live-site enquiries (part of the standalone tracker web app).
 * Paste below Tracker.gs in the "Maystone view tracker" project. doGet/doPost in Tracker.gs route here.
 *
 * Details form:  <web app URL>?form=<LeadID>&k=<key>   (key is stored in the sheet's "Form key" column)
 *   Saves photos + answers to Drive: "Maystone client uploads/<LeadID>/". The sheet script picks them
 *   up within 5 minutes and publishes them to the customer's site.
 * Enquiries:     live sites POST action=enquiry&id=<LeadID>&name=... -> emailed to the business owner.
 */

var COL = { email: 11, details: 30, domain: 31, live: 32, key: 33 }; // K, AD, AE, AF, AG
var UPLOAD_ROOT = 'Maystone client uploads';

function routeGet_(e) {
  var p = (e && e.parameter) || {};
  if (p.form) return detailsForm_(String(p.form), String(p.k || ''));
  return null;
}

function doPost(e) {
  var p = (e && e.parameter) || {};
  if (p.action === 'enquiry') { try { enquiry_(p); } catch (err) { console.error(err); } }
  return ContentService.createTextOutput('ok');
}

// ---------- details form ----------

function checkKey_(id, k) {
  id = String(id).replace(/[^A-Za-z0-9_-]/g, '');
  var hit = findLead_(id);
  if (!hit || !k) return null;
  var key = String(hit.sheet.getRange(hit.row, COL.key).getValue()).trim();
  return key && key === k ? hit : null;
}

function detailsForm_(id, k) {
  var hit = checkKey_(id, k);
  if (!hit) return HtmlService.createHtmlOutput('<p style="font:16px system-ui;padding:24px">This link has expired or is not valid. Reply to our email and we\'ll send a new one.</p>').setTitle('Maystone');
  var sh = hit.sheet, r = hit.row;
  var biz = String(sh.getRange(r, C.biz).getValue()), phone = String(sh.getRange(r, 5).getValue());
  var html = FORM_HTML_
    .replace(/{{ID}}/g, esc_(id)).replace(/{{K}}/g, esc_(k))
    .replace(/{{BIZ}}/g, esc_(biz)).replace(/{{PHONE}}/g, esc_(phone))
    .replace(/{{EMAIL}}/g, esc_(String(sh.getRange(r, COL.email).getValue())));
  return HtmlService.createHtmlOutput(html).setTitle('Your website details – ' + biz)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

/** Called from the form with google.script.run. photos: [{name, dataUrl}] already resized in the browser. */
function submitDetails(id, k, data, photos) {
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    var hit = checkKey_(id, k);
    if (!hit) throw new Error('This link is not valid any more.');
    var folder = leadFolder_(id);
    var saved = 0;
    (photos || []).slice(0, 13).forEach(function (ph) {
      var m = String(ph.dataUrl).match(/^data:(image\/(jpeg|png|webp));base64,(.+)$/);
      if (!m) return;
      var name = /^(logo|\d{1,2})$/.test(ph.name) ? ph.name : null;
      if (!name) return;
      var ext = m[2] === 'jpeg' ? 'jpg' : m[2];
      folder.getFilesByName(name + '.' + ext).hasNext() && folder.getFilesByName(name + '.' + ext).next().setTrashed(true);
      folder.createFile(Utilities.newBlob(Utilities.base64Decode(m[3]), m[1], name + '.' + ext));
      saved++;
    });
    var clean = {
      business: str_(data.business, 80), phone: str_(data.phone, 30), email: str_(data.email, 120),
      creds_list: [str_(data.reg, 160), str_(data.insurance, 160)],
      company: str_(data.company, 240), changes: str_(data.changes, 3000),
      domain_have: str_(data.domain_have, 120), domain_ideas: str_(data.domain_ideas, 200),
      submitted: new Date().toISOString()
    };
    var old = folder.getFilesByName('details.json');
    while (old.hasNext()) old.next().setTrashed(true);
    folder.createFile('details.json', JSON.stringify(clean, null, 1), 'application/json');

    var sh = hit.sheet, r = hit.row;
    sh.getRange(r, COL.details).setValue('Received ' + Utilities.formatDate(new Date(), 'Europe/London', 'dd/MM HH:mm') + ' – ' + saved + ' file(s)');
    if (clean.domain_have && !String(sh.getRange(r, COL.domain).getValue()).trim()) {
      sh.getRange(r, COL.domain).setValue(clean.domain_have.toLowerCase().replace(/^https?:\/\//, '').replace(/^www\./, '').replace(/\/.*$/, ''));
    }
    var biz = clean.business || sh.getRange(r, C.biz).getValue();
    notify_(sh.getName(), 'DETAILS IN: ' + biz + ' sent their photos and details',
      biz + ' (' + id + ') sent ' + saved + ' file(s).\n\n' +
      'Domain they have: ' + (clean.domain_have || '–') + '\nDomain ideas: ' + (clean.domain_ideas || '–') +
      '\n\nChanges they asked for:\n' + (clean.changes || '–') +
      '\n\nThe site updates with their photos and details within about 10 minutes. Wording changes above need doing by hand.' +
      '\nFiles: ' + folder.getUrl());
    return 'ok';
  } finally { lock.releaseLock(); }
}

function leadFolder_(id) {
  var roots = DriveApp.getFoldersByName(UPLOAD_ROOT);
  var root = roots.hasNext() ? roots.next() : DriveApp.createFolder(UPLOAD_ROOT);
  var f = root.getFoldersByName(id);
  return f.hasNext() ? f.next() : root.createFolder(id);
}

// ---------- enquiries from live sites ----------

function enquiry_(p) {
  if (p.website) return; // honeypot
  var id = String(p.id || '').replace(/[^A-Za-z0-9_-]/g, '');
  var cache = CacheService.getScriptCache(), ck = 'enq_' + id, n = Number(cache.get(ck) || 0);
  if (n >= 20) return; // flood guard: 20 an hour per site
  cache.put(ck, String(n + 1), 3600);
  var hit = findLead_(id);
  if (!hit) return;
  var sh = hit.sheet, r = hit.row;
  var to = '';
  var f = DriveApp.getFoldersByName(UPLOAD_ROOT);
  if (f.hasNext()) {
    var lf = f.next().getFoldersByName(id);
    if (lf.hasNext()) {
      var dj = lf.next().getFilesByName('details.json');
      if (dj.hasNext()) { try { to = JSON.parse(dj.next().getBlob().getDataAsString()).email || ''; } catch (e) {} }
    }
  }
  to = to || String(sh.getRange(r, COL.email).getValue()).trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(to)) return;
  var biz = sh.getRange(r, C.biz).getValue();
  var body = 'New enquiry from your website:\n\n' +
    'Name: ' + str_(p.name, 100) + '\nPhone: ' + str_(p.phone, 40) + '\nEmail: ' + str_(p.email, 120) +
    '\nPostcode: ' + str_(p.postcode, 20) + '\nJob: ' + str_(p.job, 100) + '\n\nDetails:\n' + str_(p.details, 3000) +
    '\n\n– Sent by your website (Maystone)';
  var opts = { from: 'hello@maystone.uk', name: biz + ' website' };
  if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(p.email || ''))) opts.replyTo = String(p.email);
  GmailApp.sendEmail(to, 'New website enquiry: ' + str_(p.job, 60) + ' – ' + str_(p.name, 60), body, opts);
}

function str_(v, max) { return String(v == null ? '' : v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').trim().slice(0, max); }
function esc_(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

var FORM_HTML_ = '<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><style>' +
  ':root{--brand:#0d3b66;--ink:#172027;--soft:#52606b;--line:#d5dbe0;--bg:#f4f6f8}' +
  '*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,Segoe UI,Arial,sans-serif}' +
  '.wrap{max-width:640px;margin:0 auto;padding:24px 16px 64px}h1{font-size:1.6rem;line-height:1.2;margin:.2rem 0 .4rem}' +
  '.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px;margin:16px 0;display:grid;gap:12px}' +
  'h2{font-size:1.1rem;margin:0}label{display:grid;gap:4px;font-weight:600;font-size:.95rem}.hint{font-weight:400;color:var(--soft);font-size:.88rem}' +
  'input,textarea{font:inherit;padding:11px 12px;border:1.5px solid var(--line);border-radius:8px;width:100%;background:#fff}textarea{min-height:90px}' +
  'input:focus,textarea:focus{outline:none;border-color:var(--brand);box-shadow:0 0 0 3px rgba(13,59,102,.2)}' +
  '.thumbs{display:grid;grid-template-columns:repeat(auto-fill,minmax(80px,1fr));gap:8px}.thumbs img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:6px}' +
  'button{font:700 1rem system-ui;background:var(--brand);color:#fff;border:0;border-radius:8px;padding:14px;cursor:pointer;width:100%}button:disabled{opacity:.6}' +
  '.msg{padding:12px;border-radius:8px;display:none}.ok{background:#e7f6ee;color:#1f7a4d;display:block}.err{background:#fdecec;color:#a12626;display:block}' +
  '.brand{font-weight:800;letter-spacing:.02em;color:var(--brand)}' +
  '</style></head><body><div class="wrap">' +
  '<div class="brand">MAYSTONE</div><h1>Your website details</h1>' +
  '<p class="hint" style="font-size:1rem">Thanks for choosing us! Send your photos and details below and we\'ll put them on your site for {{BIZ}}. It takes about 5 minutes. You can send this form again later to update anything.</p>' +
  '<form id="f">' +
  '<div class="card"><h2>Your business</h2>' +
  '<label>Business name<input name="business" value="{{BIZ}}" maxlength="80"></label>' +
  '<label>Phone number for the website<input name="phone" value="{{PHONE}}" maxlength="30"></label>' +
  '<label>Email for website enquiries <span class="hint">New enquiries from your site get sent here.</span><input name="email" type="email" value="{{EMAIL}}" maxlength="120"></label></div>' +
  '<div class="card"><h2>Photos</h2>' +
  '<label>Photos of your work <span class="hint">Up to 12. Your best one first, it goes at the top of the site.</span><input id="photos" type="file" accept="image/*" multiple></label><div class="thumbs" id="pt"></div>' +
  '<label>Your logo <span class="hint">Optional.</span><input id="logo" type="file" accept="image/*"></label><div class="thumbs" id="lt"></div></div>' +
  '<div class="card"><h2>Trust badges</h2>' +
  '<label>Registrations and memberships <span class="hint">e.g. Gas Safe 123456, NICEIC, FMB member, TrustMark. Leave blank if none.</span><input name="reg" maxlength="160"></label>' +
  '<label>Insurance and guarantees <span class="hint">e.g. £2m public liability, 12-month workmanship guarantee.</span><input name="insurance" maxlength="160"></label>' +
  '<label>Company details <span class="hint">Only if you\'re a Ltd company: company number and registered office.</span><input name="company" maxlength="240"></label></div>' +
  '<div class="card"><h2>Web address</h2>' +
  '<label>Do you already own a web address? <span class="hint">e.g. smithsplumbing.co.uk. Leave blank if not.</span><input name="domain_have" maxlength="120"></label>' +
  '<label>If not, any ideas for one? <span class="hint">We\'ll check what\'s available and set it up.</span><input name="domain_ideas" maxlength="200"></label></div>' +
  '<div class="card"><h2>Anything to change?</h2>' +
  '<label>Services, wording, areas you cover… <span class="hint">Tell us anything that\'s wrong or missing.</span><textarea name="changes" maxlength="3000"></textarea></label></div>' +
  '<div id="m" class="msg"></div><button id="b" type="submit">Send my details</button></form></div>' +
  '<script>' +
  'var photos=[],logo=null;' +
  'function shrink(file,max,cb){var r=new FileReader();r.onload=function(){var i=new Image();i.onload=function(){var s=Math.min(1,max/Math.max(i.width,i.height));var c=document.createElement("canvas");c.width=Math.round(i.width*s);c.height=Math.round(i.height*s);var x=c.getContext("2d");x.fillStyle="#fff";x.fillRect(0,0,c.width,c.height);x.drawImage(i,0,0,c.width,c.height);cb(c.toDataURL(file.type==="image/png"&&max<1000?"image/png":"image/jpeg",0.82));};i.onerror=function(){cb(null)};i.src=r.result;};r.readAsDataURL(file);}' +
  'function thumbs(el,list){el.innerHTML="";list.forEach(function(u){var im=document.createElement("img");im.src=u;el.appendChild(im);});}' +
  'document.getElementById("photos").onchange=function(e){photos=[];var fs=[].slice.call(e.target.files,0,12),n=fs.length;if(!n)return thumbs(document.getElementById("pt"),[]);var out=new Array(n);fs.forEach(function(f,ix){shrink(f,1600,function(u){out[ix]=u;if(--n===0){photos=out.filter(Boolean);thumbs(document.getElementById("pt"),photos);}});});};' +
  'document.getElementById("logo").onchange=function(e){var f=e.target.files[0];logo=null;if(!f)return;shrink(f,600,function(u){logo=u;thumbs(document.getElementById("lt"),u?[u]:[]);});};' +
  'document.getElementById("f").onsubmit=function(ev){ev.preventDefault();var b=document.getElementById("b"),m=document.getElementById("m");b.disabled=true;b.textContent="Sending…";m.className="msg";' +
  'var d={};new FormData(ev.target).forEach(function(v,k){d[k]=v;});' +
  'var files=photos.map(function(u,i){return{name:String(i+1),dataUrl:u};});if(logo)files.push({name:"logo",dataUrl:logo});' +
  'google.script.run.withSuccessHandler(function(){m.className="msg ok";m.textContent="Thanks, got it! We\'ll update your website and let you know when it\'s ready.";b.textContent="Sent";})' +
  '.withFailureHandler(function(er){m.className="msg err";m.textContent="Something went wrong: "+(er&&er.message||er)+" Please try again or reply to our email.";b.disabled=false;b.textContent="Send my details";})' +
  '.submitDetails("{{ID}}","{{K}}",d,files);};' +
  '</script></body></html>';
