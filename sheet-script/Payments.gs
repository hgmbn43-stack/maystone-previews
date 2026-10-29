/**
 * Maystone – views, payments and go-live.
 *
 * Views: each preview page loads a tiny image from this script's web app (doGet ?v=<LeadID>).
 *   Only counted after the email has been sent (so your own checks don't count).
 *   First view: "Hot?" gets "Yes – <date>" and the rep gets an email to call now.
 * Payments: every 5 minutes (processAll) completed Stripe Checkout sessions are read.
 *   The pay buttons carry client_reference_id=<LeadID>, so the right row gets Package + Paid,
 *   the site is republished without the preview banner, and the rep + Harvey are emailed.
 *
 * Setup: Maystone menu -> 5. Set Stripe key (a restricted key with read access to Checkout Sessions).
 * Web app: Deploy > New deployment > Web app, execute as me, access Anyone.
 */

var REP_EMAILS = { Harvey: 'harvey@maystone.uk', Fin: 'fin.john@icloud.com' };
var OWNER_EMAIL = 'harvey@maystone.uk';
var CALLS_ID = '1QWrKee1Li45r1Zw2YcIV4XMSUyC-oFueAx4wWglWoEQ'; // this sheet (web app calls can't rely on getActive)
var C2 = { pkg: 18, paid: 19, views: 16, hot: 17 }; // R, S, P, Q

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
    notify_(sh.getName(), 'HOT LEAD: ' + biz + ' is looking at their preview now',
      biz + ' just opened their website preview.\n\nCall them now while it\'s on their screen: ' + phone + '\n\nLead ' + id + ' on the ' + sh.getName() + ' tab.');
  }
}

// ---------- payments ----------

function setStripeKey() {
  var ui = SpreadsheetApp.getUi();
  var r = ui.prompt('Stripe key', 'Paste a Stripe restricted key (starts rk_live_) with READ access to Checkout Sessions.', ui.ButtonSet.OK_CANCEL);
  if (r.getSelectedButton() !== ui.Button.OK) return;
  var key = r.getResponseText().trim();
  if (!/^(rk|sk)_(live|test)_/.test(key)) { ui.alert('That does not look like a Stripe key.'); return; }
  PropertiesService.getUserProperties().setProperty('STRIPE_KEY', key);
  var props = PropertiesService.getScriptProperties();
  if (!props.getProperty('STRIPE_SINCE')) props.setProperty('STRIPE_SINCE', String(Math.floor(Date.now() / 1000) - 86400));
  var res = stripe_('checkout/sessions?limit=1');
  ui.alert(res.code === 200 ? 'Stripe key saved and working.' : 'Key saved, but Stripe said ' + res.code + '. Check it can read Checkout Sessions.');
}

/** Called from processAll every 5 minutes. */
function stripePoll_() {
  if (!PropertiesService.getUserProperties().getProperty('STRIPE_KEY')) return;
  var props = PropertiesService.getScriptProperties();
  var since = Number(props.getProperty('STRIPE_SINCE') || Math.floor(Date.now() / 1000) - 86400);
  var res = stripe_('checkout/sessions?limit=50&status=complete&created[gt]=' + since);
  if (res.code !== 200) return;
  var newest = since;
  (res.json.data || []).forEach(function (s) {
    newest = Math.max(newest, s.created);
    if (s.payment_status !== 'paid' && s.payment_status !== 'no_payment_required') return;
    var id = String(s.client_reference_id || '').replace(/[^A-Za-z0-9_-]/g, '');
    var amount = '£' + (Number(s.amount_total || 0) / 100).toFixed(2).replace(/\.00$/, '');
    var who = (s.customer_details && (s.customer_details.name || s.customer_details.email)) || '';
    var hit = id ? findLead_(id) : null;
    if (!hit) {
      notify_(null, 'PAID (no lead matched): ' + amount,
        'A payment of ' + amount + ' from ' + who + ' came in without a lead ID. Match it up by hand in the sheet.');
      return;
    }
    var sh = hit.sheet, r = hit.row;
    if (String(sh.getRange(r, C2.paid).getValue()).trim()) return; // already recorded
    var pkg = s.mode === 'subscription' ? 'Care plan (£599 + £49/mo)' : 'Pay once (£500)';
    sh.getRange(r, C2.pkg).setValue(pkg);
    sh.getRange(r, C2.paid).setValue('Paid ' + amount + ' – ' + Utilities.formatDate(new Date(s.created * 1000), 'Europe/London', 'dd/MM/yyyy'));
    var biz = sh.getRange(r, C.biz).getValue();
    var liveNote = '';
    try { goLive_(id); liveNote = 'Their site is being switched to live (preview banner removed) – about 2 minutes.'; }
    catch (err) { liveNote = 'Could not switch the site to live automatically: ' + err.message; }
    try { ensureClientHeaders_(); sendDetailsLink_(sh, r, s.customer_details && s.customer_details.email); liveNote += '\nThey\'ve been emailed the form to send their photos and details.'; }
    catch (err) { liveNote += '\nCould not email them the details form: ' + err.message + ' (use Maystone > Send details form).'; }
    notify_(sh.getName(), 'PAID: ' + biz + ' just paid ' + amount,
      biz + ' paid ' + amount + ' for ' + pkg + '.\n\n' + liveNote +
      '\n\nNext: get their photos, logo and any wording changes, and book the day-2 check-in call.');
  });
  props.setProperty('STRIPE_SINCE', String(newest));
}

/** Mark leads/<id>.json as live so GitHub Actions rebuilds it without the preview banner/noindex/pay section. */
function goLive_(id) {
  var path = 'repos/' + REPO + '/contents/leads/' + id + '.json';
  var cur = gh_('GET', path);
  if (cur.code !== 200) throw new Error('lead file not found on GitHub');
  var data = JSON.parse(Utilities.newBlob(Utilities.base64Decode(cur.json.content.replace(/\n/g, ''))).getDataAsString('UTF-8'));
  if (data.live) return;
  data.live = true;
  var res = gh_('PUT', path, {
    message: 'Live: ' + id, sha: cur.json.sha,
    content: Utilities.base64Encode(JSON.stringify(data, null, 1), Utilities.Charset.UTF_8),
    committer: { name: 'Maystone sheet', email: 'hello@maystone.uk' }
  });
  if (res.code !== 200) throw new Error('GitHub ' + res.code);
}

// ---------- helpers ----------

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

function stripe_(path) {
  var key = PropertiesService.getUserProperties().getProperty('STRIPE_KEY');
  var res = UrlFetchApp.fetch('https://api.stripe.com/v1/' + path, { muteHttpExceptions: true, headers: { Authorization: 'Bearer ' + key } });
  var json = null;
  try { json = JSON.parse(res.getContentText()); } catch (e) {}
  return { code: res.getResponseCode(), json: json };
}
