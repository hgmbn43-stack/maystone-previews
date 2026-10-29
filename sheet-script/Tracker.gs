/**
 * Maystone – preview view tracker (standalone web app owned by harvey@maystone.uk).
 * Each preview page loads <img src="<this web app URL>?v=<LeadID>">. After the preview email has
 * been sent, views are counted in the Call Lists sheet and the rep is emailed on the first view.
 * Deploy: Web app, execute as me, access Anyone.
 */
var TABS = ['Harvey', 'Fin'];
var C = { biz: 2, sent: 15 };
var C2 = { pkg: 18, paid: 19, views: 16, hot: 17 };
var REP_EMAILS = { Harvey: 'harvey@maystone.uk', Fin: 'fin.john@icloud.com' };
var OWNER_EMAIL = 'harvey@maystone.uk';
var CALLS_ID = '1QWrKee1Li45r1Zw2YcIV4XMSUyC-oFueAx4wWglWoEQ';

// ---------- views ----------

function doGet(e) {
  var id = e && e.parameter && String(e.parameter.v || '').replace(/[^A-Za-z0-9_-]/g, '');
  if (id) {
    var lock = LockService.getScriptLock();
    if (lock.tryLock(10000)) {
      try { recordView_(id); } catch (err) { console.error(err); } finally { lock.releaseLock(); }
    }
  }
  return ContentService.createTextOutput('ok');
}

function recordView_(id) {
  var hit = findLead_(id);
  if (!hit) return;
  var sh = hit.sheet, r = hit.row;
  if (!String(sh.getRange(r, C.sent).getValue()).trim()) return; // not sent yet: ignore our own looks
  if (sh.getRange(r, C2.paid).getValue()) return;               // already paid
  var views = Number(sh.getRange(r, C2.views).getValue()) || 0;
  sh.getRange(r, C2.views).setValue(views + 1);
  if (!String(sh.getRange(r, C2.hot).getValue()).trim()) {
    sh.getRange(r, C2.hot).setValue('Yes – ' + Utilities.formatDate(new Date(), 'Europe/London', 'dd/MM HH:mm'));
    var biz = sh.getRange(r, C.biz).getValue(), phone = sh.getRange(r, 5).getValue();
    notify_(sh.getName(), '🔥 ' + biz + ' is looking at their preview now',
      biz + ' just opened their website preview.\n\nCall them now while it\'s on their screen: ' + phone + '\n\nLead ' + id + ' on the ' + sh.getName() + ' tab.');
  }
}

function findLead_(id) {
  var ss = SpreadsheetApp.openById(CALLS_ID);
  for (var t = 0; t < TABS.length; t++) {
    var sh = ss.getSheetByName(TABS[t]);
    if (!sh) continue;
    var last = lastIdRow_(sh);
    if (last < 2) continue;
    var ids = sh.getRange(2, 1, last - 1, 1).getValues();
    for (var i = 0; i < ids.length; i++) if (String(ids[i][0]).trim() === id) return { sheet: sh, row: i + 2 };
  }
  return null;
}

function notify_(tab, subject, body) {
  var to = {};
  to[OWNER_EMAIL] = true;
  if (tab && REP_EMAILS[tab]) to[REP_EMAILS[tab]] = true;
  try { GmailApp.sendEmail(Object.keys(to).join(','), subject, body, { name: 'Maystone sheet' }); } catch (e) { console.error(e); }
}

function lastIdRow_(sh) {
  var n = sh.getLastRow();
  if (n < 2) return 1;
  var col = sh.getRange(1, 1, n, 1).getValues();
  for (var i = col.length - 1; i >= 0; i--) if (String(col[i][0]).trim()) return i + 1;
  return 1;
}

