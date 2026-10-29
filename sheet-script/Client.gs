/**
 * Maystone – after the sale: details form link, publishing customer photos/details, own domain.
 *
 * Columns added to the Harvey/Fin tabs: AD Details, AE Domain, AF Live site, AG Form key.
 * - After a Stripe payment (Payments.gs) the customer is emailed a private link to the details form.
 *   Menu "Send details form" does the same by hand (e.g. if they paid by bank transfer).
 * - Every 5 minutes: any "Received" details (saved to Drive by the tracker web app) are pushed to
 *   GitHub (leads/<ID>/ photos + details in leads/<ID>.json), so the site rebuilds with them.
 * - Type the customer's web address in Domain (e.g. smithsplumbing.co.uk). Once they've paid, the
 *   site is published on its own address and you're emailed the DNS records to add.
 */

var FORM_URL = 'https://script.google.com/macros/s/AKfycbyHy9OQT8lM1U_xwEg2rpJqCG1PZApcAKPNbtpDUzI1Gw-Btro7IwNEr-GZwHxXf3Er/exec';
var UPLOAD_ROOT = 'Maystone client uploads';
var CX = { email: 11, paid: 19, details: 30, domain: 31, live: 32, key: 33 }; // K, S, AD, AE, AF, AG
var CX_HEADERS = ['Details', 'Domain', 'Live site', 'Form key'];
var PAGES_IPS = ['185.199.108.153', '185.199.109.153', '185.199.110.153', '185.199.111.153'];

function ensureClientHeaders_() {
  var ss = SpreadsheetApp.getActive();
  TABS.forEach(function (n) {
    var sh = ss.getSheetByName(n);
    if (!sh) return;
    if (sh.getMaxColumns() < CX.key) sh.insertColumnsAfter(sh.getMaxColumns(), CX.key - sh.getMaxColumns());
    var h = sh.getRange(1, CX.details, 1, 4);
    if (h.getValues()[0].join('') !== CX_HEADERS.join('')) {
      h.setValues([CX_HEADERS]).setFontWeight('bold');
      sh.getRange(1, CX.details, 1, 4).setBackground(sh.getRange(1, 1).getBackground());
    }
  });
}

/** Email the customer a private link to the details form. */
function sendDetailsLink_(sh, r, to) {
  to = String(to || sh.getRange(r, CX.email).getValue()).trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(to)) throw new Error('no valid customer email');
  var id = String(sh.getRange(r, 1).getValue()).trim();
  var key = String(sh.getRange(r, CX.key).getValue()).trim();
  if (!key) { key = Utilities.getUuid().replace(/-/g, '').slice(0, 16); sh.getRange(r, CX.key).setValue(key); }
  var link = FORM_URL + '?form=' + encodeURIComponent(id) + '&k=' + key;
  var biz = sh.getRange(r, 2).getValue();
  var body = 'Hi,\n\nThanks for your payment – we\'re getting your new website for ' + biz + ' ready.\n\n' +
    'Please send us your photos and a few details here (it takes about 5 minutes):\n' + link + '\n\n' +
    'Once we have them, your photos, logo and details go straight onto your site, and we\'ll set up your web address.\n\n' +
    'Any questions, just reply to this email.\n\nThanks,\n' + sh.getName() + '\nMaystone';
  GmailApp.sendEmail(to, 'Next step for your website – ' + biz, body, { from: SENDER, name: SENDER_NAME });
  if (!String(sh.getRange(r, CX.details).getValue()).trim()) sh.getRange(r, CX.details).setValue('Form sent ' + Utilities.formatDate(new Date(), 'Europe/London', 'dd/MM'));
}

/** Menu: send the details form to the customer on the selected row. */
function sendDetailsFormMenu() {
  var ui = SpreadsheetApp.getUi(), sh = SpreadsheetApp.getActiveSheet(), r = sh.getActiveRange().getRow();
  if (TABS.indexOf(sh.getName()) === -1 || r < 2) { ui.alert('Click a lead row on the Harvey or Fin tab first.'); return; }
  ensureClientHeaders_();
  try { sendDetailsLink_(sh, r); ui.alert('Details form sent to ' + sh.getRange(r, CX.email).getValue()); }
  catch (e) { ui.alert('Not sent: ' + e.message); }
}

/** Called from processAll every 5 minutes. */
function clientPoll_() {
  ensureClientHeaders_();
  var ss = SpreadsheetApp.getActive();
  TABS.forEach(function (n) {
    var sh = ss.getSheetByName(n);
    if (!sh) return;
    var last = lastIdRow_(sh);
    if (last < 2) return;
    var vals = sh.getRange(2, 1, last - 1, CX.key).getValues();
    vals.forEach(function (v, i) {
      var r = i + 2, id = String(v[0]).trim();
      if (!id) return;
      try {
        if (/^Received/.test(String(v[CX.details - 1]))) publishDetails_(sh, r, id);
        var domain = cleanDomain_(v[CX.domain - 1]);
        var paid = String(v[CX.paid - 1]).trim();
        var liveCell = String(v[CX.live - 1]);
        if (domain && paid && liveCell.indexOf(domain) === -1) setDomain_(sh, r, id, domain);
      } catch (e) {
        sh.getRange(r, CX.details).setNote('Problem: ' + e.message);
      }
    });
  });
}

function cleanDomain_(d) {
  return String(d || '').trim().toLowerCase().replace(/^https?:\/\//, '').replace(/^www\./, '').replace(/\/.*$/, '');
}

/** Push the customer's photos + answers from Drive to GitHub. */
function publishDetails_(sh, r, id) {
  var roots = DriveApp.getFoldersByName(UPLOAD_ROOT);
  if (!roots.hasNext()) return;
  var fs = roots.next().getFoldersByName(id);
  if (!fs.hasNext()) return;
  var folder = fs.next(), files = folder.getFiles(), details = null, n = 0;
  while (files.hasNext()) {
    var f = files.next();
    if (f.isTrashed()) continue;
    if (f.getName() === 'details.json') { details = JSON.parse(f.getBlob().getDataAsString()); continue; }
    if (!/^(logo|\d{1,2})\.(jpg|png|webp)$/.test(f.getName())) continue;
    ghPutFile_('leads/' + id + '/' + f.getName(), Utilities.base64Encode(f.getBlob().getBytes()), 'Photos: ' + id);
    n++;
  }
  if (details) {
    var path = 'repos/' + REPO + '/contents/leads/' + id + '.json';
    var cur = gh_('GET', path);
    if (cur.code !== 200) throw new Error('lead file not on GitHub');
    var data = JSON.parse(Utilities.newBlob(Utilities.base64Decode(cur.json.content.replace(/\n/g, ''))).getDataAsString('UTF-8'));
    data.details = { business: details.business, phone: details.phone, email: details.email,
                     creds_list: details.creds_list, company: details.company };
    var res = gh_('PUT', path, { message: 'Details: ' + id, sha: cur.json.sha,
      content: Utilities.base64Encode(JSON.stringify(data, null, 1), Utilities.Charset.UTF_8),
      committer: { name: 'Maystone sheet', email: 'hello@maystone.uk' } });
    if (res.code !== 200) throw new Error('GitHub ' + res.code);
  }
  sh.getRange(r, CX.details).setValue('Published ' + Utilities.formatDate(new Date(), 'Europe/London', 'dd/MM HH:mm') + ' – ' + n + ' file(s)');
}

function ghPutFile_(path, b64, message) {
  var api = 'repos/' + REPO + '/contents/' + path;
  var cur = gh_('GET', api);
  var body = { message: message, content: b64, committer: { name: 'Maystone sheet', email: 'hello@maystone.uk' } };
  if (cur.code === 200) {
    if (cur.json.content && cur.json.content.replace(/\n/g, '') === b64) return; // unchanged
    body.sha = cur.json.sha;
  }
  var res = gh_('PUT', api, body);
  if (res.code !== 200 && res.code !== 201) throw new Error('GitHub ' + res.code + ' on ' + path);
}

/** Put the domain in the lead file (GitHub Actions then publishes the site on it) and email the DNS steps. */
function setDomain_(sh, r, id, domain) {
  var path = 'repos/' + REPO + '/contents/leads/' + id + '.json';
  var cur = gh_('GET', path);
  if (cur.code !== 200) throw new Error('lead file not on GitHub');
  var data = JSON.parse(Utilities.newBlob(Utilities.base64Decode(cur.json.content.replace(/\n/g, ''))).getDataAsString('UTF-8'));
  data.domain = domain;
  data.live = true;
  var res = gh_('PUT', path, { message: 'Domain: ' + id + ' -> ' + domain, sha: cur.json.sha,
    content: Utilities.base64Encode(JSON.stringify(data, null, 1), Utilities.Charset.UTF_8),
    committer: { name: 'Maystone sheet', email: 'hello@maystone.uk' } });
  if (res.code !== 200) throw new Error('GitHub ' + res.code);
  sh.getRange(r, CX.live).setValue('Setting up: https://' + domain + ' (add DNS)');
  var biz = sh.getRange(r, 2).getValue();
  var owner = REPO.split('/')[0];
  notify_(sh.getName(), 'DNS TO ADD: ' + domain + ' for ' + biz,
    biz + '\'s site is being published on ' + domain + ' (ready in about 5 minutes).\n\n' +
    'In the DNS settings where ' + domain + ' is registered, add:\n\n' +
    PAGES_IPS.map(function (ip) { return '  A      @     ' + ip; }).join('\n') +
    '\n  CNAME  www   ' + owner + '.github.io\n\n' +
    'Delete any other A or AAAA records for @ first. It can take up to an hour to work, and the padlock (HTTPS) ' +
    'switches on by itself shortly after. When https://' + domain + ' shows their site, change the Live site cell to "Live: https://' + domain + '".');
}
