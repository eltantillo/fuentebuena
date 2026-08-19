19.0.1.0.0 ( Date : 30 July 2025 )
----------------------------------

Initial Release

19.0.2.0.0 ( Date : 28 September 2025 )
---------------------------------------

[Add] Hide Menu multi company supported feature and add company id in most js side filters.

( Date : 30 September 2025 )
----------------------------

[Add] Hide Spreadsheet Model wise and Global multi company supported feature. 

19.0.3.0.0 ( Date : 08 October 2025 )
-------------------------------------

[Add] Feature for hide Quick Create, Create and edit field level and Global both.

19.0.3.0.1 ( Date : 20 November 2025 ) [TICKET/31588]
--------------------------------------

[Fix] Expert Multi action issue this.onExportData is not a function.

19.0.3.0.2 ( Date : 02 December 2025 ) [TICKET/31588]
--------------------------------------

[Remove] Warnings from module.

19.0.4.0.0 ( Date : 03 December 2025 )
--------------------------------------

[Add] Feature to Global restrict access of chatter and its features like Hide Search Message Icon, Hide Attachment Icon, Hide Followers Icon and Hide Follow/Unfollow Button.
[Add] Feature to Global restrict access of Action and its features like Hide New, Hide Delete, Hide Duplicate, Hide Archive, Hide Unarchive.

19.0.4.0.1 ( Date : 09 December 2025 )
--------------------------------------

[Fix] Issue of Some portions are hidden in view.

19.0.4.0.2 ( Date : 09 December 2025 ) [TICKET/31928]
--------------------------------------

[Fix] Issue of Cannot find the definition of component "SuggestedRecipientsList".

19.0.5.0.0 ( Date : 17 December 2025 )
--------------------------------------

[Add] Feature for Expiration Record.

19.0.6.0.0 ( Date : 29 December 2025 )
--------------------------------------

[Add] New Feature for Restriction By Groups, Restriction Type Groups and Users Optional now.

19.0.6.0.1 ( Date : 06 January 2026 ) [TICKET/32490]
-------------------------------------

[Fix] Issue of Buttons and Notbook tabs not hidden.

19.0.6.0.2 ( Date : 10 January 2026 ) [TICKET/32490]
-------------------------------------

[Fix] Button hide on multiple refresh issue.

19.0.6.0.3 ( Date : 12 January 2026 ) [TICKET/32490]
-------------------------------------

[Fix] View hide on multiple refresh issue.

19.0.7.0.0 ( Date : 20 January 2026 )
-------------------------------------

[Add] New Feature model-wise and global control over Odoo's search panel visibility, including filter and group-by options model-wise.

19.0.7.0.1 ( Date : 27 January 2026 )
-------------------------------------

[Fix] Default Filter Not hidden Bug.
[Fix] Some Smart buttons not Display in Selection list Bug.

19.0.7.0.2 ( Date : 28 January 2026 )
-------------------------------------

[Update] Smart Hide Button name (Add Smart button).

19.0.7.0.3 ( Date : 02 February 2026 )
-------------------------------------

[Update] Global Hide Group By name (Add By).

19.0.7.0.4 ( Date : 05 February 2026 )
-------------------------------------

[Fix] Group wise restriction issues resolved (AI).

19.0.7.0.5 ( Date : 11 February 2026 )
-------------------------------------

[Fix] **Critical Module Shadowing Bug**:
- **Bug**: Global ``AttributeError: 'NoneType' object has no attribute 'Date'`` occurred due to ``fields`` module shadowing when calling ``fields.Date.today()``.
- **Fix**: Refactored imports across all models to use explicit ``from odoo.fields import Date`` and unified ``Date.today()`` calls.

[Fix] **Expiry Date Logic Failure**:
- **Bug**: Expiry dates were ignored in backend security checks (Read-Only mode), Report hiding, and XML button hiding.
- **Fix**: Integrated real-time ``sh_expiry_date`` validation across the entire security architecture.

[Fix] **JavaScript View Loading Crash**:
- **Bug**: ``TypeError: Cannot read properties of undefined (reading 'arch')`` when refreshing a page with restricted views.
- **Fix**: Changed view restriction strategy to keep view keys in results but set root nodes to ``invisible="1"``.

[Fix] **UI Cache Synchronization Issue**:
- **Bug**: Changes to access rules required multiple refreshes or manual server restarts to reflect in the UI.
- **Fix**: Implemented automatic ``registry.clear_cache()`` on all rule modifications (create/write/unlink).

[Fix] **Global View Restriction Leak**:
- **Bug**: Hiding a view for one model (e.g., Sale Order) was incorrectly hiding it for other models globally.
- **Fix**: Scoped view hiding logic to be strictly per-model.

[Fix] **Action Mode Redirection**:
- **Bug**: Restricted 'List' views remained in the breadcrumbs and attempted to load on refresh, causing errors.
- **Fix**: Synchronized ``ir.actions.act_window`` to strip restricted modes and redirect users to the next available valid view.

[Add] **Field Access Dependency Logic**:
- **Feature**: Added ``onchange`` rules to ensure logical consistency: Required fields cannot be Readonly/Invisible, and Invisible fields cannot be Required.

19.0.7.0.6 ( Date : 14 February 2026 )
-------------------------------------

[Fix] **Report/Action Bindings Cache Not Scoped Per User & Company**:
- **Bug**: The ``_get_bindings`` ormcache key only included ``model_name`` and ``self.env.lang``, causing cached report/action bindings from one user or company to be incorrectly served to another.
- **Fix**: Added ``self.env.uid`` and ``self.env.company.id`` to the ormcache key for proper per-user, per-company scoping.

[Fix] **Chatter Restrictions Not Passing Company ID**:
- **Bug**: ``chatter_container.js`` did not pass ``company_id`` to the backend ``sh_checkhide_chatter`` method, unlike all other JS files. This could cause incorrect chatter restrictions in edge cases.
- **Fix**: Added ``company_id: user.activeCompany.id`` to the JS call and updated the server-side method to use the passed ``company_id`` with fallback to ``self.env.company.id``.

[Fix] **Inconsistent Company ID Source in Filter/GroupBy JS**:
- **Bug**: ``hide_filters_groupby.js`` used ``this.env.company?.id || user.companyId`` which could be undefined in certain component contexts, causing wrong company filtering.
- **Fix**: Replaced with ``user.activeCompany.id`` to match the consistent pattern used across all other JS files.

[Fix] **Many2X Create/Edit Restrictions Ignoring Company**:
- **Bug**: ``sh_hide_create_and_edit.js`` sent ``company_ids`` (plural) via cookie parsing, but the server-side ``get_access_restrictions`` reads ``company_id`` (singular), so the explicit company value was silently ignored.
- **Fix**: Changed to send ``company_id: user.activeCompany.id`` directly and removed the unused ``getCompanyIdsFromCookie()`` function.

19.0.7.0.7 ( Date : 18 February 2026 )
-------------------------------------

[Fix]  Export functionality resolved bug.
[Fix] **Global View Restriction Cache Not Scoped Per User & Company**:
- **Bug**: The ``_get_hidden_views`` ormcache key only included ``model_name`` and ``self.env.lang``, causing cached view restrictions from one user or company to be incorrectly served to another.
- **Fix**: Added ``self.env.uid`` and ``self.env.company.id`` to the ormcache key for proper per-user, per-company scoping.

19.0.8.0.0 ( Date : 17 March 2026 )
-------------------------------------

[ADD] - Added new feature for hide favorites model wise and Global both.

19.0.8.0.1 ( Date : 19 March 2026 )
-----------------------------------

[Fix] Fix global rule bypass

19.0.8.0.2 ( Date : 24 March 2026 )
-----------------------------------

[Fix] Resolved an issue where the Unit of Measure (UoM) field would vanish from Sales Order lines when "External Links" hide configuration was active.

19.0.9.0.0 ( Date : 26 March 2026 )
-----------------------------------

[Add] Timezone-Aware Time-Based Access Restrictions.

19.0.9.0.1 ( Date : 30 March 2026 )
-----------------------------------

[Fix] TypeError ``AccessManager._sh_is_within_time_window() missing 1 required positional argument: 'rule'``.

19.0.10.0.0 ( Date : 07 April 2026 )
-----------------------------------

[Add] Enhanced Conditional Domain restrictions for record-level CRUD and UI elements (Filters, Group By, Search Panel).

19.0.10.0.1 ( Date : 19 May 2026 ) [TICKET/35506]
----------------------------------

[Fix] Fixed attachment upload crash (TypeError: Cannot read properties of undefined (reading 'localId')).

19.0.11.0.0 ( Date : 28 April 2026 )
-----------------------------------

[Add] Added XMLRPC feature to restrict XML-RPC / Script Access.
[Add] Added feature to hide import and restrict edit in model-wise access.

19.0.12.0.0 ( Date : 19 May 2026 )
----------------------------------

[Add] Access Management Dashboard
