(() => {
  'use strict';

  // ------------------------------------------------------------------ language
  const TEXT = {
    en: {
      brand: 'RAS Staff Portal', sign_in: 'Sign in', username: 'Username', password: 'Password',
      sign_out: 'Sign out', lang_switch: 'عربي',
      nav_overview: 'Overview', nav_home: 'My day', nav_sites: 'Sites', nav_requests: 'Material requests',
      nav_team: 'Team', nav_logs: 'Daily logs', nav_alerts: 'Alerts',
      hello: 'Hello, {0}', reminders: 'Needs your attention', all_clear: 'Nothing waiting. You are up to date.',
      r_overdue: '{0} overdue task(s)', r_due_today: '{0} task(s) due today',
      r_carried: '{0} task(s) carried over from earlier days', r_log_missing: 'You have not logged today\'s work yet',
      r_my_pending: '{0} of your request(s) waiting for approval', r_to_receive: '{0} order(s) on the way: confirm when received',
      r_approvals: '{0} request(s) waiting for your approval', r_to_order: '{0} approved request(s) to order',
      my_tasks: 'My tasks', no_tasks: 'No open tasks.', add_task: 'Add task', task_title: 'What needs doing?',
      due_date: 'Due date', site: 'Site', no_site: 'No site', general: 'General (no site)', high_priority: 'High priority',
      assign_to: 'Assign to', assigned_by: 'from {0}', overdue_by: 'Overdue {0}d', due_today: 'Due today', due_on: 'Due {0}',
      high: 'High', done_on: 'Done', delete: 'Delete', edit: 'Edit', save: 'Save', cancel: 'Cancel', add: 'Add',
      todays_work: 'Today\'s work', log_placeholder: 'What did you do today? Work done, quantities, problems…',
      log_save: 'Save to today\'s log', no_logs_today: 'Nothing logged today yet.', edited: 'edited',
      my_sites: 'My sites', no_sites: 'No sites assigned to you yet. Ask management to add you to your sites.',
      open_tasks_n: '{0} open tasks', open_requests_n: '{0} open requests', members_n: '{0} people',
      request_materials: 'Request materials', my_requests: 'My recent requests', no_requests: 'No requests yet.',
      all_requests: 'See all requests', new_request: 'New request', requests_title: 'Material requests',
      f_all: 'All', st_pending: 'Waiting approval', st_approved: 'Approved', st_rejected: 'Rejected',
      st_ordered: 'Ordered', st_delivered: 'Received', st_cancelled: 'Cancelled', urgent: 'Urgent',
      needed_by: 'Needed by', requested_by: 'Requested by', material: 'Material', spec: 'Size / spec', qty: 'Qty',
      unit: 'Unit', add_item: 'Add another item', remove: 'Remove', note: 'Note', note_optional: 'Note (optional)',
      send_request: 'Send request for approval', items: 'Items', history: 'History',
      a_approve: 'Approve', a_reject: 'Reject', a_order: 'Mark as ordered', a_deliver: 'Confirm received',
      a_cancel: 'Cancel request', action_note: 'Reason, supplier or LPO number', review: 'Open',
      ev_create: 'Requested', ev_approve: 'Approved', ev_reject: 'Rejected', ev_order: 'Ordered',
      ev_deliver: 'Received', ev_cancel: 'Cancelled',
      sites_title: 'Sites', add_site: 'Add a site', code: 'Short code', name: 'Name', location: 'Location',
      inactive: 'Closed', people: 'People on this site', no_members: 'Nobody assigned yet.', save_members: 'Save people',
      close_site: 'Close site', reopen_site: 'Reopen site', site_tasks: 'Open tasks on this site',
      site_requests: 'Requests for this site', site_logs: 'Recent work logged here', nothing_here: 'Nothing here yet.',
      overview_title: 'Team overview', s_open: 'Open tasks', s_overdue: 'Overdue', s_logged: 'Logged today',
      s_pending: 'Waiting approval', s_approved: 'To order', s_ordered: 'On the way',
      approvals: 'Requests waiting for approval', no_approvals: 'No requests waiting.',
      tracker: 'Everyone\'s tracker', employee: 'Employee', c_open: 'Open', c_overdue: 'Overdue', c_done: 'Done (7d)',
      c_log: 'Log today', c_requests: 'Requests', yes: 'Yes', not_yet: 'Not yet', last_log: 'last {0}',
      activity: 'Latest activity', no_activity: 'No activity yet.',
      back_overview: 'Back to overview', assign_task: 'Assign a task', open_tasks: 'Open tasks',
      done_recent: 'Completed in the last 14 days', logs_recent: 'Work log, last 14 days', their_requests: 'Their requests',
      team_title: 'Team accounts', add_user: 'Add an employee', full_name: 'Full name', job_title: 'Job title',
      role: 'Role', role_employee: 'Employee', role_procurement: 'Procurement', role_management: 'Management',
      temp_password: 'Temporary password (8+ characters)', new_temp_password: 'New temporary password (leave empty to keep)',
      username_hint: 'Lowercase letters, numbers, dot or dash', sites_access: 'Sites', active: 'Active',
      disabled: 'Disabled', create_user: 'Create account', user_created: 'Account created. Give them the username and temporary password.',
      saved: 'Saved', logs_title: 'Daily logs', day: 'Day', missing_logs: 'No log from', everyone_logged: 'Everyone has logged.',
      no_logs_day: 'No logs for this day.', alerts_title: 'Alerts', no_alerts: 'No alerts.',
      change_password: 'Change password', must_change: 'Choose your own password to continue',
      current_password: 'Current password', new_password: 'New password (8+ characters)', repeat_password: 'Repeat new password',
      password_changed: 'Password changed', passwords_differ: 'The two new passwords are not the same',
      act_task_assigned: '{name} assigned you a task: {title}', feed_task_assigned: '{name} assigned a task: {title}', act_task_done: '{name} completed: {title}',
      act_task_reopened: '{name} reopened: {title}', act_log_added: '{name} logged work: {text}',
      act_request_new: '{name} requested materials for {site} ({ref})', act_request_approve: '{name} approved {ref} for {site}',
      act_request_reject: '{name} rejected {ref}: {note}', act_request_order: '{name} ordered {ref} for {site}',
      act_request_deliver: '{name} confirmed {ref} was received', act_request_cancel: '{name} cancelled {ref}',
      err_wrong_login: 'Wrong username or password', err_too_many_attempts: 'Too many attempts. Try again in 10 minutes.',
      err_wrong_current_password: 'The current password is wrong', err_same_password: 'Choose a different password',
      err_username_taken: 'That username is already used', err_code_taken: 'That site code is already used',
      err_reason_required: 'Write the reason for rejecting', err_already_changed: 'Someone else just updated this request',
      err_not_your_site: 'You are not assigned to this site', err_last_manager: 'There must be at least one management account',
      err_cannot_demote_self: 'You cannot remove your own management access', err_day_closed: 'Only today\'s entries can be changed',
      err_invalid_input: 'Check the form: something is missing or too short', err_generic: 'Something went wrong. Try again.',
      err_network: 'No connection to the server',
    },
    ar: {
      brand: 'بوابة موظفي RAS', sign_in: 'تسجيل الدخول', username: 'اسم المستخدم', password: 'كلمة السر',
      sign_out: 'خروج', lang_switch: 'English',
      nav_overview: 'نظرة عامة', nav_home: 'يومي', nav_sites: 'المواقع', nav_requests: 'طلبات المواد',
      nav_team: 'الفريق', nav_logs: 'السجل اليومي', nav_alerts: 'التنبيهات',
      hello: 'أهلاً {0}', reminders: 'بحاجة لانتباهك', all_clear: 'ما في شي متراكم عليك.',
      r_overdue: '{0} مهمة متأخرة', r_due_today: '{0} مهمة موعدها اليوم',
      r_carried: '{0} مهمة متراكمة من أيام سابقة', r_log_missing: 'لسا ما سجّلت شغل اليوم',
      r_my_pending: '{0} من طلباتك بانتظار الموافقة', r_to_receive: '{0} طلب بالطريق: أكّد لما يوصل',
      r_approvals: '{0} طلب بانتظار موافقتك', r_to_order: '{0} طلب موافق عليه بانتظار الشراء',
      my_tasks: 'مهامي', no_tasks: 'ما في مهام مفتوحة.', add_task: 'إضافة مهمة', task_title: 'شو المطلوب؟',
      due_date: 'الموعد', site: 'الموقع', no_site: 'بدون موقع', general: 'عام (بدون موقع)', high_priority: 'أولوية عالية',
      assign_to: 'إسناد إلى', assigned_by: 'من {0}', overdue_by: 'متأخرة {0} يوم', due_today: 'اليوم', due_on: 'الموعد {0}',
      high: 'عالية', done_on: 'تمت', delete: 'حذف', edit: 'تعديل', save: 'حفظ', cancel: 'إلغاء', add: 'إضافة',
      todays_work: 'شغل اليوم', log_placeholder: 'شو اشتغلت اليوم؟ الأعمال المنجزة، الكميات، المشاكل…',
      log_save: 'حفظ بسجل اليوم', no_logs_today: 'ما في شي مسجّل اليوم.', edited: 'معدّل',
      my_sites: 'مواقعي', no_sites: 'ما في مواقع مسندة إلك. اطلب من الإدارة تضيفك على مواقعك.',
      open_tasks_n: '{0} مهمة مفتوحة', open_requests_n: '{0} طلب مفتوح', members_n: '{0} أشخاص',
      request_materials: 'طلب مواد', my_requests: 'آخر طلباتي', no_requests: 'ما في طلبات.',
      all_requests: 'كل الطلبات', new_request: 'طلب جديد', requests_title: 'طلبات المواد',
      f_all: 'الكل', st_pending: 'بانتظار الموافقة', st_approved: 'موافق عليه', st_rejected: 'مرفوض',
      st_ordered: 'تم الطلب', st_delivered: 'تم الاستلام', st_cancelled: 'ملغي', urgent: 'عاجل',
      needed_by: 'مطلوب بتاريخ', requested_by: 'صاحب الطلب', material: 'المادة', spec: 'المقاس / المواصفة', qty: 'الكمية',
      unit: 'الوحدة', add_item: 'إضافة مادة', remove: 'حذف', note: 'ملاحظة', note_optional: 'ملاحظة (اختياري)',
      send_request: 'إرسال الطلب للموافقة', items: 'المواد', history: 'سجل الطلب',
      a_approve: 'موافقة', a_reject: 'رفض', a_order: 'تم الطلب من المورد', a_deliver: 'تأكيد الاستلام',
      a_cancel: 'إلغاء الطلب', action_note: 'السبب، أو المورد، أو رقم LPO', review: 'فتح',
      ev_create: 'تم الطلب', ev_approve: 'تمت الموافقة', ev_reject: 'تم الرفض', ev_order: 'تم الطلب من المورد',
      ev_deliver: 'تم الاستلام', ev_cancel: 'تم الإلغاء',
      sites_title: 'المواقع', add_site: 'إضافة موقع', code: 'رمز قصير', name: 'الاسم', location: 'المكان',
      inactive: 'مغلق', people: 'العاملون بالموقع', no_members: 'ما في حدا مسند.', save_members: 'حفظ',
      close_site: 'إغلاق الموقع', reopen_site: 'إعادة فتح الموقع', site_tasks: 'المهام المفتوحة بالموقع',
      site_requests: 'طلبات الموقع', site_logs: 'آخر شغل مسجّل هون', nothing_here: 'ما في شي لسا.',
      overview_title: 'نظرة عامة على الفريق', s_open: 'مهام مفتوحة', s_overdue: 'متأخرة', s_logged: 'سجّلوا اليوم',
      s_pending: 'بانتظار الموافقة', s_approved: 'بانتظار الشراء', s_ordered: 'بالطريق',
      approvals: 'طلبات بانتظار الموافقة', no_approvals: 'ما في طلبات بالانتظار.',
      tracker: 'متابعة كل موظف', employee: 'الموظف', c_open: 'مفتوحة', c_overdue: 'متأخرة', c_done: 'منجزة (7 أيام)',
      c_log: 'سجل اليوم', c_requests: 'طلبات', yes: 'نعم', not_yet: 'لسا', last_log: 'آخر مرة {0}',
      activity: 'آخر النشاطات', no_activity: 'ما في نشاط لسا.',
      back_overview: 'رجوع للنظرة العامة', assign_task: 'إسناد مهمة', open_tasks: 'المهام المفتوحة',
      done_recent: 'منجزة بآخر 14 يوم', logs_recent: 'سجل الشغل، آخر 14 يوم', their_requests: 'طلباته',
      team_title: 'حسابات الفريق', add_user: 'إضافة موظف', full_name: 'الاسم الكامل', job_title: 'المسمى الوظيفي',
      role: 'الصلاحية', role_employee: 'موظف', role_procurement: 'مشتريات', role_management: 'إدارة',
      temp_password: 'كلمة سر مؤقتة (8 أحرف أو أكثر)', new_temp_password: 'كلمة سر مؤقتة جديدة (اتركها فاضية لتبقى)',
      username_hint: 'أحرف إنجليزية صغيرة وأرقام ونقطة أو شرطة', sites_access: 'المواقع', active: 'فعّال',
      disabled: 'موقوف', create_user: 'إنشاء الحساب', user_created: 'تم إنشاء الحساب. أعطِ الموظف اسم المستخدم وكلمة السر المؤقتة.',
      saved: 'تم الحفظ', logs_title: 'السجل اليومي', day: 'اليوم', missing_logs: 'ما سجّلوا', everyone_logged: 'الكل سجّل.',
      no_logs_day: 'ما في سجلات لهاليوم.', alerts_title: 'التنبيهات', no_alerts: 'ما في تنبيهات.',
      change_password: 'تغيير كلمة السر', must_change: 'اختار كلمة سر خاصة فيك لتكمل',
      current_password: 'كلمة السر الحالية', new_password: 'كلمة السر الجديدة (8 أحرف أو أكثر)', repeat_password: 'أعد كتابة كلمة السر الجديدة',
      password_changed: 'تم تغيير كلمة السر', passwords_differ: 'كلمتا السر الجديدتان غير متطابقتين',
      act_task_assigned: '{name} أسند إلك مهمة: {title}', feed_task_assigned: '{name} أسند مهمة: {title}', act_task_done: '{name} أنجز: {title}',
      act_task_reopened: '{name} أعاد فتح: {title}', act_log_added: '{name} سجّل شغل: {text}',
      act_request_new: '{name} طلب مواد لموقع {site} ({ref})', act_request_approve: '{name} وافق على {ref} لموقع {site}',
      act_request_reject: '{name} رفض {ref}: {note}', act_request_order: '{name} طلب {ref} من المورد لموقع {site}',
      act_request_deliver: '{name} أكّد استلام {ref}', act_request_cancel: '{name} ألغى {ref}',
      err_wrong_login: 'اسم المستخدم أو كلمة السر غلط', err_too_many_attempts: 'محاولات كتير. جرّب بعد 10 دقايق.',
      err_wrong_current_password: 'كلمة السر الحالية غلط', err_same_password: 'اختار كلمة سر مختلفة',
      err_username_taken: 'اسم المستخدم مستعمل', err_code_taken: 'رمز الموقع مستعمل',
      err_reason_required: 'اكتب سبب الرفض', err_already_changed: 'حدا تاني عدّل هالطلب هلّق',
      err_not_your_site: 'إنت مش مسند لهالموقع', err_last_manager: 'لازم يضل حساب إدارة واحد على الأقل',
      err_cannot_demote_self: 'ما بتقدر تشيل صلاحية الإدارة عن حالك', err_day_closed: 'بس سجلات اليوم بتتعدل',
      err_invalid_input: 'راجع النموذج: في شي ناقص أو قصير', err_generic: 'صار خطأ. جرّب مرة تانية.',
      err_network: 'ما في اتصال بالخادم',
    },
  };

  const store = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch { /* private mode */ } },
  };
  let lang = store.get('lang') === 'ar' ? 'ar' : 'en';
  const t = (key, ...args) => {
    let s = TEXT[lang][key] ?? TEXT.en[key] ?? key;
    args.forEach((a, i) => { s = s.replace(`{${i}}`, a); });
    return s;
  };
  const fill = (key, data) => t(key).replace(/\{(\w+)\}/g, (_, k) => data[k] ?? '');
  const errText = (e) => (TEXT.en['err_' + e.code] ? t('err_' + e.code) : t(e.code === 'network' ? 'err_network' : 'err_generic'));

  // ------------------------------------------------------------------ helpers
  const state = { me: null, rev: null, unread: 0, route: '', stale: false, draft: '' };

  function h(tag, attrs, ...kids) {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v == null || v === false || k === 'value') continue;
      if (k === 'class') el.className = v;
      else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v === true ? '' : v);
    }
    for (const kid of kids.flat(Infinity)) {
      if (kid != null && kid !== false) el.append(kid.nodeType ? kid : String(kid));
    }
    if (attrs && attrs.value != null) el.value = attrs.value;
    return el;
  }

  async function api(method, path, body) {
    let res;
    try {
      res = await fetch('/api' + path, {
        method, credentials: 'same-origin',
        headers: { 'X-Requested-With': 'portal', ...(body ? { 'Content-Type': 'application/json' } : {}) },
        body: body ? JSON.stringify(body) : undefined,
      });
    } catch { throw Object.assign(new Error('network'), { code: 'network' }); }
    const data = await res.json().catch(() => ({}));
    if (res.status === 401 && path !== '/login') {
      state.me = null;
      render();
      throw Object.assign(new Error('signed_out'), { code: 'signed_out' });
    }
    if (!res.ok) {
      const code = typeof data.detail === 'string' ? data.detail : 'invalid_input';
      throw Object.assign(new Error(code), { code });
    }
    return data;
  }

  let toastTimer;
  function toast(text, bad) {
    const el = document.getElementById('toast');
    el.textContent = text;
    el.className = 'toast show' + (bad ? ' bad' : '');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { el.className = 'toast'; }, 4000);
  }

  // Run a change, then redraw. Errors show as a toast and leave the form as it was.
  async function act(fn, okText) {
    try {
      await fn();
      if (okText) toast(okText);
      await render(true);
    } catch (e) {
      if (e.code !== 'signed_out') toast(errText(e), true);
    }
  }

  function form(onSubmit, attrs, ...kids) {
    const el = h('form', attrs, ...kids);
    el.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      const button = el.querySelector('button[type=submit]');
      if (button) button.disabled = true;
      try { await onSubmit(el); } finally { if (button) button.disabled = false; }
    });
    return el;
  }
  const val = (formEl, name) => (formEl.elements[name]?.value ?? '').trim();
  const field = (label, control) => h('label', { class: 'field' }, h('span', null, label), control);

  const dateFmt = () => new Intl.DateTimeFormat(lang === 'ar' ? 'ar' : 'en-GB', { day: 'numeric', month: 'short' });
  const fmtDate = (iso) => (iso ? dateFmt().format(new Date(iso.slice(0, 10) + 'T12:00:00')) : '');
  const fmtTime = (iso) => (iso ? iso.slice(11, 16) : '');
  const fmtWhen = (iso) => `${fmtDate(iso)} ${fmtTime(iso)}`;
  const daysBetween = (a, b) => Math.round((new Date(b + 'T12:00:00') - new Date(a + 'T12:00:00')) / 864e5);
  const num = (n) => (n == null ? '' : String(Math.round(n * 100) / 100));
  const isBoss = () => state.me.role === 'management';

  const section = (title, ...kids) => h('section', { class: 'card' }, title && h('h2', null, title), ...kids);
  const empty = (text) => h('p', { class: 'muted' }, text);
  const pill = (status) => h('span', { class: 'pill st-' + status }, t('st_' + status));

  function siteSelect(sites, selected, emptyLabel) {
    return h('select', { name: 'site_id', value: selected ?? '' },
      emptyLabel && h('option', { value: '' }, emptyLabel),
      sites.map((s) => h('option', { value: s.id }, s.name)));
  }

  // ------------------------------------------------------------------ tasks
  function taskList(tasks, today, opts = {}) {
    if (!tasks.length) return empty(t('no_tasks'));
    return h('ul', { class: 'tasks' }, tasks.map((task) => {
      const done = task.status === 'done';
      const id = 'task-' + task.id;
      const canDelete = isBoss() || task.created_by === state.me.id;
      let due = null;
      if (!done && task.due_date) {
        if (task.overdue) due = h('span', { class: 'tag bad' }, t('overdue_by', daysBetween(task.due_date, today)));
        else if (task.due_date === today) due = h('span', { class: 'tag warn' }, t('due_today'));
        else due = h('span', { class: 'tag' }, t('due_on', fmtDate(task.due_date)));
      }
      return h('li', { class: 'task' + (done ? ' done' : '') + (task.overdue ? ' overdue' : '') },
        h('input', {
          type: 'checkbox', id, checked: done,
          onchange: (ev) => act(() => api('PATCH', '/tasks/' + task.id, { status: ev.target.checked ? 'done' : 'open' })),
        }),
        h('div', { class: 'task-body' },
          h('label', { for: id }, task.title),
          h('div', { class: 'meta' },
            due,
            !done && task.priority === 'high' && h('span', { class: 'tag warn' }, t('high')),
            done && h('span', { class: 'tag good' }, `${t('done_on')} ${fmtDate(task.done_at)}`),
            opts.showAssignee && h('span', null, task.assignee_name),
            task.site_name && h('span', null, task.site_name),
            task.created_by !== task.assigned_to && h('span', null, t('assigned_by', task.creator_name)))),
        canDelete && h('button', {
          type: 'button', class: 'link small', 'aria-label': `${t('delete')}: ${task.title}`,
          onclick: () => act(() => api('DELETE', '/tasks/' + task.id)),
        }, t('delete')));
    }));
  }

  function taskForm({ sites, assignees, assignee, site }) {
    return form(async (f) => {
      await act(() => api('POST', '/tasks', {
        title: val(f, 'title'),
        due_date: val(f, 'due_date') || null,
        site_id: Number(val(f, 'site_id')) || site || null,
        assigned_to: Number(val(f, 'assigned_to')) || assignee || null,
        priority: f.elements.high.checked ? 'high' : 'normal',
      }));
    }, { class: 'inline-form' },
    h('input', { name: 'title', required: true, maxlength: 200, placeholder: t('task_title'), 'aria-label': t('task_title') }),
    assignees && h('select', { name: 'assigned_to', required: true, 'aria-label': t('assign_to') },
      h('option', { value: '' }, t('assign_to')), assignees.map((u) => h('option', { value: u.id }, u.name))),
    !site && sites.length > 0 && siteSelect(sites, '', t('no_site')),
    h('input', { name: 'due_date', type: 'date', 'aria-label': t('due_date') }),
    h('label', { class: 'check' }, h('input', { type: 'checkbox', name: 'high' }), t('high_priority')),
    h('button', { type: 'submit', class: 'btn' }, t('add')));
  }

  // ------------------------------------------------------------------ requests
  const itemsSummary = (r) => {
    const parts = r.items.slice(0, 2).map((i) => i.material + (i.qty ? ` × ${num(i.qty)} ${i.unit}` : ''));
    return parts.join(', ') + (r.items.length > 2 ? ` +${r.items.length - 2}` : '');
  };

  function requestList(requests) {
    if (!requests.length) return empty(t('no_requests'));
    return h('ul', { class: 'rows' }, requests.map((r) => h('li', null,
      h('a', { href: '#/request/' + r.id, class: 'row' },
        h('span', { class: 'mono' }, r.ref),
        h('span', { class: 'row-main' }, h('strong', null, r.site_name), h('span', { class: 'muted' }, itemsSummary(r))),
        h('span', { class: 'row-end' },
          r.urgent && ['pending', 'approved'].includes(r.status) && h('span', { class: 'tag bad' }, t('urgent')),
          pill(r.status),
          h('span', { class: 'muted small' }, `${r.requester_name} · ${fmtDate(r.created_at)}`))))));
  }

  // ------------------------------------------------------------------ views
  function loginView() {
    return h('main', { class: 'auth' },
      h('h1', null, t('brand')),
      form(async (f) => {
        try {
          state.me = await api('POST', '/login', { username: val(f, 'username'), password: f.elements.password.value });
          location.hash = '';
          await render();
        } catch (e) { toast(errText(e), true); }
      }, { class: 'card stack' },
      field(t('username'), h('input', { name: 'username', required: true, autocomplete: 'username', autocapitalize: 'none', autofocus: true })),
      field(t('password'), h('input', { name: 'password', type: 'password', required: true, autocomplete: 'current-password' })),
      h('button', { type: 'submit', class: 'btn wide' }, t('sign_in'))),
      h('button', { type: 'button', class: 'link', onclick: switchLang }, t('lang_switch')));
  }

  function passwordForm() {
    return form(async (f) => {
      if (f.elements.new.value !== f.elements.repeat.value) return toast(t('passwords_differ'), true);
      try {
        await api('POST', '/password', { current: f.elements.current.value, new: f.elements.new.value });
        state.me.must_change_password = 0;
        toast(t('password_changed'));
        location.hash = '';
        await render();
      } catch (e) { if (e.code !== 'signed_out') toast(errText(e), true); }
    }, { class: 'card stack' },
    field(t('current_password'), h('input', { name: 'current', type: 'password', required: true, autocomplete: 'current-password' })),
    field(t('new_password'), h('input', { name: 'new', type: 'password', required: true, minlength: 8, autocomplete: 'new-password' })),
    field(t('repeat_password'), h('input', { name: 'repeat', type: 'password', required: true, minlength: 8, autocomplete: 'new-password' })),
    h('button', { type: 'submit', class: 'btn wide' }, t('change_password')));
  }

  async function homeView() {
    const d = await api('GET', '/home');
    const r = d.reminders;
    const reminders = [
      r.overdue && ['bad', t('r_overdue', r.overdue)],
      r.due_today && ['warn', t('r_due_today', r.due_today)],
      r.carried_over && ['warn', t('r_carried', r.carried_over)],
      r.log_missing && ['warn', t('r_log_missing')],
      r.approvals_waiting && ['bad', t('r_approvals', r.approvals_waiting), '#/overview'],
      r.to_order && ['bad', t('r_to_order', r.to_order), '#/requests'],
      r.to_receive && ['warn', t('r_to_receive', r.to_receive), '#/requests'],
      r.my_pending_requests && ['', t('r_my_pending', r.my_pending_requests), '#/requests'],
    ].filter(Boolean);

    const logEntry = (log) => {
      const li = h('li', { class: 'log' });
      const show = () => li.replaceChildren(
        h('p', null, log.text),
        h('div', { class: 'meta' },
          h('span', null, log.site_name || t('general')), h('span', null, fmtTime(log.created_at)),
          log.updated_at && h('span', null, t('edited')),
          h('button', { type: 'button', class: 'link small', onclick: edit }, t('edit')),
          h('button', { type: 'button', class: 'link small', onclick: () => act(() => api('DELETE', '/logs/' + log.id)) }, t('delete'))));
      const edit = () => li.replaceChildren(form(async (f) => {
        await act(() => api('PUT', '/logs/' + log.id, { text: val(f, 'text'), site_id: Number(val(f, 'site_id')) || null }));
      }, { class: 'stack' },
      siteSelect(d.sites, log.site_id, t('general')),
      h('textarea', { name: 'text', required: true, rows: 3, maxlength: 4000, 'aria-label': t('todays_work') }, log.text),
      h('div', { class: 'actions' }, h('button', { type: 'submit', class: 'btn' }, t('save')),
        h('button', { type: 'button', class: 'btn ghost', onclick: show }, t('cancel')))));
      show();
      return li;
    };

    return [
      h('div', { class: 'page-head' }, h('h1', null, t('hello', state.me.name)), h('span', { class: 'muted' }, fmtDate(d.today))),
      section(t('reminders'), reminders.length
        ? h('ul', { class: 'reminders' }, reminders.map(([cls, text, href]) => h('li', { class: cls },
          href ? h('a', { href }, text) : text)))
        : empty(t('all_clear'))),
      section(t('my_tasks'), taskForm({ sites: d.sites }), taskList(d.tasks, d.today)),
      section(t('todays_work'),
        form(async (f) => {
          await act(async () => {
            await api('POST', '/logs', { text: val(f, 'text'), site_id: Number(val(f, 'site_id')) || null });
            state.draft = '';
          });
        }, { class: 'stack' },
        d.sites.length > 0 && siteSelect(d.sites, d.sites.length === 1 ? d.sites[0].id : '', t('general')),
        h('textarea', {
          name: 'text', required: true, rows: 3, maxlength: 4000, placeholder: t('log_placeholder'), 'aria-label': t('todays_work'),
          oninput: (ev) => { state.draft = ev.target.value; },
        }, state.draft),
        h('div', { class: 'actions' }, h('button', { type: 'submit', class: 'btn' }, t('log_save')))),
        d.logs.length ? h('ul', { class: 'logs' }, d.logs.map(logEntry)) : empty(t('no_logs_today'))),
      section(t('my_sites'), d.sites.length ? siteCards(d.sites) : empty(t('no_sites'))),
      section(t('my_requests'), requestList(d.requests),
        h('div', { class: 'actions' }, h('a', { href: '#/requests', class: 'btn ghost' }, t('all_requests')),
          d.sites.length > 0 && h('a', { href: '#/new-request', class: 'btn' }, t('new_request')))),
    ];
  }

  function siteCards(sites) {
    return h('div', { class: 'grid' }, sites.map((s) => h('div', { class: 'site' + (s.active ? '' : ' closed') },
      h('a', { href: '#/site/' + s.id, class: 'site-name' }, s.name),
      h('span', { class: 'muted small' }, [s.code, s.location, !s.active && t('inactive')].filter(Boolean).join(' · ')),
      h('span', { class: 'small' }, [t('open_tasks_n', s.open_tasks), t('open_requests_n', s.open_requests),
        t('members_n', s.members)].join(' · ')),
      s.active && h('a', { href: '#/new-request/' + s.id, class: 'btn ghost small' }, t('request_materials')))));
  }

  async function requestsView(filter) {
    const all = await api('GET', '/requests');
    const filters = ['all', 'pending', 'approved', 'ordered', 'delivered', 'rejected'];
    const current = filters.includes(filter) ? filter : 'all';
    const shown = current === 'all' ? all : all.filter((r) => r.status === current);
    return [
      h('div', { class: 'page-head' }, h('h1', null, t('requests_title')),
        h('a', { href: '#/new-request', class: 'btn' }, t('new_request'))),
      h('nav', { class: 'filters', 'aria-label': t('requests_title') }, filters.map((f) => h('a', {
        href: '#/requests/' + f, class: f === current ? 'on' : '', 'aria-current': f === current ? 'page' : null,
      }, `${t(f === 'all' ? 'f_all' : 'st_' + f)} (${f === 'all' ? all.length : all.filter((r) => r.status === f).length})`))),
      section(null, requestList(shown)),
    ];
  }

  async function requestView(id) {
    const r = await api('GET', '/requests/' + id);
    const needsNote = r.actions.some((a) => ['reject', 'order', 'approve'].includes(a));
    const note = h('input', { name: 'note', maxlength: 500, placeholder: t('action_note'), 'aria-label': t('action_note') });
    const classes = { approve: 'btn', order: 'btn', deliver: 'btn', reject: 'btn danger', cancel: 'btn ghost' };
    return [
      h('div', { class: 'page-head' },
        h('h1', null, h('span', { class: 'mono' }, r.ref), ' · ', r.site_name),
        h('span', null, r.urgent && h('span', { class: 'tag bad' }, t('urgent')), ' ', pill(r.status))),
      section(t('items'),
        h('div', { class: 'table-wrap' }, h('table', null,
          h('thead', null, h('tr', null, h('th', null, t('material')), h('th', null, t('spec')), h('th', null, t('qty')))),
          h('tbody', null, r.items.map((i) => h('tr', null, h('td', null, i.material), h('td', null, i.spec || '–'),
            h('td', { class: 'mono' }, i.qty ? `${num(i.qty)} ${i.unit}` : '–')))))),
        h('dl', { class: 'facts' },
          h('dt', null, t('requested_by')), h('dd', null, `${r.requester_name} · ${fmtWhen(r.created_at)}`),
          r.needed_by && [h('dt', null, t('needed_by')), h('dd', null, fmtDate(r.needed_by))],
          r.note && [h('dt', null, t('note')), h('dd', null, r.note)]),
        r.actions.length > 0 && h('div', { class: 'stack' },
          needsNote && note,
          h('div', { class: 'actions' }, r.actions.map((a) => h('button', {
            type: 'button', class: classes[a],
            onclick: () => act(() => api('POST', `/requests/${r.id}/action`, { action: a, note: note.value.trim() })),
          }, t('a_' + a)))))),
      section(t('history'), h('ul', { class: 'timeline' }, r.events.map((e) => h('li', { class: 'ev-' + e.action },
        h('strong', null, t('ev_' + e.action)), ` · ${e.name} · ${fmtWhen(e.at)}`, e.note && h('p', null, e.note))))),
    ];
  }

  async function newRequestView(siteId) {
    const sites = (await api('GET', '/sites')).filter((s) => s.active);
    if (!sites.length) return [h('h1', null, t('new_request')), section(null, empty(t('no_sites')))];
    const itemRow = () => {
      const row = h('div', { class: 'item-row' },
        h('input', { name: 'material', required: true, maxlength: 200, placeholder: t('material'), 'aria-label': t('material') }),
        h('input', { name: 'spec', maxlength: 200, placeholder: t('spec'), 'aria-label': t('spec') }),
        h('input', { name: 'qty', type: 'number', min: '0', step: 'any', placeholder: t('qty'), 'aria-label': t('qty') }),
        h('input', { name: 'unit', maxlength: 30, placeholder: t('unit'), 'aria-label': t('unit') }),
        h('button', { type: 'button', class: 'link small', onclick: () => { if (list.children.length > 1) row.remove(); } }, t('remove')));
      return row;
    };
    const list = h('div', { class: 'stack' }, itemRow());
    return [
      h('h1', null, t('new_request')),
      form(async (f) => {
        const items = [...list.children].map((row) => {
          const get = (n) => row.querySelector(`[name=${n}]`).value.trim();
          return { material: get('material'), spec: get('spec'), qty: Number(get('qty')) || null, unit: get('unit') };
        });
        try {
          const made = await api('POST', '/requests', {
            site_id: Number(val(f, 'site_id')), items, needed_by: val(f, 'needed_by') || null,
            urgent: f.elements.urgent.checked, note: val(f, 'note'),
          });
          f.removeAttribute('data-dirty');
          location.hash = '#/request/' + made.id;
        } catch (e) { if (e.code !== 'signed_out') toast(errText(e), true); }
      }, { class: 'card stack' },
      field(t('site'), siteSelect(sites, sites.some((s) => String(s.id) === siteId) ? siteId : sites[0].id)),
      h('h2', null, t('items')), list,
      h('button', { type: 'button', class: 'btn ghost', onclick: () => list.append(itemRow()) }, t('add_item')),
      field(t('needed_by'), h('input', { name: 'needed_by', type: 'date' })),
      h('label', { class: 'check' }, h('input', { type: 'checkbox', name: 'urgent' }), t('urgent')),
      field(t('note_optional'), h('textarea', { name: 'note', rows: 2, maxlength: 1000 })),
      h('button', { type: 'submit', class: 'btn wide' }, t('send_request'))),
    ];
  }

  async function sitesView() {
    const sites = await api('GET', '/sites');
    return [
      h('h1', null, t('sites_title')),
      isBoss() && h('details', { class: 'card' }, h('summary', null, t('add_site')),
        form(async (f) => {
          await act(() => api('POST', '/sites', { code: val(f, 'code'), name: val(f, 'name'), location: val(f, 'location') }), t('saved'));
        }, { class: 'inline-form' },
        h('input', { name: 'code', required: true, maxlength: 20, placeholder: t('code'), 'aria-label': t('code') }),
        h('input', { name: 'name', required: true, maxlength: 100, placeholder: t('name'), 'aria-label': t('name') }),
        h('input', { name: 'location', maxlength: 200, placeholder: t('location'), 'aria-label': t('location') }),
        h('button', { type: 'submit', class: 'btn' }, t('add')))),
      section(null, sites.length ? siteCards(sites) : empty(t('no_sites'))),
    ];
  }

  async function siteView(id) {
    const [s, users] = await Promise.all([api('GET', '/sites/' + id), isBoss() ? api('GET', '/users') : null]);
    const memberIds = new Set(s.members.map((m) => m.id));
    return [
      h('div', { class: 'page-head' },
        h('h1', null, s.name, ' ', !s.active && h('span', { class: 'tag' }, t('inactive'))),
        s.active && h('a', { href: '#/new-request/' + s.id, class: 'btn' }, t('request_materials'))),
      h('p', { class: 'muted' }, [s.code, s.location].filter(Boolean).join(' · ')),
      section(t('people'),
        users
          ? form(async (f) => {
            const ids = [...f.querySelectorAll('input[name=member]:checked')].map((c) => Number(c.value));
            await act(() => api('PATCH', '/sites/' + id, { member_ids: ids }), t('saved'));
          }, { class: 'stack' },
          h('div', { class: 'checks' }, users.filter((u) => u.active && u.role !== 'management').map((u) => h('label', { class: 'check' },
            h('input', { type: 'checkbox', name: 'member', value: u.id, checked: memberIds.has(u.id) }),
            `${u.name}${u.job_title ? ' · ' + u.job_title : ''}`))),
          h('div', { class: 'actions' }, h('button', { type: 'submit', class: 'btn' }, t('save_members')),
            h('button', { type: 'button', class: 'btn ghost', onclick: () => act(() => api('PATCH', '/sites/' + id, { active: !s.active })) },
              t(s.active ? 'close_site' : 'reopen_site'))))
          : (s.members.length ? h('ul', { class: 'plain' }, s.members.map((m) => h('li', null, m.name,
            m.job_title && h('span', { class: 'muted' }, ' · ' + m.job_title)))) : empty(t('no_members')))),
      section(t('site_tasks'),
        users && taskForm({ sites: [], site: s.id, assignees: users.filter((u) => u.active) }),
        taskList(s.tasks, s.today, { showAssignee: true })),
      section(t('site_requests'), requestList(s.requests)),
      section(t('site_logs'), s.logs.length ? logList(s.logs, true) : empty(t('nothing_here'))),
    ];
  }

  function logList(logs, withUser) {
    return h('ul', { class: 'logs' }, logs.map((l) => h('li', { class: 'log' }, h('p', null, l.text),
      h('div', { class: 'meta' }, withUser && h('strong', null, l.user_name), h('span', null, fmtDate(l.day)),
        h('span', null, fmtTime(l.created_at)), l.site_name && h('span', null, l.site_name)))));
  }

  async function overviewView() {
    const d = await api('GET', '/overview');
    const s = d.stats;
    const tile = (label, value, cls, href) => h(href ? 'a' : 'div', { class: 'tile ' + (cls || ''), href },
      h('span', { class: 'tile-num' }, String(value)), h('span', null, label));
    return [
      h('div', { class: 'page-head' }, h('h1', null, t('overview_title')), h('span', { class: 'muted' }, fmtDate(d.today))),
      h('div', { class: 'tiles' },
        tile(t('s_open'), s.open_tasks), tile(t('s_overdue'), s.overdue, s.overdue ? 'bad' : ''),
        tile(t('s_logged'), `${s.logged_today}/${s.people}`, '', '#/logs'),
        tile(t('s_pending'), s.pending, s.pending ? 'warn' : '', '#/requests/pending'),
        tile(t('s_approved'), s.approved, '', '#/requests/approved'), tile(t('s_ordered'), s.ordered, '', '#/requests/ordered')),
      section(t('approvals'), d.approvals.length ? h('ul', { class: 'rows' }, d.approvals.map((r) => h('li', { class: 'row' },
        h('span', { class: 'mono' }, r.ref),
        h('span', { class: 'row-main' }, h('strong', null, r.site_name, ' ', r.urgent && h('span', { class: 'tag bad' }, t('urgent'))),
          h('span', { class: 'muted' }, itemsSummary(r)),
          h('span', { class: 'muted small' }, `${r.requester_name} · ${fmtWhen(r.created_at)}`)),
        h('span', { class: 'row-end' },
          h('button', { type: 'button', class: 'btn small', onclick: () => act(() => api('POST', `/requests/${r.id}/action`, { action: 'approve' })) }, t('a_approve')),
          h('a', { href: '#/request/' + r.id, class: 'btn ghost small' }, t('review')))))) : empty(t('no_approvals'))),
      section(t('tracker'), h('div', { class: 'table-wrap' }, h('table', { class: 'tracker' },
        h('thead', null, h('tr', null, [t('employee'), t('c_open'), t('c_overdue'), t('c_done'), t('c_log'), t('c_requests')].map((x) => h('th', null, x)))),
        h('tbody', null, d.people.map((p) => h('tr', null,
          h('td', null, h('a', { href: '#/user/' + p.id }, p.name), h('span', { class: 'muted small block' }, p.job_title || t('role_' + p.role))),
          h('td', { class: 'mono' }, p.open_tasks),
          h('td', { class: 'mono' + (p.overdue ? ' bad-text' : '') }, p.overdue),
          h('td', { class: 'mono' }, p.done_week),
          h('td', null, p.logs_today ? h('span', { class: 'tag good' }, t('yes'))
            : h('span', { class: 'tag warn' }, t('not_yet'), p.last_log_day ? ` · ${t('last_log', fmtDate(p.last_log_day))}` : '')),
          h('td', { class: 'mono' }, p.open_requests))))))),
      section(t('activity'), d.feed.length ? h('ul', { class: 'feed' }, d.feed.map((f) => h('li', null,
        h('a', { href: f.link || '#/overview' }, fill(f.kind === 'task_assigned' ? 'feed_task_assigned' : 'act_' + f.kind, f.data)),
        h('span', { class: 'muted small' }, fmtWhen(f.at))))) : empty(t('no_activity'))),
    ];
  }

  async function userView(id) {
    const d = await api('GET', `/users/${id}/tracker`);
    const open = d.tasks.filter((x) => x.status === 'open');
    const done = d.tasks.filter((x) => x.status === 'done');
    const byDay = {};
    d.logs.forEach((l) => { (byDay[l.day] ||= []).push(l); });
    return [
      h('a', { href: '#/overview', class: 'link' }, t('back_overview')),
      h('div', { class: 'page-head' }, h('h1', null, d.user.name),
        h('span', { class: 'muted' }, [d.user.job_title, t('role_' + d.user.role), ...d.sites.map((s) => s.name)].filter(Boolean).join(' · '))),
      section(t('assign_task'), taskForm({ sites: d.sites, assignee: d.user.id })),
      section(`${t('open_tasks')} (${open.length})`, taskList(open, d.today)),
      section(t('logs_recent'), d.logs.length ? Object.entries(byDay).map(([day, logs]) => [h('h3', null, fmtDate(day)), logList(logs)])
        : empty(t('nothing_here'))),
      section(`${t('done_recent')} (${done.length})`, done.length ? taskList(done, d.today) : empty(t('nothing_here'))),
      section(t('their_requests'), requestList(d.requests)),
    ];
  }

  async function teamView() {
    const [users, sites] = await Promise.all([api('GET', '/users'), api('GET', '/sites')]);
    const roleSelect = (value) => h('select', { name: 'role', value }, ['employee', 'procurement', 'management'].map((r) => h('option', { value: r }, t('role_' + r))));
    const siteChecks = (chosen) => h('div', { class: 'checks' }, sites.filter((s) => s.active).map((s) => h('label', { class: 'check' },
      h('input', { type: 'checkbox', name: 'site', value: s.id, checked: chosen.includes(s.id) }), s.name)));
    const picked = (f) => [...f.querySelectorAll('input[name=site]:checked')].map((c) => Number(c.value));
    return [
      h('h1', null, t('team_title')),
      h('details', { class: 'card' }, h('summary', null, t('add_user')),
        form(async (f) => {
          await act(() => api('POST', '/users', {
            username: val(f, 'username').toLowerCase(), name: val(f, 'name'), job_title: val(f, 'job_title'),
            role: val(f, 'role'), password: f.elements.password.value, site_ids: picked(f),
          }), t('user_created'));
        }, { class: 'stack' },
        field(t('full_name'), h('input', { name: 'name', required: true, maxlength: 100 })),
        field(`${t('username')} (${t('username_hint')})`, h('input', { name: 'username', required: true, pattern: '[a-z0-9._\\-]{3,32}', autocapitalize: 'none', autocomplete: 'off' })),
        field(t('job_title'), h('input', { name: 'job_title', maxlength: 100 })),
        field(t('role'), roleSelect('employee')),
        field(t('temp_password'), h('input', { name: 'password', required: true, minlength: 8, autocomplete: 'off' })),
        h('span', { class: 'label' }, t('sites_access')), siteChecks([]),
        h('button', { type: 'submit', class: 'btn' }, t('create_user')))),
      section(null, h('ul', { class: 'rows' }, users.map((u) => h('li', null, h('details', null,
        h('summary', { class: 'row' },
          h('span', { class: 'row-main' }, h('strong', null, u.name), h('span', { class: 'muted small' }, `@${u.username}${u.job_title ? ' · ' + u.job_title : ''}`)),
          h('span', { class: 'row-end' }, h('span', { class: 'tag' }, t('role_' + u.role)), !u.active && h('span', { class: 'tag bad' }, t('disabled')))),
        form(async (f) => {
          const body = { name: val(f, 'name'), job_title: val(f, 'job_title'), role: val(f, 'role'), active: f.elements.active.checked, site_ids: picked(f) };
          if (f.elements.password.value) body.password = f.elements.password.value;
          await act(() => api('PATCH', '/users/' + u.id, body), t('saved'));
        }, { class: 'stack edit' },
        field(t('full_name'), h('input', { name: 'name', required: true, maxlength: 100, value: u.name })),
        field(t('job_title'), h('input', { name: 'job_title', maxlength: 100, value: u.job_title })),
        field(t('role'), roleSelect(u.role)),
        h('span', { class: 'label' }, t('sites_access')), siteChecks(u.site_ids),
        h('label', { class: 'check' }, h('input', { type: 'checkbox', name: 'active', checked: !!u.active }), t('active')),
        field(t('new_temp_password'), h('input', { name: 'password', minlength: 8, autocomplete: 'off' })),
        h('div', { class: 'actions' }, h('button', { type: 'submit', class: 'btn' }, t('save')),
          h('a', { href: '#/user/' + u.id, class: 'btn ghost' }, t('tracker'))))))))),
    ];
  }

  async function logsView(day) {
    if (!isBoss()) {
      const d = await api('GET', '/logs');
      return [h('h1', null, t('logs_title')), section(null, d.entries.length ? logList(d.entries) : empty(t('nothing_here')))];
    }
    const d = await api('GET', '/logs' + (/^\d{4}-\d\d-\d\d$/.test(day || '') ? '?day=' + day : ''));
    const byUser = {};
    d.entries.forEach((l) => { (byUser[l.user_name] ||= []).push(l); });
    return [
      h('div', { class: 'page-head' }, h('h1', null, t('logs_title')),
        field(t('day'), h('input', { type: 'date', value: d.day, onchange: (ev) => { if (ev.target.value) location.hash = '#/logs/' + ev.target.value; } }))),
      section(t('missing_logs'), d.missing.length ? h('ul', { class: 'chips' }, d.missing.map((m) => h('li', null,
        h('a', { href: '#/user/' + m.id }, m.name)))) : empty(t('everyone_logged'))),
      d.entries.length ? Object.entries(byUser).map(([name, logs]) => section(name, logList(logs))) : section(null, empty(t('no_logs_day'))),
    ];
  }

  async function alertsView() {
    const list = await api('GET', '/notifications');
    if (state.unread) { await api('POST', '/notifications/read'); state.unread = 0; }
    return [
      h('h1', null, t('alerts_title')),
      section(null, list.length ? h('ul', { class: 'feed' }, list.map((n) => h('li', { class: n.read ? '' : 'unread' },
        h('a', { href: n.link || '#/home' }, fill('act_' + n.kind, n.data)), h('span', { class: 'muted small' }, fmtWhen(n.at)))))
        : empty(t('no_alerts'))),
    ];
  }

  const ROUTES = {
    overview: { view: overviewView, nav: 'nav_overview', boss: true },
    home: { view: homeView, nav: 'nav_home' },
    sites: { view: sitesView, nav: 'nav_sites' },
    requests: { view: requestsView, nav: 'nav_requests' },
    team: { view: teamView, nav: 'nav_team', boss: true },
    logs: { view: logsView, nav: 'nav_logs', boss: true },
    site: { view: siteView, parent: 'sites' },
    request: { view: requestView, parent: 'requests' },
    'new-request': { view: newRequestView, parent: 'requests' },
    user: { view: userView, parent: 'overview', boss: true },
    alerts: { view: alertsView },
    password: { view: async () => [h('h1', null, t('change_password')), passwordForm()] },
  };

  // ------------------------------------------------------------------ shell
  function shell(route, body) {
    const active = ROUTES[route].parent || route;
    return [
      h('header', { class: 'top' },
        h('div', { class: 'top-row' },
          h('a', { href: '#/', class: 'brand' }, t('brand')),
          h('div', { class: 'top-tools' },
            h('a', { href: '#/alerts', class: 'bell' + (state.unread ? ' has' : ''), id: 'bell' }, t('nav_alerts'), state.unread ? ` (${state.unread})` : ''),
            h('button', { type: 'button', class: 'link', onclick: switchLang }, t('lang_switch')),
            h('a', { href: '#/password', class: 'link who' }, state.me.name),
            h('button', { type: 'button', class: 'link', onclick: async () => { await api('POST', '/logout').catch(() => {}); state.me = null; render(); } }, t('sign_out')))),
        h('nav', { class: 'main-nav', 'aria-label': t('brand') }, Object.entries(ROUTES)
          .filter(([, r]) => r.nav && (!r.boss || isBoss()))
          .map(([name, r]) => h('a', { href: '#/' + name, class: name === active ? 'on' : '', 'aria-current': name === active ? 'page' : null }, t(r.nav))))),
      h('main', { class: 'page' }, body),
    ];
  }

  function switchLang() {
    lang = lang === 'ar' ? 'en' : 'ar';
    store.set('lang', lang);
    render();
  }

  let renderId = 0;
  async function render(keepScroll) {
    const mine = ++renderId;
    const app = document.getElementById('app');
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    document.title = t('brand');
    state.stale = false;
    if (!state.me) return app.replaceChildren(loginView());
    if (state.me.must_change_password) {
      return app.replaceChildren(h('main', { class: 'auth' }, h('h1', null, t('must_change')), passwordForm()));
    }
    const [name, arg] = location.hash.replace(/^#\/?/, '').split('/');
    let route = ROUTES[name] ? name : (isBoss() ? 'overview' : 'home');
    if (ROUTES[route].boss && !isBoss()) route = 'home';
    const sameRoute = state.route === location.hash;
    const scroll = window.scrollY;
    let body;
    try {
      body = await ROUTES[route].view(arg);
    } catch (e) {
      if (e.code === 'signed_out') return;
      body = h('div', { class: 'card bad-text' }, errText(e));
    }
    if (mine !== renderId) return;
    app.replaceChildren(...shell(route, body));
    state.route = location.hash;
    window.scrollTo(0, keepScroll || sameRoute ? scroll : 0);
    pulse(true);
  }

  // Someone typing should never lose their text to a background refresh.
  const busy = () => document.querySelector('form[data-dirty]')
    || (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName) && document.activeElement.type !== 'checkbox');

  async function pulse(silent) {
    if (!state.me || state.me.must_change_password || document.hidden) return;
    let p;
    try { p = await api('GET', '/pulse'); } catch { return; }
    const changed = state.rev !== null && p.rev !== state.rev;
    state.rev = p.rev;
    if (p.unread !== state.unread) {
      state.unread = p.unread;
      const bell = document.getElementById('bell');
      if (bell) { bell.textContent = t('nav_alerts') + (p.unread ? ` (${p.unread})` : ''); bell.className = 'bell' + (p.unread ? ' has' : ''); }
    }
    if (silent) return;
    if (changed || state.stale) {
      if (busy()) state.stale = true; else render(true);
    }
  }

  document.addEventListener('input', (ev) => { ev.target.closest?.('form')?.setAttribute('data-dirty', '1'); });
  window.addEventListener('hashchange', () => render());
  document.addEventListener('visibilitychange', () => pulse());
  setInterval(() => pulse(), 4000);

  (async () => {
    try { state.me = await api('GET', '/me'); } catch { /* not signed in: render shows the sign-in form */ }
    render();
  })();
})();
