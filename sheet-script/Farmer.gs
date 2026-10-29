/**
 * Maystone – Lead Farmer (runs inside the Call Lists sheet, no Zapier).
 *
 * Weekdays ~06:00: picks the next town from the queue, starts an Apify Google Maps scrape
 * (businesses WITHOUT a website only). The 5-minute processAll run checks on it; when it
 * finishes, new leads are filtered, de-duplicated against the master sheet + Do Not Call,
 * graded A/B/C, written to the master "Maystone – Leads" sheet (Leads tab) and split
 * fairly between the Harvey and Fin tabs here. A Coverage row is logged in the master.
 *
 * Setup: Maystone menu -> 3. Set Apify key, then 4. Switch on lead farmer.
 */

var MASTER_ID = '1mbmuBmjrXDgVm7GlkptSGpBHloYSkMB1h81Xfwy6zik';
var ACTOR = 'compass~crawler-google-places';
var MAX_RUN_USD = 0.5;
var MIN_CREDIT_USD = 5;
var SEARCHES = ['plasterer', 'carpenter', 'builder', 'painter and decorator', 'plumber', 'roofer',
  'electrician', 'landscaper', 'handyman', 'tiler', 'gardener', 'fencing contractor'];
var QUEUE = ['Bognor Regis', 'Chichester', 'Horsham', 'Crawley', 'Burgess Hill', 'Haywards Heath',
  'Eastbourne', 'Lewes', 'Seaford', 'Newhaven', 'Peacehaven', 'Hastings', 'Bexhill-on-Sea',
  'East Grinstead', 'Crowborough', 'Uckfield', 'Hailsham', 'Arundel', 'Steyning', 'Storrington',
  'Southwick', 'Hassocks', 'Henfield', 'Midhurst', 'Selsey', 'Portsmouth', 'Havant', 'Southampton',
  'Guildford', 'Tunbridge Wells', 'Petersfield', 'Haslemere', 'Godalming', 'Farnham', 'Reigate',
  'Redhill', 'Dorking', 'Leatherhead', 'Epsom', 'Woking', 'Camberley', 'Fareham', 'Gosport',
  'Waterlooville', 'Eastleigh', 'Winchester', 'Basingstoke', 'Andover', 'Romsey', 'Tonbridge',
  'Sevenoaks', 'Maidstone', 'Ashford', 'Folkestone', 'Hythe', 'Rye', 'Battle', 'Heathfield',
  'Billingshurst', 'Pulborough', 'Littlehampton', 'Rustington', 'Angmering'];
var NOT_A_TRADE_NAME = /\b(register|directory|merchants?|supplies|wholesale)\b/i;
var NOT_A_TRADE_CAT = /apartment|\bpark\b|lodging|allotment|transport hub|^house$|hotel|landmark|hiking|discount store|cottage|community garden|takeaway|restaurant|bed & breakfast|guest house|holiday|materials supplier|\bschool\b|\bchurch\b/i;
var PRIORITY_ORDER = { A: 0, B: 1, C: 2 };

// ---------- menu actions ----------

function setApifyKey() {
  var ui = SpreadsheetApp.getUi();
  var r = ui.prompt('Apify key', 'Paste your Apify API token (Apify console > Settings > API & Integrations).', ui.ButtonSet.OK_CANCEL);
  if (r.getSelectedButton() !== ui.Button.OK) return;
  PropertiesService.getUserProperties().setProperty('APIFY_TOKEN', r.getResponseText().trim());
  var res = apify_('GET', 'users/me/limits');
  ui.alert(res.code === 200 ? 'Apify key saved and working. Credit left this month: $' + creditLeft_(res.json).toFixed(2) : 'Key saved, but Apify said ' + res.code + '.');
}

function switchOnFarmer() {
  var ui = SpreadsheetApp.getUi();
  if (!PropertiesService.getUserProperties().getProperty('APIFY_TOKEN')) { ui.alert('Do step 3 (Apify key) first.'); return; }
  ScriptApp.getProjectTriggers().forEach(function (t) { if (t.getHandlerFunction() === 'farmDaily') ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('farmDaily').timeBased().everyDays(1).atHour(6).inTimezone('Europe/London').create();
  ui.alert('Lead farmer is on. Every weekday around 6am it adds one new town of leads to the Harvey and Fin tabs.\nNext town: ' + (nextTown_() || 'queue finished'));
}

/** Menu: start a scrape now (any day). */
function farmNow() {
  var msg = startFarm_(true);
  SpreadsheetApp.getUi().alert(msg);
}

/** Daily trigger. */
function farmDaily() {
  var day = Number(Utilities.formatDate(new Date(), 'Europe/London', 'u')); // 1 = Mon ... 7 = Sun
  if (day > 5) return;
  startFarm_(false);
}

// ---------- start + poll ----------

function startFarm_(manual) {
  var props = PropertiesService.getScriptProperties();
  if (props.getProperty('FARM_RUN')) return 'A scrape is already running. Leads appear within about 15 minutes.';
  if (!PropertiesService.getUserProperties().getProperty('APIFY_TOKEN')) return 'No Apify key set.';
  var limits = apify_('GET', 'users/me/limits');
  if (limits.code !== 200) return 'Apify error ' + limits.code;
  var left = creditLeft_(limits.json);
  if (left < MIN_CREDIT_USD) {
    logCoverage_(['paused – Apify budget', '', 0, 0, '', 0, 'Only $' + left.toFixed(2) + ' credit left']);
    return 'Paused: only $' + left.toFixed(2) + ' Apify credit left this month.';
  }
  var town = nextTown_();
  if (!town) return 'Town queue finished. Add more towns to QUEUE in Farmer.gs.';
  var input = {
    searchStringsArray: SEARCHES, locationQuery: town + ', United Kingdom', maxCrawledPlacesPerSearch: 25,
    language: 'en', website: 'withoutWebsite', skipClosedPlaces: false, scrapePlaceDetailPage: false,
    maxReviews: 0, maxImages: 0, maxQuestions: 0, scrapeContacts: false
  };
  var run = apify_('POST', 'acts/' + ACTOR + '/runs?maxTotalChargeUsd=' + MAX_RUN_USD, input);
  if (run.code !== 201) return 'Could not start Apify: ' + run.code + ' ' + JSON.stringify(run.json).slice(0, 200);
  props.setProperty('FARM_RUN', JSON.stringify({ id: run.json.data.id, town: town, started: Date.now() }));
  return 'Started scraping ' + town + '. New leads appear in the Harvey and Fin tabs within about 15 minutes.';
}

/** Called from processAll every 5 minutes. */
function farmPoll_() {
  var props = PropertiesService.getScriptProperties();
  var raw = props.getProperty('FARM_RUN');
  if (!raw) return;
  var job = JSON.parse(raw);
  var run = apify_('GET', 'actor-runs/' + job.id);
  if (run.code !== 200) return;
  var status = run.json.data.status;
  if (status === 'READY' || status === 'RUNNING') {
    if (Date.now() - job.started > 2 * 3600 * 1000) { props.deleteProperty('FARM_RUN'); logCoverage_([job.town, '12 trades', 0, 0, '', 0, 'Apify run timed out']); }
    return;
  }
  props.deleteProperty('FARM_RUN');
  var cost = Number(run.json.data.usageTotalUsd || 0);
  if (status !== 'SUCCEEDED') { logCoverage_([job.town, '12 trades', 0, 0, '', round2_(cost), 'Apify run ' + status]); return; }
  var items = apify_('GET', 'datasets/' + run.json.data.defaultDatasetId + '/items?clean=true&limit=1000');
  addLeads_(job.town, items.json || [], cost);
}

// ---------- build + write ----------

function addLeads_(town, items, cost) {
  var master = SpreadsheetApp.openById(MASTER_ID);
  var leadsTab = master.getSheetByName('Leads');
  var existing = readExisting_(master, leadsTab);
  var today = Utilities.formatDate(new Date(), 'Europe/London', 'yyyy-MM-dd');

  var rows = [], seenPhone = {}, seenPlace = {};
  items.forEach(function (it) {
    var pid = it.placeId;
    if (!pid || existing.places[pid] || seenPlace[pid]) return;
    seenPlace[pid] = true;
    if (it.permanentlyClosed || it.temporarilyClosed) return;
    if (it.website && !/facebook\.com|fb\.com|instagram\.com|checkatrade|mybuilder|trustatrader|ratedpeople|yell\.com|bark\.com|linktr\.ee/i.test(it.website)) return;
    var name = clean_(it.title);
    var cat = clean_(it.categoryName);
    if (!name || NOT_A_TRADE_NAME.test(name) || NOT_A_TRADE_CAT.test(cat)) return;
    var phone = ukPhone_(it.phone);
    var key = digits_(phone);
    if (!key || existing.phones[key]) return;
    var rating = (it.totalScore === null || it.totalScore === undefined || it.totalScore === '') ? null : Number(it.totalScore);
    var reviews = Number(it.reviewsCount || 0);
    var row = { name: name, cat: cat || titleCase_(it.searchString || ''), town: clean_(it.city) || town, phone: phone,
                rating: rating, reviews: reviews, pid: pid, notes: (/^(none|null)$/i.test(name) ? 'Google listing has no proper business name (shows as "None")' : '') };
    row.priority = priority_(rating, reviews);
    var clash = seenPhone[key];
    if (clash) {
      if (reviews > clash.reviews) { rows[rows.indexOf(clash)] = row; seenPhone[key] = row; }
      return;
    }
    seenPhone[key] = row;
    rows.push(row);
  });

  // shared number blocks (call-tracking / answering services)
  var blocks = {};
  Object.keys(existing.phones).concat(Object.keys(seenPhone)).forEach(function (k) { var b = k.slice(0, -2); blocks[b] = (blocks[b] || 0) + 1; });
  rows.forEach(function (r) {
    var n = blocks[digits_(r.phone).slice(0, -2)];
    if (n >= 3) {
      var note = 'Shared number block (' + n + ' listings): may be a call-tracking or answering service, check you\'re speaking to the owner';
      r.notes = r.notes ? r.notes + '; ' + note : note;
    }
  });

  rows.sort(function (a, b) {
    return (PRIORITY_ORDER[a.priority] - PRIORITY_ORDER[b.priority]) || (b.reviews - a.reviews) || a.name.toLowerCase().localeCompare(b.name.toLowerCase());
  });

  var nextNum = existing.maxId + 1;
  var values = rows.map(function (r, i) {
    var id = 'L' + ('00' + (nextNum + i)).slice(-3);
    r.id = id;
    return [id, r.name, r.cat, r.town, r.phone, 'No website', mention_(r.rating, r.reviews), 'Not checked',
      '', '', '', r.notes, '', '', '', '', '', '', '', r.priority,
      r.rating === null ? '' : r.rating, r.reviews, 'https://www.google.com/maps/place/?q=place_id:' + r.pid, today];
  });

  if (values.length) {
    writeAfterLast_(leadsTab, values);
    splitToReps_(values);
  }
  var ids = values.length ? values[0][0] + '–' + values[values.length - 1][0] : '';
  var counts = { A: 0, B: 0, C: 0 };
  rows.forEach(function (r) { counts[r.priority]++; });
  logCoverage_([town, '12 trades', items.length, values.length, ids, round2_(cost), 'Sheet script (Apify no-website filter)']);
  try { SpreadsheetApp.getActive().toast('+' + values.length + ' leads from ' + town + ' (A ' + counts.A + ', B ' + counts.B + ')', 'Lead farmer', 10); } catch (e) {}
}

function readExisting_(master, leadsTab) {
  var places = {}, phones = {}, maxId = 0;
  var last = lastIdRow_(leadsTab);
  if (last >= 2) {
    leadsTab.getRange(2, 1, last - 1, 23).getValues().forEach(function (r) {
      var m = String(r[0]).match(/^L(\d+)$/);
      if (m) maxId = Math.max(maxId, Number(m[1]));
      var k = digits_(r[4]); if (k) phones[k] = true;
      (String(r[11]).match(/0\d[\d ]{8,12}\d/g) || []).forEach(function (p) { phones[digits_(p)] = true; });
      var pm = String(r[22]).match(/place_id:([\w-]+)/); if (pm) places[pm[1]] = true;
    });
  }
  var dnc = master.getSheetByName('Do Not Call');
  if (dnc && dnc.getLastRow() >= 2) {
    dnc.getRange(2, 1, dnc.getLastRow() - 1, 1).getValues().forEach(function (r) { var k = digits_(r[0]); if (k) phones[k] = true; });
  }
  // Leads in the call-list tabs too (in case any were added by hand)
  TABS.forEach(function (name) {
    var sh = SpreadsheetApp.getActive().getSheetByName(name);
    var l = sh ? lastIdRow_(sh) : 0;
    if (l >= 2) sh.getRange(2, 1, l - 1, 23).getValues().forEach(function (r) {
      var m = String(r[0]).match(/^L(\d+)$/); if (m) maxId = Math.max(maxId, Number(m[1]));
      var k = digits_(r[4]); if (k) phones[k] = true;
      var pm = String(r[22]).match(/place_id:([\w-]+)/); if (pm) places[pm[1]] = true;
    });
  });
  return { places: places, phones: phones, maxId: maxId };
}

/** Deal new leads out between the rep tabs: snake order, starting with whoever has fewer leads. */
function splitToReps_(values) {
  var ss = SpreadsheetApp.getActive();
  var tabs = TABS.map(function (n) { return ss.getSheetByName(n); }).filter(Boolean);
  if (!tabs.length) return;
  var counts = tabs.map(function (sh) { return Math.max(0, lastIdRow_(sh) - 1); });
  var order = tabs.map(function (_, i) { return i; }).sort(function (a, b) { return counts[a] - counts[b]; });
  var buckets = tabs.map(function () { return []; });
  values.forEach(function (v, i) {
    var round = Math.floor(i / order.length), pos = i % order.length;
    buckets[order[round % 2 === 0 ? pos : order.length - 1 - pos]].push(v);
  });
  tabs.forEach(function (sh, i) { if (buckets[i].length) writeAfterLast_(sh, buckets[i]); });
}

/** Write rows (A..X) directly under the last Lead ID; grow the grid and carry formats/tick boxes if needed. */
function writeAfterLast_(sh, values) {
  var first = lastIdRow_(sh) + 1;
  var need = first + values.length - 1;
  if (need > sh.getMaxRows()) {
    var oldMax = sh.getMaxRows();
    sh.insertRowsAfter(oldMax, need - oldMax + 200);
    sh.getRange(2, 1, 1, sh.getMaxColumns()).copyTo(sh.getRange(oldMax + 1, 1, sh.getMaxRows() - oldMax, sh.getMaxColumns()), SpreadsheetApp.CopyPasteType.PASTE_FORMAT, false);
    sh.getRange(2, 1, 1, sh.getMaxColumns()).copyTo(sh.getRange(oldMax + 1, 1, sh.getMaxRows() - oldMax, sh.getMaxColumns()), SpreadsheetApp.CopyPasteType.PASTE_DATA_VALIDATION, false);
  }
  sh.getRange(first, 5, values.length, 1).setNumberFormat('@'); // keep leading zeros on phones
  sh.getRange(first, 1, values.length, values[0].length).setValues(values);
}

function lastIdRow_(sh) {
  var n = sh.getLastRow();
  if (n < 2) return 1;
  var col = sh.getRange(1, 1, n, 1).getValues();
  for (var i = col.length - 1; i >= 0; i--) if (String(col[i][0]).trim()) return i + 1;
  return 1;
}

function nextTown_() {
  var cov = SpreadsheetApp.openById(MASTER_ID).getSheetByName('Coverage');
  var done = {};
  if (cov && cov.getLastRow() >= 2) {
    cov.getRange(2, 2, cov.getLastRow() - 1, 1).getValues().forEach(function (r) {
      String(r[0]).split(/;\s*|\s*&\s*/).forEach(function (t) { done[t.trim().toLowerCase()] = true; });
    });
  }
  for (var i = 0; i < QUEUE.length; i++) if (!done[QUEUE[i].toLowerCase()]) return QUEUE[i];
  return null;
}

function logCoverage_(cols) {
  var cov = SpreadsheetApp.openById(MASTER_ID).getSheetByName('Coverage');
  if (!cov) return;
  cov.appendRow([Utilities.formatDate(new Date(), 'Europe/London', 'yyyy-MM-dd')].concat(cols));
}

// ---------- helpers ----------

function apify_(method, path, payload) {
  var token = PropertiesService.getUserProperties().getProperty('APIFY_TOKEN');
  var opts = { method: method, muteHttpExceptions: true, headers: { Authorization: 'Bearer ' + token } };
  if (payload) { opts.contentType = 'application/json'; opts.payload = JSON.stringify(payload); }
  var res = UrlFetchApp.fetch('https://api.apify.com/v2/' + path, opts);
  var json = null;
  try { json = JSON.parse(res.getContentText()); } catch (e) {}
  return { code: res.getResponseCode(), json: json };
}

function creditLeft_(limitsJson) {
  var d = limitsJson.data;
  return Number(d.limits.maxMonthlyUsageUsd) - Number(d.current.monthlyUsageUsd);
}

function priority_(rating, reviews) {
  if (reviews >= 10 && rating !== null && rating >= 4.5) return 'A';
  if (reviews >= 3 && rating !== null && rating >= 4.0) return 'B';
  return 'C';
}

function mention_(rating, reviews) {
  if (!reviews || rating === null) return 'No Google reviews yet, no website';
  var r = String(Math.round(rating * 10) / 10);
  var s = reviews === 1 ? 'review' : 'reviews';
  if (rating >= 4) return r + '★ from ' + reviews + ' Google ' + s + ', but no website';
  return 'Rated ' + r + '★ on Google (' + reviews + ' ' + s + ')';
}

function ukPhone_(raw) {
  if (!raw) return '';
  var p = String(raw).trim();
  if (p.indexOf('+44') === 0) p = '0' + p.slice(3).trim();
  p = p.replace(/[^\d ]/g, '').trim();
  if (p.indexOf(' ') === -1 && p.length === 11) p = p.slice(0, 5) + ' ' + p.slice(5);
  return p;
}

function digits_(s) { return String(s || '').replace(/\D/g, ''); }
function clean_(s) { return String(s || '').replace(/️/g, '').replace(/\s+/g, ' ').trim(); }
function titleCase_(s) { return String(s).replace(/\w\S*/g, function (w) { return w.charAt(0).toUpperCase() + w.slice(1); }); }
function round2_(n) { return Math.round(n * 100) / 100; }
