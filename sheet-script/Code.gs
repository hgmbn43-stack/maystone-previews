/**
 * Maystone – preview automation for the "Call Lists (Harvey & Fin)" sheet.
 *
 * Outcome = "yes" + Client email  -> publishes the lead to GitHub (leads/<ID>.json),
 *                                    GitHub Actions builds the page, link goes in Preview link.
 * Approved ticked                 -> once the page is live, emails the link to the client
 *                                    from hello@maystone.uk, then writes the date in Sent to client.
 *
 * Setup (once, signed in as harvey@maystone.uk): Maystone menu -> 1. Set GitHub key,
 * then 2. Switch on automation. Triggers run as whoever switched them on, so emails send
 * from that person's Gmail using the hello@maystone.uk alias.
 */

var REPO = 'hgmbn43-stack/maystone-previews';
var SITE = 'https://hgmbn43-stack.github.io/maystone-previews/';
var TABS = ['Harvey', 'Fin'];
var SENDER = 'hello@maystone.uk';
var SENDER_NAME = 'Maystone';
// 1-based column numbers
var C = { id: 1, biz: 2, trade: 3, town: 4, phone: 5, outcome: 10, email: 11, link: 13,
          approved: 14, sent: 15, rating: 21, reviews: 22, maps: 23 };
var WIDTH = 23; // A..W

function onOpen() {
  SpreadsheetApp.getUi().createMenu('Maystone')
    .addItem('1. Set GitHub key', 'setGitHubKey')
    .addItem('2. Switch on automation', 'switchOn')
    .addItem('3. Set Apify key', 'setApifyKey')
    .addItem('4. Switch on lead farmer', 'switchOnFarmer')
    .addItem('5. Set Stripe key', 'setStripeKey')
    .addItem('Send details form (selected row)', 'sendDetailsFormMenu')
    .addSeparator()
    .addItem('Farm leads now', 'farmNow')
    .addItem('Run now', 'processAll')
    .addToUi();
}

function setGitHubKey() {
  var ui = SpreadsheetApp.getUi();
  var r = ui.prompt('GitHub key', 'Paste the GitHub key (starts with github_pat_).', ui.ButtonSet.OK_CANCEL);
  if (r.getSelectedButton() !== ui.Button.OK) return;
  var key = r.getResponseText().trim();
  if (!/^(github_pat_|ghp_)/.test(key)) { ui.alert('That does not look like a GitHub key.'); return; }
  PropertiesService.getUserProperties().setProperty('GH_TOKEN', key);
  var res = gh_('GET', 'repos/' + REPO);
  ui.alert(res.code === 200 ? 'GitHub key saved and working.' : 'Key saved, but GitHub said ' + res.code + '. Check the key has access to maystone-previews.');
}

function switchOn() {
  var ui = SpreadsheetApp.getUi();
  if (GmailApp.getAliases().indexOf(SENDER) === -1) {
    ui.alert('This account cannot send as ' + SENDER + '. Open the sheet signed in as harvey@maystone.uk and try again.');
    return;
  }
  if (!PropertiesService.getUserProperties().getProperty('GH_TOKEN')) { ui.alert('Do step 1 (GitHub key) first.'); return; }
  ScriptApp.getProjectTriggers().forEach(function (t) { if (t.getHandlerFunction() !== 'farmDaily') ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('onEditRun').forSpreadsheet(SpreadsheetApp.getActive()).onEdit().create();
  ScriptApp.newTrigger('processAll').timeBased().everyMinutes(5).create();
  processAll();
  ui.alert('Automation is on. Emails will send from ' + SENDER + '.');
}

/** Installable on-edit trigger: react straight away to edits in Outcome, Client email or Approved. */
function onEditRun(e) {
  if (!e || !e.range) return;
  var sh = e.range.getSheet();
  if (TABS.indexOf(sh.getName()) === -1) return;
  var c1 = e.range.getColumn(), c2 = e.range.getLastColumn();
  var touches = [C.outcome, C.email, C.approved].some(function (c) { return c >= c1 && c <= c2; });
  if (!touches) return;
  withLock_(function () { processRows_(sh, Math.max(2, e.range.getRow()), e.range.getLastRow()); });
}

/** Every 5 minutes: catches anything missed and sends approved emails once pages are live. */
function processAll() {
  withLock_(function () {
    TABS.forEach(function (name) {
      var sh = SpreadsheetApp.getActive().getSheetByName(name);
      if (sh && sh.getLastRow() >= 2) processRows_(sh, 2, sh.getLastRow());
    });
    try { farmPoll_(); } catch (e) { console.error('farmPoll_: ' + e); }
    try { stripePoll_(); } catch (e) { console.error('stripePoll_: ' + e); }
    try { clientPoll_(); } catch (e) { console.error('clientPoll_: ' + e); }
  });
}

function processRows_(sh, first, last) {
  if (last < first) return;
  var range = sh.getRange(first, 1, last - first + 1, WIDTH);
  var rows = range.getValues();
  for (var i = 0; i < rows.length; i++) {
    var r = rows[i], rowNum = first + i;
    var id = String(r[C.id - 1]).trim();
    if (!id) continue;
    var email = String(r[C.email - 1]).trim();
    var link = String(r[C.link - 1]).trim();
    var okEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

    // 1. Publish preview
    if (/^yes/i.test(String(r[C.outcome - 1]).trim()) && okEmail && !link) {
      try {
        link = publish_(r);
        sh.getRange(rowNum, C.link).setValue(link);
      } catch (err) {
        sh.getRange(rowNum, C.link).setNote('Preview not published: ' + err.message);
        continue;
      }
    }

    // 2. Send once approved and live
    var approved = r[C.approved - 1] === true;
    var sent = String(r[C.sent - 1]).trim();
    if (approved && link && okEmail && !sent) {
      if (!isLive_(link)) continue; // page still building; the 5-minute run retries
      try {
        sendPreview_(email, String(r[C.biz - 1]).trim(), link, sh.getName());
        sh.getRange(rowNum, C.sent).setValue(Utilities.formatDate(new Date(), 'Europe/London', 'dd/MM/yyyy'));
      } catch (err) {
        sh.getRange(rowNum, C.sent).setNote('Not sent: ' + err.message);
      }
    }
  }
}

function publish_(r) {
  var id = String(r[C.id - 1]).trim().replace(/[^A-Za-z0-9_-]/g, '');
  var name = String(r[C.biz - 1]).replace(/\s+/g, ' ').trim().replace(/,+$/, '');
  if (!id || !name) throw new Error('missing Lead ID or business name');
  if (!String(r[C.phone - 1]).trim()) throw new Error('missing phone number');
  var data = {
    'Lead ID': id, 'Business': name, 'Trade': String(r[C.trade - 1]), 'Town': String(r[C.town - 1]),
    'Phone': String(r[C.phone - 1]), 'Google rating': String(r[C.rating - 1]),
    'Google reviews': String(r[C.reviews - 1]), 'Google Maps': String(r[C.maps - 1])
  };
  var path = 'repos/' + REPO + '/contents/leads/' + id + '.json';
  var existing = gh_('GET', path);
  var body = {
    message: 'Preview: ' + id,
    content: Utilities.base64Encode(JSON.stringify(data, null, 1), Utilities.Charset.UTF_8),
    committer: { name: 'Maystone sheet', email: 'hello@maystone.uk' }
  };
  if (existing.code === 200) body.sha = existing.json.sha;
  var res = gh_('PUT', path, body);
  if (res.code !== 200 && res.code !== 201) throw new Error('GitHub ' + res.code + ' ' + (res.json && res.json.message || ''));
  return SITE + 'p/' + id + '-' + slug_(name) + '/';
}

/** Must match engine/build_preview.py slugify(). */
function slug_(name) {
  var s = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  return s.slice(0, 40);
}

function isLive_(url) {
  try {
    return UrlFetchApp.fetch(url, { muteHttpExceptions: true, followRedirects: true }).getResponseCode() === 200;
  } catch (e) { return false; }
}

function sendPreview_(to, business, link, rep) {
  if (GmailApp.getAliases().indexOf(SENDER) === -1) throw new Error('cannot send as ' + SENDER);
  var body = 'Hi,\n\n' +
    'Thanks for speaking with us. Here\'s the preview of your new website for ' + business + ':\n' +
    link + '\n\n' +
    'It works on phones and computers. Photos, badges and a few bits of wording are placeholders – we swap in your own before it goes live.\n\n' +
    'When you\'re happy, you can pick a package and pay securely at the bottom of the page, and we\'ll get it live.\n\n' +
    'Have a look and reply to this email or give us a ring with any changes.\n\n' +
    'Thanks,\n' + rep + '\nMaystone';
  GmailApp.sendEmail(to, 'Your new website preview – ' + business, body, { from: SENDER, name: SENDER_NAME });
}

function gh_(method, path, payload) {
  var token = PropertiesService.getUserProperties().getProperty('GH_TOKEN');
  if (!token) throw new Error('no GitHub key set');
  var opts = {
    method: method, muteHttpExceptions: true,
    headers: { Authorization: 'Bearer ' + token, Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' }
  };
  if (payload) { opts.contentType = 'application/json'; opts.payload = JSON.stringify(payload); }
  var res = UrlFetchApp.fetch('https://api.github.com/' + path, opts);
  var json = null;
  try { json = JSON.parse(res.getContentText()); } catch (e) {}
  return { code: res.getResponseCode(), json: json };
}

function withLock_(fn) {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(30000)) return;
  try { fn(); } finally { lock.releaseLock(); }
}
