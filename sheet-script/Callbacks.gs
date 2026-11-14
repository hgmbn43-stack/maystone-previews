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
var CB_HEAD = ['When', 'Day', 'Time', 'Closer', 'Business', 'Trade', 'Town', 'Phone', 'Client email', 'Booked by', 'Outcome', 'Preview (staff link)', 'Rep tab', 'Lead ID', 'Status'];
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
  var ss = SpreadsheetApp.getActive(), tz = 'Europe/London', out = [], now = Date.now();
  repTabsCb_().forEach(function (sh) {
    if (sh.getName() === CB_TAB) return;
    var lr = sh.getLastRow(); if (lr < 2) return;
    var head = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0].map(String);
    ensureCol_(sh, head, 'Closer');
    var v = sh.getRange(1, 1, lr, head.length).getValues(), col = function (h) { return head.indexOf(h); };
    for (var i = 1; i < v.length; i++) {
      var r = v[i], id = String(r[0]).trim(); if (!id) continue;
      var outcome = String(r[col('Outcome')] || '').trim(), next = r[col('Next contact')];
      if (!next || r[col('Do not call')] === true) continue;
      if (!/^\s*yes|call\s*back/i.test(outcome)) continue;
      if (/^paid/i.test(String(r[col('Paid')] || '').trim())) continue;
      var w = cbWhen_(next, col('Callback time') === -1 ? '' : r[col('Callback time')]); if (!w) continue;
      var prev = String(r[col('Preview link')] || '').trim();
      out.push([w.at, Utilities.formatDate(w.at, tz, 'EEE d MMM'), w.hasTime ? Utilities.formatDate(w.at, tz, 'HH:mm') : 'any time',
        String(r[col('Closer')] || ''), r[col('Business')], r[col('Trade')], r[col('Town')], r[col('Phone')], r[col('Client email')],
        col('Booked by') === -1 ? '' : r[col('Booked by')], outcome, prev ? prev + (prev.indexOf('?') === -1 ? '?me' : '&me') : '',
        sh.getName(), id, w.at.getTime() < now - 3600000 ? 'Overdue' : 'Due']);
    }
  });
  out.sort(function (a, b) { return a[0] - b[0]; });
  var cb = ss.getSheetByName(CB_TAB) || ss.insertSheet(CB_TAB);
  cb.clear();
  cb.getRange(1, 1, 1, CB_HEAD.length).setValues([CB_HEAD]).setFontWeight('bold').setBackground('#142D4C').setFontColor('#ffffff');
  cb.setFrozenRows(1);
  if (out.length) {
    cb.getRange(2, 1, out.length, CB_HEAD.length).setValues(out);
    cb.getRange(2, 1, out.length, 1).setNumberFormat('dd/mm/yyyy hh:mm');
    cb.getRange(2, 4, out.length, 1).setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(CLOSERS, true).setAllowInvalid(true).build());
    var bg = out.map(function (r) { return CB_HEAD.map(function () { return r[14] === 'Overdue' ? '#FDECEC' : r[3] ? '#ffffff' : '#FFF4E5'; }); });
    cb.getRange(2, 1, out.length, CB_HEAD.length).setBackgrounds(bg);
  } else {
    cb.getRange(2, 1).setValue('No callbacks booked yet.');
  }
  cb.getRange(1, CB_HEAD.length + 2).setValue('Rebuilt ' + Utilities.formatDate(new Date(), tz, 'dd/MM HH:mm') + '. Pick a Closer (Harvey or Fin). Orange = nobody has claimed it, red = overdue. Edit the lead itself on its rep tab.');
  return out;
}

/** Called from onEditRun: a Closer picked on the Callbacks tab is saved back to the lead's row. */
function callbackEdit_(e) {
  var sh = e.range.getSheet(); if (sh.getName() !== CB_TAB) return false;
  if (e.range.getColumn() !== 4 || e.range.getNumRows() !== 1 || e.range.getRow() < 2) return true;
  var row = sh.getRange(e.range.getRow(), 1, 1, CB_HEAD.length).getValues()[0], tab = String(row[12]), id = String(row[13]).trim();
  var rep = SpreadsheetApp.getActive().getSheetByName(tab); if (!rep || !id) return true;
  var head = rep.getRange(1, 1, 1, rep.getLastColumn()).getValues()[0].map(String), c = ensureCol_(rep, head, 'Closer');
  var ids = rep.getRange(1, 1, rep.getLastRow(), 1).getValues();
  for (var i = 1; i < ids.length; i++) if (String(ids[i][0]).trim() === id) { rep.getRange(i + 1, c + 1).setValue(e.range.getValue()); break; }
  sh.getRange(e.range.getRow(), 1, 1, CB_HEAD.length).setBackground('#ffffff');
  return true;
}

function morningCallbacks() {
  var tz = 'Europe/London', all = buildCallbacks(), today = Utilities.formatDate(new Date(), tz, 'yyyy-MM-dd');
  var todays = all.filter(function (r) { return Utilities.formatDate(r[0], tz, 'yyyy-MM-dd') === today; });
  var overdue = all.filter(function (r) { return r[14] === 'Overdue' && Utilities.formatDate(r[0], tz, 'yyyy-MM-dd') < today; });
  if (!todays.length && !overdue.length) return;
  var line = function (r) {
    return '<tr><td style="padding:6px 10px"><b>' + r[2] + '</b>' + (r[14] === 'Overdue' ? '<br><small>' + r[1] + '</small>' : '') + '</td><td style="padding:6px 10px"><b>' + cbEsc_(r[4]) + '</b><br><small>' + cbEsc_([r[5], r[6]].filter(String).join(' · ')) + '</small></td>' +
      '<td style="padding:6px 10px"><a href="tel:' + String(r[7]).replace(/[^\d+]/g, '') + '">' + cbEsc_(r[7]) + '</a></td><td style="padding:6px 10px">' + (r[3] ? cbEsc_(r[3]) : '<b style="color:#E0531F">Unclaimed</b>') + '</td>' +
      '<td style="padding:6px 10px"><small>Booked by ' + cbEsc_(r[9] || r[12]) + '</small>' + (r[11] ? '<br><a href="' + r[11] + '">Preview</a>' : '') + '</td></tr>';
  };
  var table = function (rows) { return '<table style="border-collapse:collapse;font:14px Arial,sans-serif;border:1px solid #ddd">' + rows.map(line).join('') + '</table>'; };
  var html = '<div style="font:15px Arial,sans-serif;color:#142D4C">' +
    (todays.length ? '<h2 style="margin:0 0 8px">Today\'s callbacks (' + todays.length + ')</h2>' + table(todays) : '<p>No callbacks booked for today.</p>') +
    (overdue.length ? '<h3 style="margin:18px 0 8px;color:#B42318">Overdue (' + overdue.length + ')</h3>' + table(overdue) : '') +
    '<p style="margin-top:16px">Claim each one in the <b>Closer</b> column on the Callbacks tab so you don\'t both ring the same person. ' +
    '<a href="' + SpreadsheetApp.getActive().getUrl() + '">Open the call sheet</a></p></div>';
  GmailApp.sendEmail(MORNING_TO.join(','), 'Callbacks today: ' + todays.length + (overdue.length ? ' (+' + overdue.length + ' overdue)' : ''), 'Open in an email app that shows HTML.',
    { htmlBody: html, from: SENDER, name: SENDER_NAME });
}


/** Run once from the editor: the 8am email, every day. */
function installMorning() {
  ScriptApp.getProjectTriggers().forEach(function (t) { if (t.getHandlerFunction() === 'morningCallbacks') ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('morningCallbacks').timeBased().everyDays(1).atHour(8).inTimezone('Europe/London').create();
  buildCallbacks();
  return 'Morning email set for 8am. Callbacks tab built.';
}

function cbEsc_(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
