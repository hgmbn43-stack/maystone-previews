/**
 * Maystone – nightly tidy (10pm).
 * - "Number not recognised" leads are moved off the Harvey/Fin tabs into a hidden "Binned" tab.
 * - Leads that didn't answer / went to voicemail / were busy are copied into the
 *   Booking Automation Leads sheet (once each), for the booking-system pitch.
 * Run installNightly() once from the editor to switch it on.
 */

var BOOKING_ID = '1boR15O45Q81m97uDYsXAluKDJePkIjMtRy_y3pzuGZA';
var BOOKING_TAB = 'Booking leads';

function installNightly() {
  ScriptApp.getProjectTriggers().forEach(function (t) { if (t.getHandlerFunction() === 'nightlySort') ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('nightlySort').timeBased().everyDays(1).atHour(22).inTimezone('Europe/London').create();
  return nightlySort();
}

function nightlySort() {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(60000)) return 'busy';
  try { return nightlySort_(); } finally { lock.releaseLock(); }
}

function nightlySort_() {
  var ss = SpreadsheetApp.openById(CALLS_ID);
  var book = SpreadsheetApp.openById(BOOKING_ID).getSheetByName(BOOKING_TAB);
  var have = {};
  if (book.getLastRow() >= 2) book.getRange(2, 1, book.getLastRow() - 1, 1).getValues().forEach(function (r) { have[String(r[0]).trim()] = true; });

  var bin = ss.getSheetByName('Binned');
  var binned = 0, added = 0;
  TABS.forEach(function (name) {
    var sh = ss.getSheetByName(name);
    if (!sh) return;
    var last = lastIdRow_(sh);
    if (last < 2) return;
    var width = sh.getLastColumn();
    var vals = sh.getRange(2, 1, last - 1, width).getValues();
    var toDelete = [];
    vals.forEach(function (v, i) {
      var id = String(v[0]).trim();
      if (!id) return;
      var called = String(v[8]).replace(/\s+/g, ' ').trim();   // I
      var outcome = String(v[9]).trim();                       // J
      var dnc = v[26] === true;                                // AA
      if (/not\s*rec/i.test(called)) {
        if (!bin) {
          bin = ss.insertSheet('Binned');
          bin.getRange(1, 1, 1, width + 1).setValues([sh.getRange(1, 1, 1, width).getValues()[0].concat(['From tab'])]).setFontWeight('bold');
          bin.hideSheet();
        }
        bin.appendRow(v.concat([name]));
        toDelete.push(i + 2);
        binned++;
        return;
      }
      if (dnc || have[id]) return;
      if (!/(didn.*answer|no answer|voice ?mail|busy)/i.test(called)) return;
      if (/yes|not int|intrest|already|no thanks|not trading|retir/i.test(outcome)) return;
      var trade = String(v[2]).trim();
      var result = /voice/i.test(called) ? 'Voicemail' : /busy/i.test(called) ? 'Busy' : 'No answer';
      var line = 'I rang you the other day and couldn\'t get through – if that was a customer needing a ' + trade.toLowerCase() +
        ', they\'d have rung the next one on Google. We set up a system that answers and books those jobs in for you.';
      book.appendRow([id, v[1], trade, v[3], v[4], name, result, v[20], v[21], line, false, '', '', '', '', '']);
      book.getRange(book.getLastRow(), 11).insertCheckboxes();
      have[id] = true;
      added++;
    });
    for (var d = toDelete.length - 1; d >= 0; d--) sh.deleteRow(toDelete[d]);
  });
  return 'Binned ' + binned + ', added ' + added + ' to booking list';
}
