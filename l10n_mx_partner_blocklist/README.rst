Partner Blocklist for Mexican Localization
------------------------------------------

This module provides a method to download, process and save in Odoo the list of partners blocked by the SAT due to
illegal operations with CFDIs, so that it can be consulted when necessary and to avoid selling or buying to blocked partners.

Configuration
-------------

1. Go to http://omawww.sat.gob.mx/cifras_sat/Paginas/DatosAbiertos/contribuyentes_publicados.html where you can found
   the block list published by the SAT.

2. Copy the **Definitivos** URL and assign it to the value of **l10n_mx_partner_blocklist_url** System Parameter.

   .. image:: /l10n_mx_partner_blocklist/static/src/sat.png
      :width: 700pt

   .. image:: /l10n_mx_partner_blocklist/static/src/system_parameter.png
      :width: 700pt

3. You can go to **Contacts/Partner Blacklist** to verify if the block list has been downloaded. If the SAT list has not been downloaded,
   you can manually execute the scheduled action **Partner Blacklist Process**, which is responsible for consulting and updating the
   list automatically every day to keep up to date with the information published by the SAT.

   .. image:: /l10n_mx_partner_blocklist/static/src/blacklist_model.png
      :width: 800pt

   .. image:: /l10n_mx_partner_blocklist/static/src/run_action.png
      :width: 600pt

Usage
-----

1. To update the **Partner SAT State** go to the partner and in Action menú click on **Partner Blocklist Status** option.
   You can update the state of multiple partners by calling that action from list view.

   .. image:: /l10n_mx_partner_blocklist/static/src/update_partner_state.png
      :width: 600pt

   .. image:: /l10n_mx_partner_blocklist/static/src/update_partner_state_list_view.png
      :width: 700pt

   The **Partner SAT Status** for each partner will be indicated with the color grey, green or red.

      .. image:: /l10n_mx_partner_blocklist/static/src/partner_blocklist_partner_state.png
         :width: 700pt

   - **Grey:** for partners whose status has not been consulted or the partner VAT is not set.
   - **Green:** for partners that was not found in block list.
   - **Red:** for partners blocked by the SAT, therefore it is recommended not to carry out commercial operations with them.

2. When updating a partner's VAT, the system checks if the partner is blocked. If it is, a warning message is displayed,
   but the update can still proceed.

   .. image:: /l10n_mx_partner_blocklist/static/src/partner_blocklist_vat_warning.png
      :width: 700pt

3. When trying to confirm an invoice, the partner will be verified to see if it is blocked in order to alert the user.

   .. image:: /l10n_mx_partner_blocklist/static/src/partner_blocklist_validation.png
      :width: 700pt

4. If the user wants to perform operations with the partner even though it is blocked, it is neccesary to add the
   **Partner Blacklist Admin** permission to the user to be able to remove the partner record from the block list by going to
   **Contacts/Partner Blacklist**, select the partner and remove it from Actions menu.
   After the blocked partner is removed from the list you will be able to confirm the invoice.

   .. image:: /l10n_mx_partner_blocklist/static/src/admin_permission.png
      :width: 700pt

   .. image:: /l10n_mx_partner_blocklist/static/src/remove_blocked_partner.png
      :width: 700pt

Credits
-------

**Contributors**

* Luis Torres <luis_t@vauxoo.com> (Reviewer)
* Germana Oliveira <germana@vauxoo.com> (Developer)

Maintainer
----------

This module is maintained by Vauxoo.

A Latin American company that provides training, coaching, development and implementation of enterprise management
systems and bases its entire operation strategy in the use of Open Source Software and its main product is Odoo.

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
    :alt: Vauxoo
    :width: 600px
