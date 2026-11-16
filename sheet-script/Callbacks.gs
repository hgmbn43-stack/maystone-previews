/**
 * Callbacks for the closers (setter model, 14 Nov 2026).
 *
 * - "Callbacks" tab: every lead with a Next contact date from every rep tab (booked previews and "call back"s),
 *   sorted by time. Rebuilt every 5 minutes (from processAll) and on demand from the Maystone menu.
 * - "Closer" column: pick Harvey or Fin on the Callbacks tab; it's saved back to the lead's own row,
 *   so it survives the rebuild and you never both ring the same person.
 * - 8am email: today's callbacks plus anything overdue, to Harvey and Fin.
 *
 * Setup once (signed in as harvey@maystone.uk): run installMorning() from the editor.
 */

var CB_TAB = 'Callbacks';
/** Closers' list (16 Nov 2026): every yes / call back, in 4 sections. */
var CB_HEAD = ['Section', 'When', 'Day', 'Time', 'Closer', 'Viewed', 'Business', 'Trade', 'Town', 'Phone', 'Client email', 'Booked by', 'Outcome', 'Tries', 'Preview (staff link)', 'Rep tab', 'Lead ID'];
var CBI = {}; CB_HEAD.forEach(function (h, i) { CBI[h] = i; });
var CB_ORDER = { '1 Due now': 1, '2 Waiting': 2, '3 Gone quiet': 3, '4 Done': 4 };
var CB_BG = { '1 Due now': '#FDECEC', '2 Waiting': '#FFF8E5', '3 Gone quiet': '#EEEEEE', '4 Done': '#E8F5E9' };
var CLOSERS = ['Harvey', 'Fin'];
var MORNING_TO = ['harvey@maystone.uk', 'finsj101@gmail.com'];

function repTabsCb_() {
  return SpreadsheetApp.getActive().getSheets().filter(function (s) { return String(s.getRange(1, 1).getValue()).trim() === 'Lead ID'; });
}

function ensureCol_(sh, head, name) {
  var c = head.indexOf(name);
  if (c !== -1) return c;
  var lc = sh.getLastColumn() + 1;
  sh.getRange(1, lc).setValue(name).setFontWeight('bold');
  head.push(name);
  return head.length - 1;
}

/** Joins a Next contact date and a Callback time ("17:30" text or a time value) into one Date. */
function cbWhen_(d, t) {
  if (!d) return null;
  var day = d instanceof Date ? new Date(d.getTime()) : new Date(String(d));
  if (isNaN(day.getTime())) return null;
  var h = 9, m = 0, hasTime = false;
  if (t instanceof Date) { h = t.getHours(); m = t.getMinutes(); hasTime = true; }
  else { var mm = String(t || '').match(/(\d{1,2})[:.](\d{2})/); if (mm) { h = Number(mm[1]); m = Number(mm[2]); hasTime = true; } }
  day.setHours(h, m, 0, 0);
  return { at: day, hasTime: hasTime };
}

function buildCallbacks() {
  var ss = SpreadsheetApp.getActive(), tz = 'Europe/London', out = [], now = Date.now(), soon = now + 2 * 3600000;
  repTabsCb_().forEach(function (sh) {
    if (sh.getName() === CB_TAB) return;
    var lr = sh.getLastRow(); if (lr < 2) return;
    var head = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0].map(String);
    ensureCol_(sh, head, 'Closer');
    var v = sh.getRange(1, 1, lr, head.length).getValues(), col = function (h) { return head.indexOf(h); };
    for (var i = 1; i < v.length; i++) {
      var r = v[i], id = String(r[0]).trim(); if (!id) continue;
      var outcome = String(r[col('Outcome')] || '').trim();
      if (!/^\s*yes|call\s*back/i.test(outcome)) continue;
      if (col('Do not call') > -1 && r[col('Do not call')] === true) continue;
      var paid = /^paid/i.test(String(r[col('Paid')] || '').trim());
      var views = Number(r[C2.views - 1]) || 0, tries = col('Tries') > -1 ? Number(r[col('Tries')]) || 0 : 0;
      var w = cbWhen_(r[col('Next contact')], col('Callback time') === -1 ? '' : r[col('Callback time')]);
      var at = w ? w.at : null, section;
      if (paid) section = '4 Done';
      else if (tries >= 3) section = '3 Gone quiet';
      else if (!at || at.getTime() <= soon) section = '1 Due now';
      else section = '2 Waiting';
      var prev = String(r[col('Preview link')] || '').trim();
      out.push([section, at || '', at ? Utilities.formatDate(at, tz, 'EEE d MMM') : 'No time set',
        at ? (w.hasTime ? Utilities.formatDate(at, tz, 'HH:mm') : 'any time') : 'call today',
        String(r[col('Closer')] || ''), views ? 'Yes (' + views + ')' : 'Not yet',
        r[col('Business')], r[col('Trade')], r[col('Town')], r[col('Phone')], r[col('Client email')],
        col('Booked by') === -1 ? '' : r[col('Booked by')], outcome, tries || '',
        prev ? prev + (prev.indexOf('?') === -1 ? '?me' : '&me') : '', sh.getName(), id]);
    }
  });
  out.sort(function (a, b) {
    var s = CB_ORDER[a[0]] - CB_ORDER[b[0]]; if (s) return s;
    if (a[0] === '1 Due now') { var va = a[CBI.Viewed] === 'Not yet' ? 1 : 0, vb = b[CBI.Viewed] === 'Not yet' ? 1 : 0; if (va !== vb) return va - vb; }
    return (a[1] ? a[1].getTime() : 0) - (b[1] ? b[1].getTime() : 0);
  });
  var cb = ss.getSheetByName(CB_TAB) || ss.insertSheet(CB_TAB);
  cb.clear(); try { cb.getRange(1, 1, cb.getMaxRows(), cb.getMaxColumns()).clearDataValidations(); } catch (e) {}
  cb.getRange(1, 1, 1, CB_HEAD.length).setValues([CB_HEAD]).setFontWeight('bold').setBackground('#142D4C').setFontColor('#ffffff');
  cb.setFrozenRows(1);
  if (out.length) {
    cb.getRange(2, 1, out.length, CB_HEAD.length).setValues(out);
    cb.getRange(2, CBI.When + 1, out.length, 1).setNumberFormat('dd/mm/yyyy hh:mm');
    cb.getRange(2, CBI.Closer + 1, out.length, 1).setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(CLOSERS, true).setAllowInvalid(true).build());
    cb.getRange(2, 1, out.length, CB_HEAD.length).setBackgrounds(out.map(function (r) { return CB_HEAD.map(function () { return CB_BG[r[0]]; }); }));
    cb.getRange(2, 1, out.length, 1).setFontWeight('bold');
  } else {
    cb.getRange(2, 1).setValue('No previews booked yet.');
  }
  cb.getRange(1, CB_HEAD.length + 2).setValue('Rebuilt ' + Utilities.formatDate(new Date(), tz, 'dd/MM HH:mm') +
    '. 1 Due now = call these (viewed ones first; no time set = call today). 2 Waiting = later callback. 3 Gone quiet = 3 no-answers: one last text, then mark it a no. 4 Done = paid. Pick your name in Closer. Edit the lead itself on its rep tab.');
  return out;
}

/** Called from onEditRun: a Closer picked on the Callbacks tab is saved back to the lead's row. */
function callbackEdit_(e) {
  var sh = e.range.getSheet(); if (sh.getName() !== CB_TAB) return false;
  if (e.range.getColumn() !== CBI.Closer + 1 || e.range.getNumRows() !== 1 || e.range.getRow() < 2) return true;
  var row = sh.getRange(e.range.getRow(), 1, 1, CB_HEAD.length).getValues()[0], tab = String(row[CBI['Rep tab']]), id = String(row[CBI['Lead ID']]).trim();
  var rep = SpreadsheetApp.getActive().getSheetByName(tab); if (!rep || !id) return true;
  var head = rep.getRange(1, 1, 1, rep.getLastColumn()).getValues()[0].map(String), c = ensureCol_(rep, head, 'Closer');
  var ids = rep.getRange(1, 1, rep.getLastRow(), 1).getValues();
  for (var i = 1; i < ids.length; i++) if (String(ids[i][0]).trim() === id) { rep.getRange(i + 1, c + 1).setValue(e.range.getValue()); break; }
  return true;
}

function morningCallbacks() {
  var all = buildCallbacks().filter(function (r) { return r[0] === '1 Due now'; }), tz = 'Europe/London';
  if (!all.length) return;
  var line = function (r) {
    return '<tr><td style="padding:6px 10px"><b>' + cbEsc_(r[CBI.Time]) + '</b><br><small>' + cbEsc_(r[CBI.Day]) + '</small></td><td style="padding:6px 10px"><b>' + cbEsc_(r[CBI.Business]) + '</b><br><small>' + cbEsc_([r[CBI.Trade], r[CBI.Town]].filter(String).join(' · ')) + '</small></td>' +
      '<td style="padding:6px 10px"><a href="tel:' + String(r[CBI.Phone]).replace(/[^\d+]/g, '') + '">' + cbEsc_(r[CBI.Phone]) + '</a></td><td style="padding:6px 10px">Viewed: ' + cbEsc_(r[CBI.Viewed]) + '<br>' + (r[CBI.Closer] ? cbEsc_(r[CBI.Closer]) : '<b style="color:#E0531F">Unclaimed</b>') + '</td>' +
      '<td style="padding:6px 10px"><small>Booked by ' + cbEsc_(r[CBI['Booked by']] || r[CBI['Rep tab']]) + '</small>' + (r[CBI['Preview (staff link)']] ? '<br><a href="' + r[CBI['Preview (staff link)']] + '">Preview</a>' : '') + '</td></tr>';
  };
  var html = '<div style="font:15px Arial,sans-serif;color:#142D4C"><h2 style="margin:0 0 8px">Due now (' + all.length + ')</h2>' +
    '<table style="border-collapse:collapse;font:14px Arial,sans-serif;border:1px solid #ddd">' + all.map(line).join('') + '</table>' +
    '<p style="margin-top:16px">Viewed ones are at the top. Claim each one in the <b>Closer</b> column on the Callbacks tab. <a href="' + SpreadsheetApp.getActive().getUrl() + '">Open the call sheet</a></p></div>';
  GmailApp.sendEmail(MORNING_TO.join(','), 'Callbacks due today: ' + all.length, 'Open in an email app that shows HTML.', { htmlBody: html, from: SENDER, name: SENDER_NAME });
}


/** Run once from the editor: the 8am email, every day. */
function installMorning() {
  ScriptApp.getProjectTriggers().forEach(function (t) { if (t.getHandlerFunction() === 'morningCallbacks') ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('morningCallbacks').timeBased().everyDays(1).atHour(8).inTimezone('Europe/London').create();
  buildCallbacks();
  return 'Morning email set for 8am. Callbacks tab built.';
}

function cbEsc_(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
